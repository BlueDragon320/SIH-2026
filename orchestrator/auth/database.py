import os
import sqlite3
import uuid
from datetime import datetime, timezone
import json
from .security import hash_password

class AuthDatabase:
    def __init__(self, db_path="/home/blue/SIH/data/auth.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        self._ensure_default_admin()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE,
                    email TEXT,
                    hashed_password TEXT,
                    role TEXT DEFAULT 'user',
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT,
                    last_login TEXT,
                    must_change_password INTEGER DEFAULT 0
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    token_jti TEXT,
                    login_at TEXT,
                    last_active TEXT,
                    logout_at TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS login_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    username TEXT,
                    login_at TEXT,
                    logout_at TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    duration_seconds REAL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    username TEXT,
                    session_id TEXT UNIQUE,
                    session_name TEXT,
                    messages_json TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            try:
                cursor.execute("ALTER TABLE user_chats ADD COLUMN username TEXT")
            except Exception:
                pass
            conn.commit()

    def _ensure_default_admin(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE role = 'admin'")
            if not cursor.fetchone():
                admin_id = str(uuid.uuid4())
                hashed_pw = hash_password("admin123")
                now_str = datetime.now(timezone.utc).isoformat()
                cursor.execute('''
                    INSERT INTO users (id, username, email, hashed_password, role, is_active, created_at, must_change_password)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (admin_id, "admin", "admin@example.com", hashed_pw, "admin", 1, now_str, 0))
                conn.commit()

    def create_user(self, username, password, role="user", email=None):
        user_id = str(uuid.uuid4())
        hashed_pw = hash_password(password)
        now_str = datetime.now(timezone.utc).isoformat()
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (id, username, email, hashed_password, role, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, username, email, hashed_pw, role, 1, now_str))
                conn.commit()
                return self.get_user_by_id(user_id)
        except sqlite3.IntegrityError:
            return None

    def get_user_by_username(self, username):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_id(self, user_id):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_user(self, user_id, **kwargs):
        if not kwargs:
            return True
        fields = []
        values = []
        for k, v in kwargs.items():
            if k == 'password':
                fields.append("hashed_password = ?")
                values.append(hash_password(v))
            elif k in ['email', 'role', 'is_active', 'last_login', 'must_change_password']:
                fields.append(f"{k} = ?")
                values.append(v)
        
        if not fields:
            return True
            
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(values))
            conn.commit()
            return cursor.rowcount > 0

    def delete_user(self, user_id):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0

    def list_users(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            return [dict(row) for row in cursor.fetchall()]

    def create_session(self, user_id, token_jti, ip, user_agent):
        session_id = str(uuid.uuid4())
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (session_id, user_id, token_jti, login_at, last_active, ip_address, user_agent, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, user_id, token_jti, now_str, now_str, ip, user_agent, 1))
            
            user = self.get_user_by_id(user_id)
            username = user['username'] if user else 'unknown'
            
            cursor.execute('''
                INSERT INTO login_history (user_id, username, login_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, now_str, ip, user_agent))
            conn.commit()
        return session_id

    def update_session_activity(self, session_id):
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE sessions SET last_active = ? WHERE session_id = ?", (now_str, session_id))
            conn.commit()

    def end_session(self, session_id):
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT login_at FROM sessions WHERE session_id = ?", (session_id,))
            session = cursor.fetchone()
            if session:
                login_at = datetime.fromisoformat(session['login_at'])
                duration = (datetime.now(timezone.utc) - login_at).total_seconds()
            else:
                duration = 0
                
            cursor.execute("UPDATE sessions SET is_active = 0, logout_at = ? WHERE session_id = ?", (now_str, session_id))
            cursor.execute("UPDATE login_history SET logout_at = ?, duration_seconds = ? WHERE user_id = (SELECT user_id FROM sessions WHERE session_id = ?) AND logout_at IS NULL", (now_str, duration, session_id))
            conn.commit()

    def invalidate_sessions_by_jti(self, jti):
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE sessions SET is_active = 0, logout_at = ? WHERE token_jti = ?", (now_str, jti))
            conn.commit()

    def get_active_sessions(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.session_id, s.user_id, 
                       COALESCE(u.username, s.user_id) as username,
                       s.login_at, s.last_active, s.logout_at,
                       s.ip_address, s.user_agent, s.is_active
                FROM sessions s
                LEFT JOIN users u ON s.user_id = u.id
                WHERE s.is_active = 1
                ORDER BY s.login_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_session(self, session_id):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_login_history(self, limit=50, user_id=None):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SELECT * FROM login_history WHERE user_id = ? ORDER BY login_at DESC LIMIT ?", (user_id, limit))
            else:
                cursor.execute("SELECT * FROM login_history ORDER BY login_at DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def force_end_session(self, session_id):
        self.end_session(session_id)
        
    def save_user_chat(self, user_id, session_id, session_name, messages_json, username=None):
        if not username:
            with self._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT username FROM users WHERE id = ? OR username = ?", (user_id, user_id))
                row = cur.fetchone()
                username = row[0] if row else str(user_id)

        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_chats (user_id, username, session_id, session_name, messages_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    user_id=excluded.user_id,
                    username=excluded.username,
                    session_name=excluded.session_name,
                    messages_json=excluded.messages_json,
                    updated_at=excluded.updated_at
            ''', (user_id, username, session_id, session_name, messages_json, now_str, now_str))
            conn.commit()

        # Dual Persistence: Also write formatted JSON file to disk
        try:
            chats_dir = os.path.join(os.path.dirname(self.db_path), "user_chats", str(username))
            os.makedirs(chats_dir, exist_ok=True)
            json_file = os.path.join(chats_dir, f"{session_id}.json")
            parsed_msgs = json.loads(messages_json) if isinstance(messages_json, str) else messages_json
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump({
                    "session_id": session_id,
                    "session_name": session_name,
                    "user_id": user_id,
                    "username": username,
                    "messages": parsed_msgs,
                    "created_at": now_str,
                    "updated_at": now_str
                }, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def delete_user_chat(self, session_id, user_id=None):
        username = None
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SELECT username FROM user_chats WHERE session_id = ? AND (user_id = ? OR username = ?)", (session_id, user_id, user_id))
                row = cursor.fetchone()
                if row:
                    username = row['username']
                cursor.execute("DELETE FROM user_chats WHERE session_id = ? AND (user_id = ? OR username = ?)", (session_id, user_id, user_id))
            else:
                cursor.execute("SELECT username FROM user_chats WHERE session_id = ?", (session_id,))
                row = cursor.fetchone()
                if row:
                    username = row['username']
                cursor.execute("DELETE FROM user_chats WHERE session_id = ?", (session_id,))
            conn.commit()

        if username:
            try:
                json_file = os.path.join(os.path.dirname(self.db_path), "user_chats", str(username), f"{session_id}.json")
                if os.path.exists(json_file):
                    os.remove(json_file)
            except Exception:
                pass

    def get_user_chats(self, user_id):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT uc.id, uc.user_id,
                       COALESCE(uc.username, u.username, uc.user_id) as username,
                       uc.session_id, uc.session_name, uc.messages_json, uc.created_at, uc.updated_at
                FROM user_chats uc
                LEFT JOIN users u ON uc.user_id = u.id OR uc.username = u.username
                WHERE uc.user_id = ? 
                   OR uc.username = ? 
                   OR uc.user_id IN (SELECT id FROM users WHERE username = ? OR id = ?)
                   OR uc.username IN (SELECT username FROM users WHERE id = ? OR username = ?)
                ORDER BY uc.updated_at DESC
            """, (user_id, user_id, user_id, user_id, user_id, user_id))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_chats_for_admin(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT uc.id, uc.user_id,
                       COALESCE(uc.username, u.username, uc.user_id) as username,
                       uc.session_id, uc.session_name, uc.messages_json, uc.created_at, uc.updated_at
                FROM user_chats uc
                LEFT JOIN users u ON uc.user_id = u.id OR uc.username = u.username
                ORDER BY uc.updated_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_dashboard_stats(self, tasks_db_path):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE is_active = 1")
            active_sessions = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM user_chats")
            total_user_chats = cursor.fetchone()[0]
            
        total_tasks_today = 0
        total_tasks_all = 0
        
        try:
            if os.path.exists(tasks_db_path):
                import sqlite3 as sqlite3_tasks
                with sqlite3_tasks.connect(tasks_db_path) as tasks_conn:
                    tasks_cursor = tasks_conn.cursor()
                    tasks_cursor.execute("SELECT COUNT(*) FROM tasks")
                    total_tasks_all = tasks_cursor.fetchone()[0]
                    
                    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                    tasks_cursor.execute("SELECT COUNT(*) FROM tasks WHERE created_at LIKE ?", (today + "%",))
                    total_tasks_today = tasks_cursor.fetchone()[0]
        except Exception:
            pass
            
        # Real system uptime
        try:
            with open('/proc/uptime', 'r') as f:
                system_uptime_seconds = int(float(f.read().split()[0]))
        except Exception:
            system_uptime_seconds = 0
            
        return {
            "total_users": total_users,
            "active_sessions": active_sessions,
            "total_tasks_today": total_tasks_today,
            "total_tasks_all": total_tasks_all,
            "total_user_chats": total_user_chats,
            "system_uptime_seconds": system_uptime_seconds
        }
