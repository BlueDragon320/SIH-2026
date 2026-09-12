import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Diamond, Loader2 } from 'lucide-react';
import { authApi } from '../../services/authApi';

export function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [needsPasswordChange, setNeedsPasswordChange] = useState(false);
  
  const { login, checkAuth, isAuthenticated, user, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && isAuthenticated && user) {
      if (user.role === 'admin') {
        navigate('/admin', { replace: true });
      } else {
        navigate('/', { replace: true });
      }
    }
  }, [isAuthenticated, user, isLoading, navigate]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await login(username, password);
      if (data.user.must_change_password) {
        setNeedsPasswordChange(true);
      } else if (data.user.role === 'admin') {
        navigate('/admin', { replace: true });
      } else {
        navigate('/', { replace: true });
      }
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authApi.changePassword(password, newPassword);
      await checkAuth();
      const me = await authApi.getMe();
      if (me.role === 'admin') {
        navigate('/admin', { replace: true });
      } else {
        navigate('/', { replace: true });
      }
    } catch (err: any) {
      setError(err.message || 'Password change failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4 bg-gradient-to-br from-background to-surface-hover">
      <div className="w-full max-w-md bg-surface/50 backdrop-blur-xl border border-border rounded-2xl shadow-2xl p-8">
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 bg-crimson-600/10 rounded-xl border border-crimson-600/20 mb-4">
            <Diamond className="w-8 h-8 text-crimson-500" />
          </div>
          <h1 className="text-2xl font-bold text-text-primary">Workbench</h1>
          <p className="text-text-muted mt-2">Sign in to your account</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-sm">
            {error}
          </div>
        )}

        {!needsPasswordChange ? (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Username</label>
              <input
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                className="w-full bg-surface border border-border rounded-xl px-4 py-2.5 text-text-primary focus:outline-none focus:border-crimson-500 focus:ring-1 focus:ring-crimson-500 transition-colors"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full bg-surface border border-border rounded-xl px-4 py-2.5 text-text-primary focus:outline-none focus:border-crimson-500 focus:ring-1 focus:ring-crimson-500 transition-colors"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-crimson-600 hover:bg-crimson-500 text-white rounded-xl px-4 py-2.5 font-medium flex items-center justify-center transition-colors disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Sign In'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">New Password</label>
              <input
                type="password"
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                className="w-full bg-surface border border-border rounded-xl px-4 py-2.5 text-text-primary focus:outline-none focus:border-crimson-500 focus:ring-1 focus:ring-crimson-500 transition-colors"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-crimson-600 hover:bg-crimson-500 text-white rounded-xl px-4 py-2.5 font-medium flex items-center justify-center transition-colors disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Update Password'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
