import React from 'react';
import { Navigate, Outlet, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { ShieldAlert, ArrowLeft } from 'lucide-react';

export function ProtectedRoute({ requireAdmin = false, children }: { requireAdmin?: boolean, children?: React.ReactNode }) {
  const { isAuthenticated, isAdmin, isLoading } = useAuth();

  if (isLoading) {
    return <div className="flex h-screen items-center justify-center bg-background text-text-primary">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && !isAdmin) {
    return (
      <div className="flex h-screen flex-col items-center justify-center bg-background text-text-primary p-6 text-center">
        <div className="p-4 bg-crimson-600/15 border border-crimson-600/30 rounded-2xl mb-4 text-crimson-500 shadow-[0_0_30px_rgba(239,35,60,0.2)]">
          <ShieldAlert className="w-12 h-12" />
        </div>
        <h1 className="text-2xl font-bold mb-2">Access Denied</h1>
        <p className="text-text-secondary text-sm max-w-md mb-6 leading-relaxed">
          The <strong>/admin</strong> dashboard is strictly restricted to the <strong>Master Head of the Department</strong>.
          Regular user accounts cannot access administrative surveillance and system management.
        </p>
        <Link
          to="/"
          className="flex items-center gap-2 px-5 py-2.5 bg-surface hover:bg-surface-hover border border-border text-text-primary rounded-xl text-sm font-medium transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Return to Chat Workbench
        </Link>
      </div>
    );
  }

  return children ? <>{children}</> : <Outlet />;
}
