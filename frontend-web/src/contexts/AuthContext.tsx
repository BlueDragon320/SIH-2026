import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AuthUser, LoginResponse } from '../types/admin';
import { authApi } from '../services/authApi';
import { useChatStore } from '../store/useChatStore';

interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<LoginResponse>;
  logout: () => void;
  refreshAuth: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const checkAuth = async () => {
    try {
      const u = await authApi.getMe();
      setUser(u);
      if (u) {
        useChatStore.getState().initUserSessions(u);
      }
    } catch (err) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const login = async (username: string, password: string) => {
    const data = await authApi.login(username, password);
    setUser(data.user);
    if (data.user) {
      await useChatStore.getState().initUserSessions(data.user);
    }
    return data;
  };

  const logout = () => {
    authApi.logout();
    setUser(null);
    useChatStore.getState().clearUserSessions();
  };

  const refreshAuth = async () => {
    const rf = localStorage.getItem('wb_refresh_token');
    if (rf) {
      await authApi.refreshToken(rf);
      await checkAuth();
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isAdmin: user?.role === 'admin',
      isLoading,
      login,
      logout,
      refreshAuth,
      checkAuth
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
