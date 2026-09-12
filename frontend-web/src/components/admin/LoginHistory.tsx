import React, { useEffect, useState } from 'react';
import { adminApi } from '../../services/adminApi';
import { LoginRecord } from '../../types/admin';
import { RefreshCw, History } from 'lucide-react';

export function LoginHistory() {
  const [history, setHistory] = useState<LoginRecord[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await adminApi.getLoginHistory(200);
      setHistory(data);
    } catch (e) {
      console.error('Failed to load login history', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const formatDuration = (seconds: number | null) => {
    if (seconds == null) return null;
    const mins = Math.floor(seconds / 60);
    const hrs = Math.floor(mins / 60);
    if (hrs > 0) return `${hrs}h ${mins % 60}m`;
    if (mins > 0) return `${mins}m`;
    return `${Math.floor(seconds)}s`;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-text-primary">Login History</h2>
          <p className="text-text-secondary text-sm">Historical login events with session duration</p>
        </div>
        <button
          onClick={fetchHistory}
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
              <th className="px-6 py-3.5">Logout Time</th>
              <th className="px-6 py-3.5">Duration</th>
              <th className="px-6 py-3.5">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border text-sm">
            {history.map(h => (
              <tr key={h.id} className="hover:bg-surface-hover/40 transition-colors">
                <td className="px-6 py-3.5 font-medium text-text-primary">{h.username || h.user_id}</td>
                <td className="px-6 py-3.5 text-text-secondary font-mono text-xs">{h.ip_address || '—'}</td>
                <td className="px-6 py-3.5 text-text-secondary text-xs">{new Date(h.login_at).toLocaleString()}</td>
                <td className="px-6 py-3.5 text-text-secondary text-xs">
                  {h.logout_at ? new Date(h.logout_at).toLocaleString() : '—'}
                </td>
                <td className="px-6 py-3.5 text-xs font-medium">
                  {formatDuration(h.duration_seconds) || '—'}
                </td>
                <td className="px-6 py-3.5">
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                    h.logout_at
                      ? 'bg-surface-hover text-text-muted border-border'
                      : 'bg-emerald-500/15 text-emerald-400 border-emerald-500/25'
                  }`}>
                    {h.logout_at ? 'Ended' : 'Active'}
                  </span>
                </td>
              </tr>
            ))}
            {history.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-text-muted">
                  <History className="w-8 h-8 mx-auto text-text-muted/40 mb-2" />
                  <p>No login history recorded yet.</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
