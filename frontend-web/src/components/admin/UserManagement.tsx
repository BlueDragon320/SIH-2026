import React, { useEffect, useState } from 'react';
import { adminApi } from '../../services/adminApi';
import { AuthUser } from '../../types/admin';
import { Plus, Edit2, Trash2, KeyRound, Search, X, Check, ShieldCheck, UserCheck } from 'lucide-react';

export function UserManagement() {
  const [users, setUsers] = useState<AuthUser[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Modals state
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingUser, setEditingUser] = useState<AuthUser | null>(null);

  // Form states for Add User
  const [newUsername, setNewUsername] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newRole, setNewRole] = useState<'user' | 'admin'>('user');

  // Form states for Edit User
  const [editRole, setEditRole] = useState<'user' | 'admin'>('user');
  const [editActive, setEditActive] = useState<boolean>(true);
  const [editResetPassword, setEditResetPassword] = useState('');

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await adminApi.getUsers();
      setUsers(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUsername.trim() || !newPassword.trim()) {
      setError('Username and password are required');
      return;
    }

    try {
      await adminApi.createUser({
        username: newUsername.trim(),
        email: newEmail.trim() || undefined,
        password: newPassword,
        role: newRole
      });
      setShowAddModal(false);
      setNewUsername('');
      setNewEmail('');
      setNewPassword('');
      setNewRole('user');
      setError(null);
      fetchUsers();
    } catch (err: any) {
      setError(err.message || 'Failed to create user');
    }
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;

    try {
      const payload: any = {
        role: editRole,
        is_active: editActive
      };
      if (editResetPassword.trim()) {
        payload.password = editResetPassword.trim();
      }

      await adminApi.updateUser(editingUser.id, payload);
      setEditingUser(null);
      setEditResetPassword('');
      setError(null);
      fetchUsers();
    } catch (err: any) {
      setError(err.message || 'Failed to update user');
    }
  };

  const handleDeleteUser = async (user: AuthUser) => {
    if (!confirm(`Are you sure you want to deactivate user "${user.username}"?`)) return;
    try {
      await adminApi.deleteUser(user.id);
      fetchUsers();
    } catch (err: any) {
      setError(err.message || 'Failed to delete user');
    }
  };

  const openEditModal = (user: AuthUser) => {
    setEditingUser(user);
    setEditRole(user.role);
    setEditActive(user.is_active);
    setEditResetPassword('');
  };

  const filteredUsers = users.filter(u =>
    u.username.toLowerCase().includes(search.toLowerCase()) ||
    (u.email && u.email.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-text-primary">User Management</h2>
          <p className="text-text-secondary text-sm">Create user credentials, assign roles, and manage access</p>
        </div>
        <button
          onClick={() => { setShowAddModal(true); setError(null); }}
          className="bg-crimson-600 hover:bg-crimson-500 px-4 py-2.5 rounded-lg text-white font-medium flex items-center gap-2 shadow-sm transition-colors text-sm"
        >
          <Plus className="w-4 h-4" /> Create User
        </button>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 px-4 py-3 rounded-lg text-sm flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)}><X className="w-4 h-4" /></button>
        </div>
      )}

      {/* Filter and Search */}
      <div className="flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-text-muted absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by username or email..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full bg-surface border border-border rounded-lg pl-9 pr-4 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-crimson-600"
          />
        </div>
        <span className="text-xs text-text-muted">Total: {users.length} user{users.length === 1 ? '' : 's'}</span>
      </div>

      {/* Users Table */}
      <div className="bg-surface border border-border rounded-xl overflow-hidden shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-surface-hover/80 text-text-secondary border-b border-border text-xs uppercase tracking-wider font-semibold">
            <tr>
              <th className="px-6 py-3.5">User</th>
              <th className="px-6 py-3.5">Role</th>
              <th className="px-6 py-3.5">Status</th>
              <th className="px-6 py-3.5">Created</th>
              <th className="px-6 py-3.5">Last Login</th>
              <th className="px-6 py-3.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border text-sm">
            {filteredUsers.map(u => (
              <tr key={u.id} className="hover:bg-surface-hover/40 transition-colors">
                <td className="px-6 py-4">
                  <div className="font-medium text-text-primary">{u.username}</div>
                  {u.email && <div className="text-xs text-text-muted">{u.email}</div>}
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                    u.role === 'admin'
                      ? 'bg-crimson-600/20 text-crimson-400 border border-crimson-600/30'
                      : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                  }`}>
                    {u.role === 'admin' ? <ShieldCheck className="w-3 h-3" /> : <UserCheck className="w-3 h-3" />}
                    {u.role}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                    u.is_active
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      : 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                  }`}>
                    {u.is_active ? 'Active' : 'Disabled'}
                  </span>
                </td>
                <td className="px-6 py-4 text-xs text-text-secondary">
                  {new Date(u.created_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 text-xs text-text-secondary">
                  {u.last_login ? new Date(u.last_login).toLocaleString() : 'Never'}
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => openEditModal(u)}
                      className="p-1.5 text-text-secondary hover:text-text-primary hover:bg-surface-hover rounded-md transition-colors"
                      title="Edit & Reset Password"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteUser(u)}
                      className="p-1.5 text-text-secondary hover:text-rose-400 hover:bg-surface-hover rounded-md transition-colors"
                      title="Deactivate User"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {filteredUsers.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-text-muted">
                  No users found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Add User Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-border rounded-xl w-full max-w-md p-6 space-y-5 shadow-2xl">
            <div className="flex justify-between items-center pb-3 border-b border-border">
              <h3 className="font-bold text-lg text-text-primary flex items-center gap-2">
                <Plus className="w-5 h-5 text-crimson-500" /> Create New User
              </h3>
              <button onClick={() => setShowAddModal(false)} className="text-text-muted hover:text-text-primary">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateUser} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-text-secondary uppercase mb-1.5">Username *</label>
                <input
                  type="text"
                  required
                  value={newUsername}
                  onChange={e => setNewUsername(e.target.value)}
                  placeholder="e.g. operator2"
                  className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-crimson-600"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-text-secondary uppercase mb-1.5">Password *</label>
                <input
                  type="password"
                  required
                  value={newPassword}
                  onChange={e => setNewPassword(e.target.value)}
                  placeholder="Set initial password"
                  className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-crimson-600"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-text-secondary uppercase mb-1.5">Email (optional)</label>
                <input
                  type="email"
                  value={newEmail}
                  onChange={e => setNewEmail(e.target.value)}
                  placeholder="user@workbench.local"
                  className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-crimson-600"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-text-secondary uppercase mb-1.5">Role & Access Level</label>
                <select
                  value={newRole}
                  onChange={e => setNewRole(e.target.value as 'user' | 'admin')}
                  className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-crimson-600"
                >
                  <option value="user">Standard User (Chat & Models)</option>
                  <option value="admin">Administrator (Full Dashboard Access)</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-sm text-text-secondary hover:text-text-primary rounded-lg hover:bg-surface-hover"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm bg-crimson-600 hover:bg-crimson-500 text-white font-medium rounded-lg shadow-sm"
                >
                  Save User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit User Modal */}
      {editingUser && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-border rounded-xl w-full max-w-md p-6 space-y-5 shadow-2xl">
            <div className="flex justify-between items-center pb-3 border-b border-border">
              <h3 className="font-bold text-lg text-text-primary flex items-center gap-2">
                <Edit2 className="w-5 h-5 text-crimson-500" /> Edit User: {editingUser.username}
              </h3>
              <button onClick={() => setEditingUser(null)} className="text-text-muted hover:text-text-primary">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpdateUser} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-text-secondary uppercase mb-1.5">Role</label>
                <select
                  value={editRole}
                  onChange={e => setEditRole(e.target.value as 'user' | 'admin')}
                  className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-crimson-600"
                >
                  <option value="user">Standard User</option>
                  <option value="admin">Administrator</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-text-secondary uppercase mb-1.5">Access Status</label>
                <select
                  value={editActive ? '1' : '0'}
                  onChange={e => setEditActive(e.target.value === '1')}
                  className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-crimson-600"
                >
                  <option value="1">Active (Permitted to Log In)</option>
                  <option value="0">Disabled (Login Blocked)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-text-secondary uppercase mb-1.5 flex items-center gap-1.5">
                  <KeyRound className="w-3.5 h-3.5 text-amber-400" /> Reset Password (leave blank to keep current)
                </label>
                <input
                  type="password"
                  value={editResetPassword}
                  onChange={e => setEditResetPassword(e.target.value)}
                  placeholder="Enter new password"
                  className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-crimson-600"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-border">
                <button
                  type="button"
                  onClick={() => setEditingUser(null)}
                  className="px-4 py-2 text-sm text-text-secondary hover:text-text-primary rounded-lg hover:bg-surface-hover"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm bg-crimson-600 hover:bg-crimson-500 text-white font-medium rounded-lg shadow-sm"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
