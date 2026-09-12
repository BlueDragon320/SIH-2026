import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Activity, Users, Clock, History, BarChart2, MessageSquare, FileText, ArrowLeft, Shield } from 'lucide-react';

import { DashboardOverview } from '../components/admin/DashboardOverview';
import { UserManagement } from '../components/admin/UserManagement';
import { ActiveSessions } from '../components/admin/ActiveSessions';
import { LoginHistory } from '../components/admin/LoginHistory';
import { UsageAnalytics } from '../components/admin/UsageAnalytics';
import { UserChats } from '../components/admin/UserChats';
import { AuditLogs } from '../components/admin/AuditLogs';

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: Activity },
  { id: 'users', label: 'Users', icon: Users },
  { id: 'sessions', label: 'Active Sessions', icon: Clock },
  { id: 'login-history', label: 'Login History', icon: History },
  { id: 'usage', label: 'Usage Analytics', icon: BarChart2 },
  { id: 'chats', label: 'User Chats', icon: MessageSquare },
  { id: 'audit', label: 'Audit Logs', icon: FileText },
];

export function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const { user, logout } = useAuth();

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return <DashboardOverview />;
      case 'users': return <UserManagement />;
      case 'sessions': return <ActiveSessions />;
      case 'login-history': return <LoginHistory />;
      case 'usage': return <UsageAnalytics />;
      case 'chats': return <UserChats />;
      case 'audit': return <AuditLogs />;
      default: return <DashboardOverview />;
    }
  };

  return (
    <div className="flex h-screen bg-background text-text-primary">
      {/* Sidebar */}
      <div className="w-64 bg-surface border-r border-border flex flex-col">
        <div className="p-4 border-b border-border flex items-center gap-3">
          <div className="p-2 bg-crimson-600/15 border border-crimson-600/30 rounded-xl text-crimson-500">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-base leading-tight">Admin Portal</h1>
            <div className="text-[10px] uppercase font-mono tracking-wider text-crimson-400 font-semibold">Head of Department</div>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto py-4">
          <nav className="space-y-1 px-2">
            {NAV_ITEMS.map(item => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                  activeTab === item.id 
                    ? 'bg-crimson-600/10 text-crimson-500 font-medium' 
                    : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'
                }`}
              >
                <item.icon className="w-5 h-5" />
                {item.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-4 border-t border-border">
          <div className="mb-3 p-2 rounded-lg bg-surface-subtle border border-border/60">
            <div className="text-[10px] text-text-muted uppercase font-mono tracking-wider">Authorized Master Head</div>
            <div className="text-sm font-semibold text-text-primary truncate">{user?.username || 'Administrator'}</div>
          </div>
          <Link 
            to="/workbench" 
            className="flex items-center justify-center gap-2 w-full py-2 bg-surface hover:bg-surface-hover border border-border text-text-primary rounded-lg transition-colors mb-2 text-xs font-medium"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Open Test Workbench
          </Link>
          <button 
            onClick={logout}
            className="w-full py-2 text-sm text-rose-400 hover:text-rose-300 hover:bg-rose-400/10 rounded-lg transition-colors"
          >
            Sign Out
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto bg-background">
        <div className="p-8 max-w-7xl mx-auto">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}
