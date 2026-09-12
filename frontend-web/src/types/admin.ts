export interface AuthUser {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'user';
  is_active: boolean;
  created_at: string;
  last_login: string | null;
  must_change_password: boolean;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: AuthUser;
}

export interface DashboardStats {
  total_users: number;
  active_sessions: number;
  total_tasks_today: number;
  total_tasks_all: number;
  total_user_chats?: number;
  system_uptime_seconds: number;
}

export interface AdminSession {
  session_id: string;
  user_id: string;
  username?: string;
  login_at: string;
  last_active: string;
  logout_at?: string | null;
  ip_address: string;
  user_agent: string;
  is_active?: number;
}

export interface LoginRecord {
  id: number;
  user_id: string;
  username: string;
  login_at: string;
  logout_at: string | null;
  ip_address: string;
  user_agent: string;
  duration_seconds: number | null;
}

export interface UsageStatsUser {
  user_id: string;
  username?: string;
  task_count: number;
  models_used?: string[];
  last_task_at: string | null;
}

export interface UserChat {
  id: number;
  user_id: string;
  username?: string;
  session_id: string;
  session_name: string;
  messages_json: string;
  created_at: string;
  updated_at: string;
}

export interface AuditLogEntry {
  id: number;
  timestamp: string;
  task_id: string;
  event_type: string;
  model_used?: string;
  tool_name?: string;
  input_payload?: string;
  output_payload?: string;
  duration_ms?: number;
  airgap_verified?: boolean;
  user_id?: string;
}
