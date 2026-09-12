import { DashboardStats, AuthUser, AdminSession, LoginRecord, UsageStatsUser, UserChat } from '../types/admin';

const API_BASE = '/api/v1/admin';

async function authFetch(url: string, options: RequestInit = {}) {
  let token = localStorage.getItem('wb_access_token');
  const headers = new Headers(options.headers || {});
  if (token) headers.set('Authorization', `Bearer ${token}`);
  
  let res = await fetch(url, { ...options, headers });
  
  if (res.status === 401) {
    const refreshToken = localStorage.getItem('wb_refresh_token');
    if (refreshToken) {
      try {
        const refreshRes = await fetch('/api/v1/auth/refresh', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken })
        });
        if (refreshRes.ok) {
          const refreshData = await refreshRes.json();
          token = refreshData.access_token;
          localStorage.setItem('wb_access_token', token as string);
          headers.set('Authorization', `Bearer ${token}`);
          res = await fetch(url, { ...options, headers });
        }
      } catch (err) {
        console.error('Refresh token failed', err);
      }
    }
  }
  
  if (!res.ok) {
    throw new Error(`API Error: ${res.status}`);
  }
  return res;
}

export const adminApi = {
  getDashboardStats: async (): Promise<DashboardStats> => {
    const res = await authFetch(`${API_BASE}/dashboard`);
    return res.json();
  },
  getUsers: async (): Promise<AuthUser[]> => {
    const res = await authFetch(`${API_BASE}/users`);
    return res.json();
  },
  createUser: async (data: any): Promise<AuthUser> => {
    const res = await authFetch(`${API_BASE}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },
  updateUser: async (userId: string, data: any): Promise<AuthUser> => {
    const res = await authFetch(`${API_BASE}/users/${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },
  deleteUser: async (userId: string): Promise<void> => {
    await authFetch(`${API_BASE}/users/${userId}`, { method: 'DELETE' });
  },
  getActiveSessions: async (): Promise<AdminSession[]> => {
    const res = await authFetch(`${API_BASE}/sessions`);
    return res.json();
  },
  forceEndSession: async (sessionId: string): Promise<void> => {
    await authFetch(`${API_BASE}/sessions/${sessionId}`, { method: 'DELETE' });
  },
  getLoginHistory: async (limit = 100, userId?: string): Promise<LoginRecord[]> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (userId) params.append('user_id', userId);
    const res = await authFetch(`${API_BASE}/login-history?${params}`);
    return res.json();
  },
  getUsageStats: async (): Promise<UsageStatsUser[]> => {
    const res = await authFetch(`${API_BASE}/usage-stats`);
    return res.json();
  },
  getAllUserChats: async (): Promise<UserChat[]> => {
    const res = await authFetch(`${API_BASE}/user-chats`);
    return res.json();
  },
  getUserChats: async (userId?: string): Promise<UserChat[]> => {
    if (!userId || userId === 'all') {
      const res = await authFetch(`${API_BASE}/user-chats`);
      return res.json();
    }
    const res = await authFetch(`${API_BASE}/user-chats/${userId}`);
    return res.json();
  },
  deleteUserChat: async (sessionId: string): Promise<void> => {
    await authFetch(`${API_BASE}/user-chats/${sessionId}`, { method: 'DELETE' });
  },
  getSystemHealth: async (): Promise<any> => {
    const res = await authFetch(`${API_BASE}/system-health`);
    return res.json();
  },
  getAuditLogs: async (limit = 100): Promise<any[]> => {
    const res = await authFetch(`/api/v1/audit/logs?limit=${limit}`);
    return res.json();
  }
};
