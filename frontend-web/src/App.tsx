import React, { useState, useEffect } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { Sidebar } from './components/layout/Sidebar';
import { ChatHeader } from './components/chat/ChatHeader';
import { HeroEmptyState } from './components/chat/HeroEmptyState';
import { MessageThread } from './components/chat/MessageThread';
import { ChatInputDock } from './components/chat/ChatInputDock';
import { ArtifactCanvas } from './components/artifacts/ArtifactCanvas';
import { ParametersDrawer } from './components/drawers/ParametersDrawer';
import { ModelManagerModal } from './components/modals/ModelManagerModal';
import { useChatStore } from './store/useChatStore';

export const App: React.FC = () => {
  const {
    getActiveSession,
    createSession,
    isArtifactOpen,
    isParamsOpen,
    setParamsOpen
  } = useChatStore();

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [modelManagerOpen, setModelManagerOpen] = useState(false);

  const currentSession = getActiveSession();
  const hasMessages = (currentSession?.messages?.length || 0) > 0;

  // Global Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+K or Cmd+K: New Chat
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        createSession();
      }
      // Ctrl+B or Cmd+B: Toggle Sidebar
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
        e.preventDefault();
        setSidebarOpen(prev => !prev);
      }
      // Escape: Close modals
      if (e.key === 'Escape') {
        setModelManagerOpen(false);
        setParamsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [createSession, setParamsOpen]);

  return (
    <div className="flex h-screen w-screen bg-background text-text-primary overflow-hidden font-sans">
      {/* 1. Left Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onOpenModelManager={() => setModelManagerOpen(true)}
      />

      {/* 2. Main Center & Right Area with Resizable Panels */}
      <div className="flex-1 flex flex-col h-full overflow-hidden min-w-0">
        <PanelGroup direction="horizontal" className="flex-1 h-full">
          {/* Chat Canvas Panel */}
          <Panel defaultSize={isArtifactOpen ? 55 : 100} minSize={35} className="flex flex-col h-full overflow-hidden bg-background">
            {/* Top Navigation Bar */}
            <ChatHeader
              sidebarOpen={sidebarOpen}
              onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
            />

            {/* Chat Body: Empty Hero or Message Stream */}
            <div className="flex-1 flex flex-col overflow-hidden relative">
              {hasMessages ? (
                <MessageThread messages={currentSession?.messages || []} />
              ) : (
                <HeroEmptyState />
              )}
            </div>

            {/* Floating Chat Input Dock */}
            <ChatInputDock />
          </Panel>

          {/* Claude-Style Artifacts Resizable Side Drawer (50/50 Split View) */}
          {isArtifactOpen && (
            <>
              <PanelResizeHandle className="w-1.5 bg-border hover:bg-crimson-600/60 transition-colors cursor-col-resize active:bg-crimson-600" />
              <Panel defaultSize={45} minSize={25} className="h-full overflow-hidden">
                <ArtifactCanvas />
              </Panel>
            </>
          )}
        </PanelGroup>
      </div>

      {/* 3. Slide-out Advanced Parameters Drawer */}
      <ParametersDrawer />

      {/* 4. Model Manager Modal */}
      <ModelManagerModal
        isOpen={modelManagerOpen}
        onClose={() => setModelManagerOpen(false)}
      />
    </div>
  );
};
export default App;
