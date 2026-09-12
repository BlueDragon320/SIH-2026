import React, { useEffect, useState } from 'react';
import { adminApi } from '../../services/adminApi';
import { UsageStatsUser } from '../../types/admin';
import { BarChart2, RefreshCw } from 'lucide-react';

export function UsageAnalytics() {
  const [stats, setStats] = useState<UsageStatsUser[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const data = await adminApi.getUsageStats();
      setStats(data.sort((a, b) => b.task_count - a.task_count));
    } catch (e) {
      console.error('Failed to load usage stats', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-text-primary">Usage Analytics</h2>
          <p className="text-text-secondary text-sm">Per-user task metrics and model utilization</p>
        </div>
        <button
          onClick={fetchData}
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
              <th className="px-6 py-3.5">Tasks Created</th>
              <th className="px-6 py-3.5">Models Used</th>
              <th className="px-6 py-3.5">Last Activity</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border text-sm">
            {stats.map(s => (
              <tr key={s.user_id} className="hover:bg-surface-hover/40 transition-colors">
                <td className="px-6 py-4 font-medium text-text-primary">{s.username || s.user_id}</td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/15 text-blue-400 border border-blue-500/25">
                    <BarChart2 className="w-3 h-3" />
                    {s.task_count}
                  </span>
                </td>
                <td className="px-6 py-4 text-text-secondary">
                  <div className="flex flex-wrap gap-1">
                    {(s.models_used || []).length > 0 ? (
                      (s.models_used || []).map((m, i) => (
                        <span key={i} className="px-2 py-0.5 rounded text-[10px] font-mono bg-surface-hover border border-border text-text-secondary">
                          {m}
                        </span>
                      ))
                    ) : (
                      <span className="text-text-muted text-xs">—</span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 text-xs text-text-secondary">
                  {s.last_task_at ? new Date(s.last_task_at).toLocaleString() : 'Never'}
                </td>
              </tr>
            ))}
            {stats.length === 0 && (
              <tr>
                <td colSpan={4} className="px-6 py-12 text-center text-text-muted">
                  <BarChart2 className="w-8 h-8 mx-auto text-text-muted/40 mb-2" />
                  <p>No task activity recorded yet.</p>
                  <p className="text-xs mt-1">User task metrics appear here as department operators submit prompts to the agent.</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
