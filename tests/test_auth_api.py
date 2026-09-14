"""
Integration tests for Authentication and Admin Dashboard API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from orchestrator.main import app
from orchestrator.auth.database import AuthDatabase

client = TestClient(app)
auth_db = AuthDatabase()

def test_health_public():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_protected_endpoint_without_token():
    res = client.get("/v1/models")
    assert res.status_code == 401
    assert "authorization token" in res.json().get("detail", "").lower()

def test_login_invalid_credentials():
    res = client.post("/v1/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert res.status_code == 401

def test_login_success_admin():
    res = client.post("/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "admin"
    assert "must_change_password" in data["user"]

def test_protected_endpoint_with_admin_token():
    # Login
    login_res = client.post("/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = login_res.json()["access_token"]
    
    # Access protected route
    res = client.get("/v1/models", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "models" in res.json()

def test_admin_dashboard():
    login_res = client.post("/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = login_res.json()["access_token"]

    res = client.get("/v1/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "total_users" in data
    assert "active_sessions" in data

def test_create_and_authenticate_standard_user():
    import uuid
    uname = f"user_{uuid.uuid4().hex[:6]}"
    # Login as admin
    admin_login = client.post("/v1/auth/login", json={"username": "admin", "password": "admin123"})
    admin_token = admin_login.json()["access_token"]

    try:
        # Create a new standard user
        new_user_payload = {
            "username": uname,
            "password": "Password123!",
            "email": f"{uname}@workbench.local",
            "role": "user"
        }
        create_res = client.post("/v1/admin/users", json=new_user_payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert create_res.status_code == 200

        # Login as new user
        user_login = client.post("/v1/auth/login", json={"username": uname, "password": "Password123!"})
        assert user_login.status_code == 200
        user_token = user_login.json()["access_token"]
        assert user_login.json()["user"]["role"] == "user"

        # User should be able to access general protected endpoints
        me_res = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {user_token}"})
        assert me_res.status_code == 200
        assert me_res.json()["username"] == uname

        # Standard user MUST NOT be allowed to access admin endpoints (403 Forbidden)
        admin_res = client.get("/v1/admin/users", headers={"Authorization": f"Bearer {user_token}"})
        assert admin_res.status_code == 403
        assert "Admin access required" in admin_res.json()["detail"]
    finally:
        u_record = auth_db.get_user_by_username(uname)
        if u_record:
            auth_db.purge_user(u_record["id"])

def test_active_sessions_and_history():
    admin_login = client.post("/v1/auth/login", json={"username": "admin", "password": "admin123"})
    admin_token = admin_login.json()["access_token"]

    sessions_res = client.get("/v1/admin/sessions", headers={"Authorization": f"Bearer {admin_token}"})
    assert sessions_res.status_code == 200
    assert isinstance(sessions_res.json(), list)

    history_res = client.get("/v1/admin/login-history", headers={"Authorization": f"Bearer {admin_token}"})
    assert history_res.status_code == 200
    assert isinstance(history_res.json(), list)

def test_refresh_token():
    admin_login = client.post("/v1/auth/login", json={"username": "admin", "password": "admin123"})
    refresh_token = admin_login.json()["refresh_token"]

    res = client.post("/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_change_password():
    import uuid
    uname = f"pwuser_{uuid.uuid4().hex[:6]}"
    admin_login = client.post("/v1/auth/login", json={"username": "admin", "password": "admin123"})
    admin_token = admin_login.json()["access_token"]

    try:
        client.post("/v1/admin/users", json={
            "username": uname,
            "password": "Password123!",
            "role": "user"
        }, headers={"Authorization": f"Bearer {admin_token}"})

        # Login as pwuser
        user_login = client.post("/v1/auth/login", json={"username": uname, "password": "Password123!"})
        assert user_login.status_code == 200
        token = user_login.json()["access_token"]

        # Change password
        change_res = client.put(
            "/v1/auth/change-password",
            json={"current_password": "Password123!", "new_password": "NewSecretPassword456!"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert change_res.status_code == 200

        # Old password should fail
        fail_login = client.post("/v1/auth/login", json={"username": uname, "password": "Password123!"})
        assert fail_login.status_code == 401

        # New password succeeds
        success_login = client.post("/v1/auth/login", json={"username": uname, "password": "NewSecretPassword456!"})
        assert success_login.status_code == 200
    finally:
        u_record = auth_db.get_user_by_username(uname)
        if u_record:
            auth_db.purge_user(u_record["id"])

def test_admin_usage_stats_and_chats():
    admin_login = client.post("/v1/auth/login", json={"username": "admin", "password": "admin123"})
    admin_token = admin_login.json()["access_token"]

    # Usage stats
    usage_res = client.get("/v1/admin/usage-stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert usage_res.status_code == 200
    assert isinstance(usage_res.json(), list)

    # User chats
    chats_res = client.get("/v1/admin/user-chats/any-user-id", headers={"Authorization": f"Bearer {admin_token}"})
    assert chats_res.status_code == 200
    assert isinstance(chats_res.json(), list)

def test_logout():
    user_login = client.post("/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = user_login.json()["access_token"]

    res = client.post("/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "success"
