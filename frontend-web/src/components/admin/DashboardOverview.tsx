import React, { useEffect, useState } from 'react';
import { adminApi } from '../../services/adminApi';
import { Users, Clock, CheckCircle, Database, Server, MessageSquare, Cpu, HardDrive, Thermometer, RefreshCw } from 'lucide-react';
import { DashboardStats } from '../../types/admin';

export function DashboardOverview() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [system, setSystem] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [st, sys] = await Promise.all([
        adminApi.getDashboardStats(),
        adminApi.getSystemHealth()
      ]);
      setStats(st);
      setSystem(sys);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const int = setInterval(fetchData, 15000);
    return () => clearInterval(int);
  }, []);

  const ramUsedGB = system?.ram ? (system.ram.used_mb / 1024).toFixed(1) : '0';
  const ramTotalGB = system?.ram ? (system.ram.total_mb / 1024).toFixed(1) : '0';
  const ramPercent = system?.ram?.percent || 0;
  const cpuPercent = system?.cpu_percent || 0;
  const gpuData = system?.gpu;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-text-primary">Overview</h2>
        <button
          onClick={fetchData}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 bg-surface hover:bg-surface-hover border border-border text-text-primary rounded-lg text-sm transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-crimson-500' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard title="Total Users" value={stats?.total_users || 0} icon={Users} color="text-blue-400" />
        <StatCard title="Active Sessions" value={stats?.active_sessions || 0} icon={Clock} color="text-emerald-400" />
        <StatCard title="User Chats" value={stats?.total_user_chats || 0} icon={MessageSquare} color="text-amber-400" />
        <StatCard title="Tasks Today" value={stats?.total_tasks_today || 0} icon={CheckCircle} color="text-purple-400" />
        <StatCard title="Total Tasks" value={stats?.total_tasks_all || 0} icon={Database} color="text-crimson-400" />
      </div>

      {/* System Health */}
      {system && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
          {/* CPU & RAM */}
          <div className="bg-surface border border-border p-6 rounded-xl space-y-5">
            <h3 className="text-lg font-bold flex items-center gap-2 text-text-primary">
              <Server className="w-5 h-5 text-blue-400" /> System Resources
            </h3>

            <div>
              <div className="flex justify-between text-sm mb-1.5">
                <span className="text-text-secondary flex items-center gap-1.5">
                  <Cpu className="w-3.5 h-3.5" /> CPU Usage
                </span>
                <span className="font-mono font-medium text-text-primary">{cpuPercent.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-background rounded-full h-2.5">
                <div
                  className={`h-2.5 rounded-full transition-all duration-500 ${cpuPercent > 80 ? 'bg-rose-500' : cpuPercent > 50 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                  style={{ width: `${Math.min(cpuPercent, 100)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-1.5">
                <span className="text-text-secondary flex items-center gap-1.5">
                  <HardDrive className="w-3.5 h-3.5" /> RAM ({ramUsedGB} / {ramTotalGB} GB)
                </span>
                <span className="font-mono font-medium text-text-primary">{ramPercent.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-background rounded-full h-2.5">
                <div
                  className={`h-2.5 rounded-full transition-all duration-500 ${ramPercent > 85 ? 'bg-rose-500' : ramPercent > 60 ? 'bg-amber-500' : 'bg-blue-500'}`}
                  style={{ width: `${Math.min(ramPercent, 100)}%` }}
                />
              </div>
            </div>
          </div>

          {/* GPU */}
          {gpuData?.available && (
            <div className="bg-surface border border-border p-6 rounded-xl space-y-5">
              <h3 className="text-lg font-bold flex items-center gap-2 text-text-primary">
                <span className="text-emerald-400">⬢</span> {gpuData.name || 'GPU'}
              </h3>

              <div>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="text-text-secondary">VRAM ({((gpuData.vram_total_mb - gpuData.vram_free_mb) / 1024).toFixed(1)} / {(gpuData.vram_total_mb / 1024).toFixed(1)} GB)</span>
                  <span className="font-mono font-medium text-text-primary">
                    {((1 - gpuData.vram_free_mb / gpuData.vram_total_mb) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-background rounded-full h-2.5">
                  <div
                    className="bg-emerald-500 h-2.5 rounded-full transition-all duration-500"
                    style={{ width: `${((1 - gpuData.vram_free_mb / gpuData.vram_total_mb) * 100)}%` }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-text-muted text-xs uppercase mb-0.5">GPU Utilization</div>
                  <div className="font-mono font-medium text-text-primary">{gpuData.gpu_util_percent}%</div>
                </div>
                <div>
                  <div className="text-text-muted text-xs uppercase mb-0.5 flex items-center gap-1">
                    <Thermometer className="w-3 h-3" /> Temperature
                  </div>
                  <div className={`font-mono font-medium ${gpuData.temperature_c > 80 ? 'text-rose-400' : gpuData.temperature_c > 60 ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {gpuData.temperature_c}°C
                  </div>
                </div>
              </div>

              {system.loaded_models && system.loaded_models.length > 0 && (
                <div>
                  <div className="text-text-muted text-xs uppercase mb-1.5">Loaded Models</div>
                  <div className="flex flex-wrap gap-1.5">
                    {system.loaded_models.map((m: any, i: number) => (
                      <span key={i} className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {typeof m === 'string' ? m : m.name || m.model || JSON.stringify(m)}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function StatCard({ title, value, icon: Icon, color }: any) {
  return (
    <div className="bg-surface border border-border p-5 rounded-xl flex items-center gap-4 hover:border-border/80 transition-colors">
      <div className={`p-3 rounded-lg bg-surface-hover ${color}`}>
        <Icon className="w-6 h-6" />
      </div>
      <div>
        <div className="text-xs text-text-muted uppercase tracking-wide font-medium">{title}</div>
        <div className="text-2xl font-bold text-text-primary">{value}</div>
      </div>
    </div>
  );
}
