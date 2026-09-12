import React, { useEffect, useState } from 'react';
import { adminApi } from '../../services/adminApi';
import { AdminSession } from '../../types/admin';
import { XCircle, RefreshCw, Clock, Wifi } from 'lucide-react';

export function ActiveSessions() {
  const [sessions, setSessions] = useState<AdminSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [now, setNow] = useState(Date.now());

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const data = await adminApi.getActiveSessions();
      setSessions(data);
    } catch (e) {
      console.error('Failed to load sessions', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
    const fetchInt = setInterval(fetchSessions, 15000);
    const tickInt = setInterval(() => setNow(Date.now()), 1000);
    return () => {
      clearInterval(fetchInt);
      clearInterval(tickInt);
    };
  }, []);

  const endSession = async (id: string) => {
    if (!confirm('Terminate this user session? They will be logged out.')) return;
    try {
      await adminApi.forceEndSession(id);
      fetchSessions();
    } catch (e) {
      console.error('Failed to end session', e);
    }
  };

  const formatDuration = (loginAt: string) => {
    const diffMs = Math.max(0, now - new Date(loginAt).getTime());
    const secs = Math.floor(diffMs / 1000);
    const mins = Math.floor(secs / 60);
    const hrs = Math.floor(mins / 60);
    if (hrs > 0) return `${hrs}h ${mins % 60}m`;
    if (mins > 0) return `${mins}m ${secs % 60}s`;
    return `${secs}s`;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-text-primary">Active Sessions ({sessions.length})</h2>
          <p className="text-text-secondary text-sm">Currently authenticated users with live session duration</p>
        </div>
        <button
          onClick={fetchSessions}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 bg-surface hover:bg-surface-hover border border-border text-text-primary rounded-lg text-sm transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-crimson-500' : ''}`} />
          Refresh
        </button>
      </div>

      <div className="bg-surface border border-border rounded-xl overflow-hidden shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-surface-hover/80 text-text-secondary border-b border-border text-xs uppercase tracking-wider font-semibold">
            <tr>
              <th className="px-6 py-3.5">User</th>
              <th className="px-6 py-3.5">IP Address</th>
              <th className="px-6 py-3.5">Login Time</th>
              <th className="px-6 py-3.5">Last Active</th>
              <th className="px-6 py-3.5">Duration</th>
              <th className="px-6 py-3.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border text-sm">
            {sessions.map(s => (
              <tr key={s.session_id} className="hover:bg-surface-hover/40 transition-colors">
                <td className="px-6 py-4 font-medium text-text-primary">
                  {s.username || s.user_id || 'Unknown'}
                </td>
                <td className="px-6 py-4 text-text-secondary font-mono text-xs">
                  <span className="inline-flex items-center gap-1">
                    <Wifi className="w-3 h-3 text-emerald-400" />
                    {s.ip_address === 'testclient' ? 'Test' : (s.ip_address || 'Local')}
                  </span>
                </td>
                <td className="px-6 py-4 text-text-secondary text-xs">
                  {new Date(s.login_at).toLocaleString()}
                </td>
                <td className="px-6 py-4 text-text-secondary text-xs">
                  {s.last_active ? new Date(s.last_active).toLocaleTimeString() : '—'}
                </td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center gap-1 text-emerald-400 font-medium text-xs">
                    <Clock className="w-3 h-3" />
                    {formatDuration(s.login_at)}
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <button
                    onClick={() => endSession(s.session_id)}
                    className="text-rose-400 hover:text-rose-300 flex items-center gap-1 text-xs bg-rose-400/10 hover:bg-rose-400/20 px-2.5 py-1.5 rounded-md transition-colors ml-auto"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    Terminate
                  </button>
                </td>
              </tr>
            ))}
            {sessions.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-text-muted">
                  <Clock className="w-8 h-8 mx-auto text-text-muted/40 mb-2" />
                  <p>No active sessions at this time.</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
