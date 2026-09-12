import { AuthUser, LoginResponse } from '../types/admin';
import { apiClient } from './apiClient';

const API_BASE = '/api/v1/auth';

export const authApi = {
  async login(username: string, password: string) {
    const res = await fetch(API_BASE + '/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) {
      let errMsg = 'Invalid username or password';
      try {
        const errJson = await res.json();
        errMsg = errJson.detail || errJson.message || errMsg;
      } catch {}
      throw new Error(errMsg);
    }
    const data: LoginResponse = await res.json();
    localStorage.setItem('wb_access_token', data.access_token);
    localStorage.setItem('wb_refresh_token', data.refresh_token);
    return data;
  },

  async refreshToken(refreshToken: string) {
    const res = await fetch(API_BASE + '/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    if (!res.ok) throw new Error('Refresh failed');
    const data = await res.json();
    if (data.access_token) {
      localStorage.setItem('wb_access_token', data.access_token);
    }
    return data;
  },

  logout() {
    localStorage.removeItem('wb_access_token');
    localStorage.removeItem('wb_refresh_token');
  },

  async getMe(): Promise<AuthUser> {
    const token = localStorage.getItem('wb_access_token');
    if (!token) throw new Error('No token');
    const res = await fetch(API_BASE + '/me', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    if (!res.ok) throw new Error('Failed to get user');
    return res.json();
  },

  async changePassword(currentPassword: string, newPassword: string) {
    const token = localStorage.getItem('wb_access_token');
    const res = await fetch(API_BASE + '/change-password', {
      method: 'POST',
      headers: { 
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
    });
    if (!res.ok) {
      let errMsg = 'Failed to change password';
      try {
        const errJson = await res.json();
        errMsg = errJson.detail || errMsg;
      } catch {}
      throw new Error(errMsg);
    }
  }
};
