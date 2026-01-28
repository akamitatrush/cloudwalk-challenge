"""
🔐 Authentication Module
========================
Phase 3: Security - Transaction Guardian

Features:
- JWT Token Authentication
- API Key Management
- Role-based Access Control
- Security Headers
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List

import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

# ============== CONFIGURATION ==============

JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

API_KEY_HEADER = "X-API-Key"

bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


# ============== STORAGE ==============

class SecurityStore:
    """Armazena API keys e tokens"""
    
    def __init__(self):
        self.api_keys: Dict[str, Dict] = {}
        self.revoked_tokens: set = set()
        self.users: Dict[str, Dict] = {
            "admin": {
                "password_hash": self._hash("admin123"),
                "role": "admin",
                "permissions": ["read", "write", "admin"]
            },
            "viewer": {
                "password_hash": self._hash("viewer123"),
                "role": "viewer", 
                "permissions": ["read"]
            },
            "operator": {
                "password_hash": self._hash("operator123"),
                "role": "operator",
                "permissions": ["read", "write"]
            }
        }
        self._create_default_api_key()
    
    def _hash(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()
    
    def _create_default_api_key(self):
        default_key = "guardian-api-key-2024"
        key_hash = self._hash(default_key)
        self.api_keys[key_hash] = {
            "name": "default-key",
            "permissions": ["read", "write"],
            "created_at": datetime.now().isoformat(),
            "last_used": None
        }
        print(f"🔑 Default API Key: {default_key}")


store = SecurityStore()


# ============== JWT FUNCTIONS ==============

def create_jwt_token(username: str, role: str, permissions: List[str]) -> str:
    payload = {
        "sub": username,
        "role": role,
        "permissions": permissions,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> Optional[Dict]:
    try:
        if token in store.revoked_tokens:
            return None
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    user = store.users.get(username)
    if not user:
        return None
    if user["password_hash"] != store._hash(password):
        return None
    return {
        "username": username,
        "role": user["role"],
        "permissions": user["permissions"]
    }


# ============== API KEY FUNCTIONS ==============

def generate_api_key(name: str, permissions: List[str] = None) -> str:
    key = f"guardian-{secrets.token_hex(16)}"
    key_hash = store._hash(key)
    store.api_keys[key_hash] = {
        "name": name,
        "permissions": permissions or ["read"],
        "created_at": datetime.now().isoformat(),
        "last_used": None
    }
    return key


def validate_api_key(api_key: str) -> Optional[Dict]:
    key_hash = store._hash(api_key)
    key_data = store.api_keys.get(key_hash)
    if key_data:
        key_data["last_used"] = datetime.now().isoformat()
        return key_data
    return None


def revoke_api_key(api_key: str) -> bool:
    key_hash = store._hash(api_key)
    if key_hash in store.api_keys:
        del store.api_keys[key_hash]
        return True
    return False


# ============== FASTAPI DEPENDENCIES ==============

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    api_key: str = Security(api_key_header)
) -> Dict:
    """Valida JWT Bearer token OU API Key"""
    
    if credentials:
        payload = decode_jwt_token(credentials.credentials)
        if payload:
            return {
                "type": "jwt",
                "username": payload["sub"],
                "role": payload["role"],
                "permissions": payload["permissions"]
            }
    
    if api_key:
        key_data = validate_api_key(api_key)
        if key_data:
            return {
                "type": "api_key",
                "name": key_data["name"],
                "permissions": key_data["permissions"]
            }
    
    raise HTTPException(
        status_code=401,
        detail="Invalid authentication. Provide valid JWT token or API key.",
        headers={"WWW-Authenticate": "Bearer"}
    )


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    api_key: str = Security(api_key_header)
) -> Optional[Dict]:
    """Opcional - não falha se não autenticado"""
    try:
        return await get_current_user(credentials, api_key)
    except HTTPException:
        return None


def require_permission(permission: str):
    """Verifica permissão específica"""
    async def permission_checker(user: Dict = Depends(get_current_user)):
        if permission not in user.get("permissions", []):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied. Required: {permission}"
            )
        return user
    return permission_checker


# ============== UTILITY FUNCTIONS ==============

def get_auth_stats() -> Dict:
    return {
        "total_api_keys": len(store.api_keys),
        "total_users": len(store.users),
        "revoked_tokens": len(store.revoked_tokens),
        "jwt_expiration_hours": JWT_EXPIRATION_HOURS
    }


def list_api_keys() -> List[Dict]:
    return [
        {
            "name": data["name"],
            "permissions": data["permissions"],
            "created_at": data["created_at"],
            "last_used": data["last_used"]
        }
        for data in store.api_keys.values()
    ]
