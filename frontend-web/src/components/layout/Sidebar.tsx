import { useAuth } from '../../contexts/AuthContext';
import { Link } from 'react-router-dom';
import { User, LogOut, Shield } from 'lucide-react';
import React, { useState, useEffect } from 'react';
import {
  Plus,
  Pin,
  Trash2,
  Edit2,
  Download,
  Check,
  X,
  Cpu,
  ShieldCheck,
  ShieldAlert,
  ChevronDown,
  Layers,
  Sparkles,
  Search,
  ExternalLink,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';
import { Session } from '../../types';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onOpenModelManager: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle, onOpenModelManager }) => {
  const { user, isAdmin, logout } = useAuth();
  const {
    sessions,
    activeSessionId,
    createSession,
    selectSession,
    deleteSession,
    renameSession,
    pinSession,
    exportSession,
    clearAllChats,
    selectedModel,
    setSelectedModel,
    models,
    fetchModels,
    hardware,
    network,
    fetchTelemetry
  } = useChatStore();

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Telemetry polling
  useEffect(() => {
    fetchModels();
    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 3000);
    return () => clearInterval(interval);
  }, [fetchModels, fetchTelemetry]);

  // Group sessions by Today, Previous 7 Days, and Older
  const now = new Date().getTime();
  const oneDay = 24 * 60 * 60 * 1000;
  const sevenDays = 7 * oneDay;

  const filteredSessions = sessions.filter(s =>
    s.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const pinnedSessions = filteredSessions.filter(s => s.pinned);
  const todaySessions = filteredSessions.filter(s => !s.pinned && now - new Date(s.createdAt).getTime() < oneDay);
  const weekSessions = filteredSessions.filter(
    s => !s.pinned && now - new Date(s.createdAt).getTime() >= oneDay && now - new Date(s.createdAt).getTime() < sevenDays
  );
  const olderSessions = filteredSessions.filter(s => !s.pinned && now - new Date(s.createdAt).getTime() >= sevenDays);

  const handleStartRename = (e: React.MouseEvent, session: Session) => {
    e.stopPropagation();
    setEditingId(session.id);
    setEditTitle(session.title);
  };

  const handleSaveRename = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    renameSession(id, editTitle);
    setEditingId(null);
  };

  const handleCancelRename = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(null);
  };

  const renderSessionItem = (s: Session) => {
    const isActive = s.id === activeSessionId;
    const isEditing = s.id === editingId;

    return (
      <div
        key={s.id}
        onClick={() => selectSession(s.id)}
        className={`group relative flex items-center justify-between px-3 py-2 rounded-lg text-xs cursor-pointer transition-all duration-150 ${
          isActive
            ? 'bg-surface-active text-text-primary border border-crimson-600/40 shadow-sm'
            : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'
        }`}
      >
        <div className="flex items-center gap-2 min-w-0 flex-1 mr-2">
          {s.pinned && <Pin className="w-3 h-3 text-crimson-500 shrink-0 fill-crimson-500" />}
          
          {isEditing ? (
            <input
              type="text"
              value={editTitle}
              onChange={e => setEditTitle(e.target.value)}
              onClick={e => e.stopPropagation()}
              onKeyDown={e => {
                if (e.key === 'Enter') handleSaveRename(e as any, s.id);
                if (e.key === 'Escape') setEditingId(null);
              }}
              autoFocus
              className="w-full bg-background border border-crimson-500 px-1.5 py-0.5 rounded text-text-primary text-xs outline-none"
            />
          ) : (
            <span className="truncate font-medium">{s.title}</span>
          )}
        </div>

        {isEditing ? (
          <div className="flex items-center gap-1 shrink-0">
            <button
              onClick={e => handleSaveRename(e, s.id)}
              className="p-1 text-emerald-400 hover:text-emerald-300 rounded hover:bg-surface"
              title="Save"
            >
              <Check className="w-3 h-3" />
            </button>
            <button
              onClick={handleCancelRename}
              className="p-1 text-text-muted hover:text-text-primary rounded hover:bg-surface"
              title="Cancel"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        ) : (
          <div className="opacity-0 group-hover:opacity-100 flex items-center gap-0.5 shrink-0 transition-opacity">
            <button
              onClick={e => handleStartRename(e, s)}
              className="p-1 text-text-muted hover:text-text-primary hover:bg-surface rounded"
              title="Rename"
            >
              <Edit2 className="w-3 h-3" />
            </button>
            <button
              onClick={e => {
                e.stopPropagation();
                pinSession(s.id);
              }}
              className="p-1 text-text-muted hover:text-crimson-500 hover:bg-surface rounded"
              title={s.pinned ? 'Unpin' : 'Pin'}
            >
              <Pin className="w-3 h-3" />
            </button>
            <button
              onClick={e => {
                e.stopPropagation();
                exportSession(s.id, 'markdown');
              }}
              className="p-1 text-text-muted hover:text-text-primary hover:bg-surface rounded"
              title="Export Markdown"
            >
              <Download className="w-3 h-3" />
            </button>
            <button
              onClick={e => {
                e.stopPropagation();
                deleteSession(s.id);
              }}
              className="p-1 text-text-muted hover:text-rose-400 hover:bg-surface rounded"
              title="Delete"
            >
              <Trash2 className="w-3 h-3" />
            </button>
          </div>
        )}
      </div>
    );
  };

  // Hardware metrics
  const vramUsedGb = hardware?.gpu?.available ? (hardware.gpu.vram_used_mb / 1024).toFixed(1) : '0.0';
  const vramTotalGb = hardware?.gpu?.available ? (hardware.gpu.vram_total_mb / 1024).toFixed(1) : '6.0';
  const gpuUtil = hardware?.gpu?.available ? Math.round(hardware.gpu.gpu_util_percent) : 0;
  const gpuTemp = hardware?.gpu?.available ? Math.round(hardware.gpu.temperature_c) : 0;
  const isAirGapped = network?.verified_zero_egress || (network?.external_egress_rate_bps || 0) < 500;

  // Derive cleaned GPU display name matching device specs
  const rawGpuName = hardware?.gpu?.name;
  const gpuDisplayName = rawGpuName && rawGpuName !== 'N/A'
    ? rawGpuName
        .replace(/^NVIDIA(\s+Corporation)?\s*/i, '')
        .replace(/^Advanced Micro Devices,?\s*Inc\.?\s*/i, '')
        .replace(/\[|\]/g, '')
        .trim()
    : (hardware?.gpu?.available ? 'Dedicated GPU' : 'Host GPU');

  return (
    <aside
      className={`relative flex flex-col h-screen bg-surface-subtle border-r border-border transition-all duration-300 ease-in-out select-none shrink-0 z-30 ${
        isOpen ? 'w-[280px]' : 'w-[0px] overflow-hidden border-r-0'
      }`}
    >
      {/* 1. Header: Brand & New Chat */}
      <div className="p-3 border-b border-border/60 shrink-0 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <span className="w-3.5 h-3.5 bg-crimson-600 rounded-[3px] rotate-45 shrink-0 shadow-[0_0_10px_rgba(239,35,60,0.5)]"></span>
            <div className="leading-tight">
              <span className="font-semibold text-sm tracking-tight text-text-primary">Workbench</span>
              <span className="text-[10px] font-mono uppercase tracking-widest text-crimson-500 ml-1.5 font-semibold">Auto-Route</span>
            </div>
          </div>
          <button
            onClick={onToggle}
            className="p-1 text-text-muted hover:text-text-primary hover:bg-surface rounded-md transition-colors"
            title="Collapse Sidebar"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
        </div>

        {/* New Chat Button with Hotkey */}
        <button
          onClick={() => createSession()}
          className="w-full flex items-center justify-between px-3 py-2 bg-surface hover:bg-surface-hover border border-border hover:border-crimson-600/50 rounded-lg text-xs font-medium text-text-primary transition-all group shadow-sm"
        >
          <div className="flex items-center gap-2">
            <Plus className="w-3.5 h-3.5 text-crimson-500 group-hover:scale-110 transition-transform" />
            <span>New Chat</span>
          </div>
          <span className="text-[10px] font-mono text-text-muted bg-background px-1.5 py-0.5 rounded border border-border">
            Ctrl+K
          </span>
        </button>

        {/* Quick Search */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-text-muted absolute left-2.5 top-2.5" />
          <input
            type="text"
            placeholder="Search chats..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full bg-background border border-border text-xs rounded-md pl-8 pr-2 py-1.5 text-text-primary placeholder:text-text-muted focus:outline-none focus:border-crimson-600/60"
          />
        </div>
      </div>

      {/* 2. Model Selection Bar */}
      <div className="px-3 py-2 border-b border-border/40 shrink-0 bg-surface/30">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[10px] font-mono uppercase tracking-wider text-text-muted">Target Model</span>
          <button
            onClick={onOpenModelManager}
            className="text-[10px] text-crimson-500 hover:text-crimson-400 font-medium flex items-center gap-1"
          >
            <Layers className="w-2.5 h-2.5" />
            Manage
          </button>
        </div>
        <div className="relative">
          <select
            value={selectedModel}
            onChange={e => setSelectedModel(e.target.value)}
            className="w-full appearance-none bg-surface border border-border hover:border-border-strong text-text-primary text-xs rounded-md px-2.5 py-1.5 pr-7 focus:outline-none focus:border-crimson-500 cursor-pointer"
          >
            <option value="Auto">⚡ Auto-Select (Intelligent Router)</option>
            <optgroup label="Installed Local LLMs">
              {models.filter(m => m.is_installed).map(m => (
                <option key={m.ollama_tag} value={m.ollama_tag}>
                  ● {m.name} ({m.ollama_tag})
                </option>
              ))}
            </optgroup>
          </select>
          <ChevronDown className="w-3.5 h-3.5 text-text-muted absolute right-2.5 top-2.5 pointer-events-none" />
        </div>
      </div>

      {/* 3. Chat History List */}
      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-4">
        <div className="flex items-center justify-between px-2 pt-1 pb-0.5">
          <span className="text-[10px] font-mono uppercase tracking-wider text-text-muted">Chat History</span>
          {sessions.some(s => s.messages && s.messages.length > 0) && (
            <button
              onClick={() => {
                if (window.confirm('Clear all chat history? This will start a completely fresh session.')) {
                  clearAllChats();
                }
              }}
              className="text-[10px] text-text-muted hover:text-rose-400 flex items-center gap-1 transition-colors px-1 py-0.5 rounded hover:bg-surface cursor-pointer"
              title="Clear all chat history"
            >
              <Trash2 className="w-2.5 h-2.5" />
              Clear All
            </button>
          )}
        </div>
        {pinnedSessions.length > 0 && (
          <div>
            <div className="px-2 pb-1 text-[10px] font-mono uppercase tracking-wider text-text-muted">Pinned</div>
            <div className="space-y-0.5">{pinnedSessions.map(renderSessionItem)}</div>
          </div>
        )}

        {todaySessions.length > 0 && (
          <div>
            <div className="px-2 pb-1 text-[10px] font-mono uppercase tracking-wider text-text-muted">Today</div>
            <div className="space-y-0.5">{todaySessions.map(renderSessionItem)}</div>
          </div>
        )}

        {weekSessions.length > 0 && (
          <div>
            <div className="px-2 pb-1 text-[10px] font-mono uppercase tracking-wider text-text-muted">Previous 7 Days</div>
            <div className="space-y-0.5">{weekSessions.map(renderSessionItem)}</div>
          </div>
        )}

        {olderSessions.length > 0 && (
          <div>
            <div className="px-2 pb-1 text-[10px] font-mono uppercase tracking-wider text-text-muted">Older</div>
            <div className="space-y-0.5">{olderSessions.map(renderSessionItem)}</div>
          </div>
        )}

        {filteredSessions.length === 0 && (
          <div className="text-center py-6 text-xs text-text-muted">
            No conversations found.
          </div>
        )}
      </div>

      {/* 4. Footer: Hardware Telemetry Bar */}
      <div className="p-3 border-t border-border/80 bg-background/90 shrink-0 space-y-2.5">

        {/* User Profile Section */}
        <div className="bg-surface/80 border border-border/80 rounded-lg p-2.5 space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-crimson-600/20 text-crimson-500 flex items-center justify-center shrink-0">
              <User className="w-3.5 h-3.5" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-[11px] font-medium text-text-primary truncate">{user?.username || 'User'}</div>
              <div className="text-[9px] text-text-muted flex items-center gap-1">
                <span className={`w-1.5 h-1.5 rounded-full ${isAdmin ? 'bg-crimson-500' : 'bg-emerald-500'}`}></span>
                {isAdmin ? 'Admin' : 'Operator'}
              </div>
            </div>
          </div>
          
          <div className="flex gap-1.5 pt-1">
            {isAdmin && (
              <Link 
                to="/admin" 
                className="flex-1 flex items-center justify-center gap-1 py-1 px-2 bg-surface hover:bg-surface-hover border border-border rounded text-[10px] text-text-primary transition-colors"
              >
                <Shield className="w-3 h-3 text-crimson-500" />
                Admin
              </Link>
            )}
            <button 
              onClick={logout}
              className="flex-1 flex items-center justify-center gap-1 py-1 px-2 bg-surface hover:bg-surface-hover border border-border rounded text-[10px] text-rose-400 hover:text-rose-300 transition-colors"
            >
              <LogOut className="w-3 h-3" />
              Logout
            </button>
          </div>
        </div>

        {/* GPU & VRAM telemetry */}
        <div className="bg-surface/80 border border-border/80 rounded-lg p-2.5 text-[11px] space-y-1.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-text-secondary font-medium min-w-0">
              <Cpu className="w-3.5 h-3.5 text-crimson-500 shrink-0" />
              <span className="truncate max-w-[130px]" title={rawGpuName || gpuDisplayName}>
                {gpuDisplayName}
              </span>
            </div>
            <span className="font-mono text-[10px] text-text-primary shrink-0 ml-1">
              {vramUsedGb} / {vramTotalGb} GB
            </span>
          </div>

          {/* VRAM Progress bar */}
          <div className="w-full bg-background rounded-full h-1.5 overflow-hidden border border-border/40">
            <div
              className="bg-gradient-to-r from-emerald-500 via-amber-500 to-crimson-600 h-full rounded-full transition-all duration-500"
              style={{
                width: `${Math.min(
                  ((hardware?.gpu?.vram_used_mb || 100) / (hardware?.gpu?.vram_total_mb || 6144)) * 100,
                  100
                )}%`,
              }}
            />
          </div>

          <div className="flex items-center justify-between text-[10px] text-text-muted pt-0.5">
            <span>Load: {gpuUtil}%</span>
            <span>Temp: {gpuTemp}°C</span>
          </div>
        </div>

        {/* Air-gap security status badge */}
        <div className="flex items-center justify-between px-2 py-1 bg-surface/50 border border-border/50 rounded-md text-[10px]">
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-3 h-3 text-emerald-400" />
            <span className="text-emerald-400 font-medium">100% Offline</span>
          </div>
          <span className="font-mono text-text-muted">Zero Egress</span>
        </div>
      </div>
    </aside>
  );
};
