import React, { useState, useEffect } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { LoginPage } from './components/auth/LoginPage';
import { AdminDashboard } from './pages/AdminDashboard';
import { Sidebar } from './components/layout/Sidebar';
import { ChatHeader } from './components/chat/ChatHeader';
import { HeroEmptyState } from './components/chat/HeroEmptyState';
import { MessageThread } from './components/chat/MessageThread';
import { ChatInputDock } from './components/chat/ChatInputDock';
import { ArtifactCanvas } from './components/artifacts/ArtifactCanvas';
import { ParametersDrawer } from './components/drawers/ParametersDrawer';
import { ModelManagerModal } from './components/modals/ModelManagerModal';
import { useChatStore } from './store/useChatStore';

const ChatWorkbench = () => {
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

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        createSession();
      }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
        e.preventDefault();
        setSidebarOpen(prev => !prev);
      }
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
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onOpenModelManager={() => setModelManagerOpen(true)}
      />
      <div className="flex-1 flex flex-col h-full overflow-hidden min-w-0">
        <PanelGroup direction="horizontal" className="flex-1 h-full">
          <Panel defaultSize={isArtifactOpen ? 55 : 100} minSize={35} className="flex flex-col h-full overflow-hidden bg-background">
            <ChatHeader
              sidebarOpen={sidebarOpen}
              onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
            />
            <div className="flex-1 flex flex-col overflow-hidden relative">
              {hasMessages ? (
                <MessageThread messages={currentSession?.messages || []} />
              ) : (
                <HeroEmptyState />
              )}
            </div>
            <ChatInputDock />
          </Panel>
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
      <ParametersDrawer />
      <ModelManagerModal
        isOpen={modelManagerOpen}
        onClose={() => setModelManagerOpen(false)}
      />
    </div>
  );
};

const RootRoute: React.FC = () => {
  const { user, isAdmin, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background text-text-primary">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-crimson-500"></div>
      </div>
    );
  }
  if (isAdmin || user?.role === 'admin') {
    return <Navigate to="/admin" replace />;
  }
  return <ChatWorkbench />;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <RootRoute />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/workbench" 
          element={
            <ProtectedRoute>
              <ChatWorkbench />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin/*" 
          element={
            <ProtectedRoute requireAdmin={true}>
              <AdminDashboard />
            </ProtectedRoute>
          } 
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
};
export default App;
