import React, { useEffect, useState } from 'react';
import { adminApi } from '../../services/adminApi';
import { RefreshCw, FileText, ChevronDown, ChevronUp } from 'lucide-react';

export function AuditLogs() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await adminApi.getAuditLogs(200);
      setLogs(data);
    } catch (e) {
      console.error('Failed to load audit logs', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const getEventColor = (type: string) => {
    switch (type) {
      case 'ROUTING_DECISION': return 'bg-blue-500/15 text-blue-400 border-blue-500/25';
      case 'TOOL_INVOCATION': return 'bg-purple-500/15 text-purple-400 border-purple-500/25';
      case 'TASK_COMPLETED': return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/25';
      case 'TASK_FAILED': return 'bg-rose-500/15 text-rose-400 border-rose-500/25';
      case 'SANDBOX_EXECUTION': return 'bg-amber-500/15 text-amber-400 border-amber-500/25';
      default: return 'bg-surface-hover text-text-secondary border-border';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-text-primary">Audit Logs</h2>
          <p className="text-text-secondary text-sm">Immutable record of all agent operations, routing decisions, and tool invocations</p>
        </div>
        <button
          onClick={fetchLogs}
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
              <th className="px-6 py-3.5">Timestamp</th>
              <th className="px-6 py-3.5">Task ID</th>
              <th className="px-6 py-3.5">Event Type</th>
              <th className="px-6 py-3.5">Model / Tool</th>
              <th className="px-6 py-3.5">Air-Gap</th>
              <th className="px-6 py-3.5 w-10"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border text-sm">
            {logs.map((l, i) => {
              const isExpanded = expandedId === (l.id || i);
              return (
                <React.Fragment key={l.id || i}>
                  <tr 
                    className="hover:bg-surface-hover/40 transition-colors cursor-pointer"
                    onClick={() => setExpandedId(isExpanded ? null : (l.id || i))}
                  >
                    <td className="px-6 py-3 text-xs text-text-secondary font-mono">
                      {new Date(l.timestamp || l.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-3 text-xs font-mono text-text-muted">
                      {l.task_id ? l.task_id.slice(0, 15) : '—'}
                    </td>
                    <td className="px-6 py-3">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-semibold border ${getEventColor(l.event_type)}`}>
                        {l.event_type}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-text-secondary text-xs">
                      {l.model_used && <span className="font-mono">{l.model_used}</span>}
                      {l.tool_name && <span className="font-mono text-purple-400">{l.tool_name}</span>}
                      {!l.model_used && !l.tool_name && '—'}
                    </td>
                    <td className="px-6 py-3">
                      {l.airgap_verified ? (
                        <span className="text-emerald-400 text-[10px] font-semibold">✓ Verified</span>
                      ) : (
                        <span className="text-text-muted text-[10px]">—</span>
                      )}
                    </td>
                    <td className="px-6 py-3 text-text-muted">
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </td>
                  </tr>
                  {isExpanded && (
                    <tr>
                      <td colSpan={6} className="px-6 py-3 bg-background/50">
                        <div className="grid grid-cols-2 gap-4 text-xs">
                          {l.duration_ms != null && (
                            <div>
                              <span className="text-text-muted font-semibold uppercase text-[10px]">Duration</span>
                              <div className="text-text-secondary mt-0.5">{l.duration_ms}ms</div>
                            </div>
                          )}
                          {l.user_id && (
                            <div>
                              <span className="text-text-muted font-semibold uppercase text-[10px]">User ID</span>
                              <div className="text-text-secondary mt-0.5 font-mono">{l.user_id}</div>
                            </div>
                          )}
                          {l.input_payload && (
                            <div className="col-span-2">
                              <span className="text-text-muted font-semibold uppercase text-[10px]">Input</span>
                              <pre className="text-text-secondary mt-0.5 font-mono text-[11px] bg-surface p-2 rounded border border-border overflow-x-auto max-h-32">
                                {l.input_payload.length > 500 ? l.input_payload.slice(0, 500) + '...' : l.input_payload}
                              </pre>
                            </div>
                          )}
                          {l.output_payload && (
                            <div className="col-span-2">
                              <span className="text-text-muted font-semibold uppercase text-[10px]">Output</span>
                              <pre className="text-text-secondary mt-0.5 font-mono text-[11px] bg-surface p-2 rounded border border-border overflow-x-auto max-h-32">
                                {l.output_payload.length > 500 ? l.output_payload.slice(0, 500) + '...' : l.output_payload}
                              </pre>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
            {logs.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-text-muted">
                  <FileText className="w-8 h-8 mx-auto text-text-muted/40 mb-2" />
                  <p>No audit events recorded yet.</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
