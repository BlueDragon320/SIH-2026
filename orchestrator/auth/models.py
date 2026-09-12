from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserPublic(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    role: str
    is_active: bool
    created_at: str
    last_login: Optional[str] = None
    must_change_password: bool = False

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserPublic

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    role: str = "user"

class UserUpdate(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class TokenPayload(BaseModel):
    sub: str
    username: str
    role: str
    exp: int
    jti: str

class SessionInfo(BaseModel):
    session_id: str
    user_id: str
    username: str
    login_at: str
    last_active: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class DashboardStats(BaseModel):
    total_users: int
    active_sessions: int
    total_tasks_today: int
    total_tasks_all: int
    system_uptime_seconds: int

class LoginRecord(BaseModel):
    id: int
    user_id: str
    username: str
    login_at: str
    logout_at: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    duration_seconds: Optional[float] = None

class UsageStatsUser(BaseModel):
    user_id: str
    username: str
    task_count: int
    models_used: List[str]
    last_task_at: Optional[str] = None
