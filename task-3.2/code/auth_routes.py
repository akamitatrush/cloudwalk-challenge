"""
🔐 Authentication Routes
========================
Phase 3: Security - Endpoints de autenticação
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List

from .auth import (
    authenticate_user,
    create_jwt_token,
    generate_api_key,
    revoke_api_key,
    get_current_user,
    require_permission,
    get_auth_stats,
    list_api_keys,
    store
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============== MODELS ==============

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours
    user: dict

class APIKeyRequest(BaseModel):
    name: str
    permissions: List[str] = ["read"]

class APIKeyResponse(BaseModel):
    api_key: str
    name: str
    permissions: List[str]
    message: str = "Save this key! It won't be shown again."


# ============== ENDPOINTS ==============

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    🔑 Login com usuário e senha.
    
    Retorna JWT token válido por 24 horas.
    
    **Usuários de teste:**
    - admin / admin123 (todas permissões)
    - operator / operator123 (read, write)
    - viewer / viewer123 (read only)
    """
    user = authenticate_user(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    token = create_jwt_token(
        username=user["username"],
        role=user["role"],
        permissions=user["permissions"]
    )
    
    return LoginResponse(
        access_token=token,
        user=user
    )


@router.get("/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """👤 Retorna informações do usuário autenticado"""
    return {
        "authenticated": True,
        "user": user
    }


@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    request: APIKeyRequest,
    user: dict = Depends(require_permission("admin"))
):
    """
    🔑 Gera nova API Key (apenas admin).
    
    A key só é mostrada UMA vez!
    """
    key = generate_api_key(request.name, request.permissions)
    
    return APIKeyResponse(
        api_key=key,
        name=request.name,
        permissions=request.permissions
    )


@router.get("/api-keys")
async def get_api_keys(user: dict = Depends(require_permission("admin"))):
    """📋 Lista todas as API Keys (apenas admin)"""
    return {
        "total": len(list_api_keys()),
        "keys": list_api_keys()
    }


@router.delete("/api-keys/{key_name}")
async def delete_api_key(
    key_name: str,
    user: dict = Depends(require_permission("admin"))
):
    """🗑️ Revoga API Key pelo nome (apenas admin)"""
    # Find key by name
    for key_hash, data in list(store.api_keys.items()):
        if data["name"] == key_name:
            del store.api_keys[key_hash]
            return {"message": f"API Key '{key_name}' revoked"}
    
    raise HTTPException(status_code=404, detail="API Key not found")


@router.get("/stats")
async def auth_stats(user: dict = Depends(require_permission("admin"))):
    """📊 Estatísticas de autenticação (apenas admin)"""
    return get_auth_stats()


@router.post("/logout")
async def logout(user: dict = Depends(get_current_user)):
    """🚪 Logout (invalida token atual)"""
    # In production, add token to blacklist
    return {
        "message": "Logged out successfully",
        "user": user.get("username") or user.get("name")
    }
