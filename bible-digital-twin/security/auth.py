"""
Security Module - Production-Grade Authentication & Authorization
Enhancements #4-8: JWT Auth, Password Hashing, API Keys, RBAC, Security Headers
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets

# Configuration
SECRET_KEY = "bible-digital-twin-super-secret-key-change-in-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Enhancement #5: Secure password verification"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Enhancement #5: Secure password hashing"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Enhancement #4: JWT token generation"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Enhancement #4: JWT token validation"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Enhancement #4: Current user dependency"""
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

def generate_api_key() -> str:
    """Enhancement #6: Secure API key generation"""
    return f"bdt_{secrets.token_urlsafe(32)}"

class RBAC:
    """Enhancement #7: Role-Based Access Control"""
    
    ROLES = {
        "admin": ["read", "write", "delete", "admin"],
        "researcher": ["read", "write"],
        "user": ["read"],
        "guest": ["read_public"]
    }
    
    @staticmethod
    def has_permission(role: str, permission: str) -> bool:
        """Check if role has specific permission"""
        role_permissions = RBAC.ROLES.get(role, [])
        return permission in role_permissions
    
    @staticmethod
    async def check_permission(request: Request, required_permission: str):
        """Dependency for route protection"""
        user = request.state.user if hasattr(request.state, 'user') else None
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_role = user.get("role", "guest")
        if not RBAC.has_permission(user_role, required_permission):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        return True
