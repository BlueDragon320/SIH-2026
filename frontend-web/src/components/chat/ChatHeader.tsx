import React from 'react';
import {
  Menu,
  Sliders,
  Sparkles,
  Zap,
  Activity,
  Layers,
  ChevronRight,
  PanelRightOpen,
  PanelRightClose
} from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';

interface ChatHeaderProps {
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({ sidebarOpen, onToggleSidebar }) => {
  const {
    selectedModel,
    getActiveSession,
    isStreaming,
    isParamsOpen,
    setParamsOpen,
    isArtifactOpen,
    openArtifact,
    closeArtifact,
    activeArtifact
  } = useChatStore();

  const currentSession = getActiveSession();
  const lastAssistantMsg = [...(currentSession?.messages || [])].reverse().find(m => m.role === 'assistant');

  // Verdict pill
  const activeModelDisplay = lastAssistantMsg?.model || (selectedModel === 'Auto' ? 'Auto-Route Engine' : selectedModel);
  const liveTps = lastAssistantMsg?.tokensPerSecond || 0;

  return (
    <header className="h-12 border-b border-border bg-surface-subtle/80 backdrop-blur-md px-4 flex items-center justify-between shrink-0 z-20 select-none">
      <div className="flex items-center gap-3">
        {!sidebarOpen && (
          <button
            onClick={onToggleSidebar}
            className="p-1.5 text-text-muted hover:text-text-primary hover:bg-surface rounded-md transition-colors"
            title="Open Sidebar"
          >
            <Menu className="w-4 h-4" />
          </button>
        )}

        {/* Active Model / Router Verdict Pill */}
        <div className="flex items-center gap-2 px-2.5 py-1 bg-surface border border-border rounded-full text-xs">
          <span className="w-2 h-2 rounded-full bg-crimson-500 animate-pulse"></span>
          <span className="text-[11px] text-text-muted font-medium">Model:</span>
          <span className="font-mono text-text-primary font-medium text-xs">
            {activeModelDisplay}
          </span>
          {lastAssistantMsg?.taskType && (
            <span className="text-[10px] font-mono uppercase tracking-wider text-crimson-400 bg-crimson-950/60 px-1.5 py-0.2 rounded border border-crimson-900/40">
              {lastAssistantMsg.taskType}
            </span>
          )}
        </div>

        {/* Live Tokens/sec Telemetry Badge */}
        {(liveTps > 0 || isStreaming) && (
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 bg-surface/80 border border-border/80 rounded-full text-[11px] font-mono text-text-secondary">
            <Zap className={`w-3 h-3 ${isStreaming ? 'text-amber-400 animate-bounce' : 'text-emerald-400'}`} />
            <span>
              {liveTps > 0 ? `${liveTps} tokens/s` : 'Computing…'}
            </span>
          </div>
        )}
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-1.5">
        {/* Toggle Artifacts Drawer */}
        <button
          onClick={() => {
            if (isArtifactOpen) closeArtifact();
            else if (activeArtifact) openArtifact(activeArtifact);
          }}
          className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium border transition-colors ${
            isArtifactOpen
              ? 'bg-crimson-950/40 border-crimson-700/60 text-crimson-300'
              : 'bg-surface border-border text-text-muted hover:text-text-primary hover:bg-surface-hover'
          }`}
          title={isArtifactOpen ? 'Close Artifact Canvas' : 'Open Artifact Canvas'}
        >
          {isArtifactOpen ? (
            <PanelRightClose className="w-3.5 h-3.5" />
          ) : (
            <PanelRightOpen className="w-3.5 h-3.5" />
          )}
          <span className="hidden sm:inline">Canvas</span>
        </button>

        {/* Parameters Trigger */}
        <button
          onClick={() => setParamsOpen(!isParamsOpen)}
          className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium border transition-colors ${
            isParamsOpen
              ? 'bg-surface-active border-crimson-600/60 text-text-primary'
              : 'bg-surface border-border text-text-muted hover:text-text-primary hover:bg-surface-hover'
          }`}
          title="Conversation Settings"
        >
          <Sliders className="w-3.5 h-3.5 text-crimson-500" />
          <span className="hidden sm:inline">Settings</span>
        </button>
      </div>
    </header>
  );
};
