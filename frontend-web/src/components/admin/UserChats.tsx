import React, { useEffect, useState } from 'react';
import { adminApi } from '../../services/adminApi';
import { AuthUser, UserChat } from '../../types/admin';
import { MessageSquare, RefreshCw, Search, User, Clock, ShieldAlert, FileText, Trash2, Filter } from 'lucide-react';

export function UserChats() {
  const [users, setUsers] = useState<AuthUser[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<string>('all');
  const [allChats, setAllChats] = useState<UserChat[]>([]);
  const [filteredChats, setFilteredChats] = useState<UserChat[]>([]);
  const [selectedChat, setSelectedChat] = useState<UserChat | null>(null);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchUsers = async () => {
    try {
      const data = await adminApi.getUsers();
      setUsers(data);
    } catch (e) {
      console.error('Failed to load users', e);
    }
  };

  const fetchChats = async () => {
    setLoading(true);
    try {
      // 1. Always fetch all chats to maintain real-time counts across all users
      const allData = await adminApi.getAllUserChats();
      setAllChats(allData);

      // 2. Filter chats based on selectedUser
      let data: UserChat[] = [];
      if (selectedUserId === 'all') {
        data = allData;
      } else {
        const targetUser = users.find(u => u.id === selectedUserId || u.username === selectedUserId);
        const targetUsername = targetUser?.username?.toLowerCase();
        const targetId = targetUser?.id?.toLowerCase() || selectedUserId.toLowerCase();

        data = allData.filter(c => {
          const cUid = (c.user_id || '').toLowerCase();
          const cUname = (c.username || '').toLowerCase();
          return cUid === targetId || (targetUsername && cUname === targetUsername);
        });
      }

      setFilteredChats(data);
      setSelectedChat(prev => {
        if (!prev && data.length > 0) return data[0];
        if (prev) {
          const found = data.find(c => c.id === prev.id || c.session_id === prev.session_id);
          return found || (data.length > 0 ? data[0] : null);
        }
        return null;
      });
    } catch (e) {
      console.error('Failed to load chats', e);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteChat = async (sessionId: string) => {
    if (!confirm('Are you sure you want to delete this recorded conversation?')) return;
    try {
      await adminApi.deleteUserChat(sessionId);
      fetchChats();
    } catch (e) {
      console.error('Failed to delete chat', e);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    fetchChats();
    const interval = setInterval(fetchChats, 3000);
    return () => clearInterval(interval);
  }, [selectedUserId, users.length]);

  const displayedChats = filteredChats.filter(c => {
    const titleMatch = (c.session_name || '').toLowerCase().includes(search.toLowerCase());
    const userMatch = (c.username || c.user_id || '').toLowerCase().includes(search.toLowerCase());
    return titleMatch || userMatch;
  });

  const parseMessages = (jsonStr: string) => {
    try {
      return JSON.parse(jsonStr || '[]');
    } catch {
      return [];
    }
  };

  const selectedUserObj = users.find(u => u.id === selectedUserId || u.username === selectedUserId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold text-text-primary">Department Chat Surveillance</h2>
            <span className="text-xs bg-crimson-600/20 text-crimson-400 border border-crimson-600/30 px-2 py-0.5 rounded-full font-semibold">
              Master Head View
            </span>
          </div>
          <p className="text-text-secondary text-sm">
            Read and audit every conversation, prompt, thought process, and output generated across all users
          </p>
        </div>
        <button
          onClick={fetchChats}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 bg-surface hover:bg-surface-hover border border-border text-text-primary rounded-lg text-sm transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-crimson-500' : ''}`} />
          Refresh
        </button>
      </div>

      {/* User Quick Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 pb-1">
        <button
          onClick={() => { setSelectedUserId('all'); setSelectedChat(null); }}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
            selectedUserId === 'all'
              ? 'bg-crimson-600/15 border-crimson-600/50 text-crimson-400 font-semibold shadow-sm'
              : 'bg-surface hover:bg-surface-hover border-border text-text-secondary'
          }`}
        >
          <span>🌟 All Users</span>
          <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-background/60 text-text-muted">
            {allChats.length}
          </span>
        </button>

        {users.map(u => {
          const count = allChats.filter(c => {
            const cUid = (c.user_id || '').toLowerCase();
            const cUname = (c.username || '').toLowerCase();
            return cUid === u.id.toLowerCase() || cUname === u.username.toLowerCase();
          }).length;
          const isSelected = selectedUserId === u.id;

          return (
            <button
              key={u.id}
              onClick={() => { setSelectedUserId(u.id); setSelectedChat(null); }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                isSelected
                  ? 'bg-crimson-600/15 border-crimson-600/50 text-crimson-400 font-semibold shadow-sm'
                  : 'bg-surface hover:bg-surface-hover border-border text-text-secondary'
              }`}
            >
              <User className="w-3 h-3 text-crimson-500" />
              <span>{u.username}</span>
              <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${count > 0 ? 'bg-emerald-500/20 text-emerald-400 font-semibold' : 'bg-background/60 text-text-muted'}`}>
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Filters & Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="w-full sm:w-80">
          <select
            value={selectedUserId}
            onChange={e => {
              setSelectedUserId(e.target.value);
              setSelectedChat(null);
            }}
            className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-crimson-600 font-medium"
          >
            <option value="all">🌟 All Department Users ({allChats.length} total chats)</option>
            {users.map(u => {
              const userCount = allChats.filter(c => {
                const cUid = (c.user_id || '').toLowerCase();
                const cUname = (c.username || '').toLowerCase();
                return cUid === u.id.toLowerCase() || cUname === u.username.toLowerCase();
              }).length;
              return (
                <option key={u.id} value={u.id}>
                  👤 {u.username} ({u.role}) — {userCount} chat{userCount === 1 ? '' : 's'}
                </option>
              );
            })}
          </select>
        </div>

        <div className="relative flex-1">
          <Search className="w-4 h-4 text-text-muted absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search conversation title or user..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full bg-surface border border-border rounded-lg pl-9 pr-4 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-crimson-600"
          />
        </div>
      </div>

      {/* Master View: Left Column (Chat Sessions List) & Right Column (Messages Thread) */}
      <div className="flex flex-col lg:flex-row gap-6 h-[650px]">
        {/* Chat List */}
        <div className="w-full lg:w-96 bg-surface border border-border rounded-xl flex flex-col overflow-hidden shadow-sm">
          <div className="p-3 border-b border-border bg-surface-hover/50 text-xs font-semibold uppercase tracking-wider text-text-secondary flex justify-between items-center">
            <span>
              {selectedUserId === 'all'
                ? `All Chats (${displayedChats.length})`
                : `${selectedUserObj?.username || 'User'} Chats (${displayedChats.length})`}
            </span>
            <span className="text-[10px] text-emerald-400 font-medium flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Live Sync
            </span>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
            {displayedChats.map(c => {
              const isSelected = selectedChat?.id === c.id || selectedChat?.session_id === c.session_id;
              const msgs = parseMessages(c.messages_json);
              const uname = c.username || c.user_id || 'Unknown';

              return (
                <button
                  key={c.id || c.session_id}
                  onClick={() => setSelectedChat(c)}
                  className={`w-full text-left p-3 rounded-lg border transition-all ${
                    isSelected
                      ? 'bg-surface-active border-crimson-500/80 shadow-sm'
                      : 'border-border/60 hover:bg-surface-hover hover:border-border'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded bg-crimson-600/15 text-crimson-400 border border-crimson-600/25">
                      <User className="w-2.5 h-2.5" /> {uname}
                    </span>
                    <span className="text-[10px] text-text-muted flex items-center gap-1">
                      <Clock className="w-2.5 h-2.5" />
                      {new Date(c.updated_at || c.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>

                  <div className="font-medium text-sm text-text-primary truncate">
                    {c.session_name || 'Untitled Chat'}
                  </div>

                  <div className="text-xs text-text-secondary flex items-center justify-between mt-1">
                    <span className="truncate">{msgs.length} message{msgs.length === 1 ? '' : 's'}</span>
                    <span className="text-[10px] text-text-muted">
                      {new Date(c.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </button>
              );
            })}

            {displayedChats.length === 0 && (
              <div className="p-8 text-center text-sm text-text-muted space-y-2">
                <MessageSquare className="w-8 h-8 mx-auto text-text-muted/40" />
                <p className="font-medium text-text-secondary">
                  {selectedUserId === 'all'
                    ? 'No user conversations recorded yet.'
                    : `No recorded chats for "${selectedUserObj?.username || 'this user'}" yet.`}
                </p>
                <p className="text-xs text-text-muted">
                  When this operator submits prompts in the Chat Workbench, their conversations will stream here in real-time.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Selected Chat Thread */}
        <div className="flex-1 bg-surface border border-border rounded-xl flex flex-col overflow-hidden shadow-sm">
          {selectedChat ? (
            <>
              {/* Thread Header */}
              <div className="p-4 border-b border-border bg-surface-hover/30 flex justify-between items-center">
                <div>
                  <h3 className="font-bold text-base text-text-primary">{selectedChat.session_name || 'Untitled Chat'}</h3>
                  <div className="flex items-center gap-3 text-xs text-text-secondary mt-0.5">
                    <span className="flex items-center gap-1">
                      <User className="w-3 h-3 text-crimson-400" />
                      User: <strong className="text-text-primary">{selectedChat.username || selectedChat.user_id}</strong>
                    </span>
                    <span>•</span>
                    <span>Created: {new Date(selectedChat.created_at).toLocaleString()}</span>
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteChat(selectedChat.session_id)}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 border border-rose-500/20 rounded-lg transition-colors"
                  title="Delete this recorded chat session"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Delete Chat</span>
                </button>
              </div>

              {/* Message History */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {parseMessages(selectedChat.messages_json).map((m: any, idx: number) => {
                  const isUser = m.role === 'user';
                  return (
                    <div
                      key={idx}
                      className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
                    >
                      <div className="text-[10px] font-semibold text-text-muted mb-1 px-1 flex items-center gap-1.5">
                        <span>{isUser ? (selectedChat.username || 'User') : (m.model || 'AI Assistant')}</span>
                        {m.timestamp && (
                          <span className="text-text-muted/60">
                            {new Date(m.timestamp).toLocaleTimeString()}
                          </span>
                        )}
                      </div>

                      <div
                        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                          isUser
                            ? 'bg-crimson-600 text-white rounded-tr-none shadow-sm'
                            : 'bg-surface-subtle text-text-primary border border-border rounded-tl-none'
                        }`}
                      >
                        {m.thinking && (
                          <div className="mb-3 p-2.5 rounded-lg bg-background/50 border border-border/50 text-xs text-text-secondary font-mono">
                            <div className="text-[10px] font-bold text-text-muted uppercase mb-1">Reasoning Process</div>
                            <div className="whitespace-pre-wrap">{m.thinking}</div>
                          </div>
                        )}
                        <div className="whitespace-pre-wrap">{m.content}</div>

                        {/* Deliverables / attachments if present */}
                        {m.attachments && m.attachments.length > 0 && (
                          <div className="mt-2.5 pt-2 border-t border-white/20 flex flex-wrap gap-1.5 text-xs">
                            {m.attachments.map((att: any, aIdx: number) => (
                              <span key={aIdx} className="px-2 py-0.5 rounded bg-black/20 flex items-center gap-1">
                                <FileText className="w-3 h-3" />
                                {typeof att === 'string' ? att : att.name}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-text-muted p-8 text-center">
              <MessageSquare className="w-12 h-12 text-text-muted/30 mb-3" />
              <p className="font-medium text-base text-text-secondary">Select a user conversation from the left</p>
              <p className="text-xs text-text-muted mt-1 max-w-sm">
                As Master Department Head, you have real-time visibility into all prompts, responses, and files.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
