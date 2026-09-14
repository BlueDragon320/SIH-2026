from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .security import decode_token
from jose import JWTError
import traceback

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, auth_db):
        super().__init__(app)
        self.whitelist = [
            "/health",
            "/v1/hardware-status",
            "/v1/network-status",
            "/v1/auth/login",
            "/v1/auth/refresh",
            "/docs",
            "/openapi.json",
            "/redoc"
        ]

    async def dispatch(self, request: Request, call_next):
        if (
            request.url.path in self.whitelist
            or request.url.path.startswith("/v1/workspace/download")
            or request.method == "OPTIONS"
        ):
            return await call_next(request)
            
        auth_header = request.headers.get("Authorization")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        elif request.query_params.get("token"):
            token = request.query_params.get("token")
            
        if not token:
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid authorization token"})
        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                return JSONResponse(status_code=401, content={"detail": "Invalid token type"})
                
            request.state.user = {
                "user_id": payload.get("sub"),
                "username": payload.get("username"),
                "role": payload.get("role"),
                "jti": payload.get("jti")
            }
            
            # Optionally update session activity if needed, requires session_id which might need a lookup or inclusion in token
            
        except JWTError:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})
            
        return await call_next(request)
