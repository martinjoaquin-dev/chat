#!/usr/bin/env python3
"""
Endpoints OAuth 2.0 para integración con Google.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import sys
import os
import logging

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.oauth import (
    generate_pkce_pair,
    create_oauth_session,
    exchange_code_for_tokens,
    refresh_access_token,
    get_authorization_url,
    get_current_user,
    require_role,
    GOOGLE_REDIRECT_URI,
)

logger = logging.getLogger(__name__)

# Router para endpoints OAuth
oauth_router = APIRouter(prefix="/api/auth", tags=["OAuth"])


class GoogleLoginResponse(BaseModel):
    """Respuesta para el endpoint de login de Google."""
    authorization_url: str
    state: str


class TokenResponse(BaseModel):
    """Respuesta con tokens OAuth."""
    access_token: str
    id_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    scope: Optional[str] = None
    user_info: Optional[dict] = None


class RefreshTokenRequest(BaseModel):
    """Request para refrescar token."""
    refresh_token: str


@oauth_router.get("/google/login", response_model=GoogleLoginResponse)
async def google_login():
    """
    Inicia el flujo OAuth 2.0 con Google usando Authorization Code + PKCE.
    
    Genera un par PKCE (code_verifier, code_challenge) y devuelve la URL
    de autorización de Google junto con el state (session ID).
    
    Returns:
        authorization_url: URL para redirigir al usuario a Google
        state: Session ID para validar el callback
    """
    try:
        # Generar par PKCE
        code_verifier, code_challenge = generate_pkce_pair()
        
        # Crear sesión OAuth
        state = create_oauth_session(code_verifier, code_challenge)
        
        # Obtener URL de autorización
        authorization_url = await get_authorization_url(state)
        
        logger.info(f"Iniciando flujo OAuth con state: {state}")
        
        return GoogleLoginResponse(
            authorization_url=authorization_url,
            state=state
        )
        
    except Exception as e:
        logger.error(f"Error al iniciar flujo OAuth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar flujo OAuth: {str(e)}"
        )


@oauth_router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Código de autorización de Google"),
    state: Optional[str] = Query(None, description="State (session ID)"),
    error: Optional[str] = Query(None, description="Error de OAuth")
):
    """
    Callback de OAuth 2.0 de Google.
    
    Intercambia el código de autorización por tokens usando PKCE.
    Si hay un error, devuelve un JSON con el error.
    Si es exitoso, puede redirigir al frontend o devolver tokens en JSON.
    
    Args:
        code: Código de autorización
        state: Session ID para validar
        error: Error de OAuth (si existe)
        
    Returns:
        Redirige al frontend con tokens o devuelve error
    """
    try:
        # Verificar si hay error
        if error:
            logger.warning(f"Error en callback OAuth: {error}")
            # Redirigir al frontend con error
            return RedirectResponse(
                url=f"http://localhost:4200/auth-callback?error={error}",
                status_code=status.HTTP_302_FOUND
            )
        
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código de autorización no proporcionado"
            )
        
        if not state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State (session ID) no proporcionado"
            )
        
        # Intercambiar código por tokens
        token_response = await exchange_code_for_tokens(code, state)
        
        # Extraer tokens
        access_token = token_response.get("access_token")
        id_token = token_response.get("id_token")
        refresh_token = token_response.get("refresh_token")
        expires_in = token_response.get("expires_in")
        scope = token_response.get("scope")
        user_info = token_response.get("user_info", {})
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se recibió access_token de Google"
            )
        
        logger.info(f"Tokens obtenidos exitosamente para usuario: {user_info.get('email')}")
        
        # Redirigir al frontend con tokens en fragment (más seguro que query params)
        # El frontend extraerá los tokens del fragment
        from urllib.parse import urlencode
        
        fragment_params = {"access_token": access_token}
        
        if id_token:
            fragment_params["id_token"] = id_token
        
        if refresh_token:
            fragment_params["refresh_token"] = refresh_token
        
        if expires_in:
            fragment_params["expires_in"] = str(expires_in)
        
        if scope:
            fragment_params["scope"] = scope
        
        # Construir URL con fragment usando urlencode para codificar correctamente
        redirect_url = f"http://localhost:4200/auth-callback#{urlencode(fragment_params)}"
        
        logger.info(f"Redirigiendo al frontend con tokens en fragment")
        
        return RedirectResponse(
            url=redirect_url,
            status_code=status.HTTP_302_FOUND
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en callback OAuth: {e}")
        # Redirigir al frontend con error
        return RedirectResponse(
            url=f"http://localhost:4200/auth-callback?error={str(e)}",
            status_code=status.HTTP_302_FOUND
        )


@oauth_router.post("/google/callback", response_model=TokenResponse)
async def google_callback_post(
    code: str = Query(..., description="Código de autorización de Google"),
    state: Optional[str] = Query(None, description="State (session ID)"),
):
    """
    Callback POST de OAuth 2.0 de Google (alternativa JSON).
    
    Similar a google_callback pero devuelve tokens en JSON en lugar de redirigir.
    Útil para aplicaciones SPA que prefieren manejar tokens directamente.
    
    Args:
        code: Código de autorización
        state: Session ID para validar
        
    Returns:
        Tokens en formato JSON
    """
    try:
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código de autorización no proporcionado"
            )
        
        if not state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State (session ID) no proporcionado"
            )
        
        # Intercambiar código por tokens
        token_response = await exchange_code_for_tokens(code, state)
        
        return TokenResponse(
            access_token=token_response.get("access_token"),
            id_token=token_response.get("id_token"),
            refresh_token=token_response.get("refresh_token"),
            token_type=token_response.get("token_type", "Bearer"),
            expires_in=token_response.get("expires_in"),
            scope=token_response.get("scope"),
            user_info=token_response.get("user_info")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en callback POST OAuth: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener tokens: {str(e)}"
        )


@oauth_router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresca un access_token usando un refresh_token.
    
    Args:
        request: Refresh token request
        
    Returns:
        Nuevos tokens
    """
    try:
        if not request.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token no proporcionado"
            )
        
        # Refrescar token
        token_response = await refresh_access_token(request.refresh_token)
        
        return TokenResponse(
            access_token=token_response.get("access_token"),
            id_token=token_response.get("id_token"),
            refresh_token=token_response.get("refresh_token", request.refresh_token),  # Mantener el mismo si no se proporciona uno nuevo
            token_type=token_response.get("token_type", "Bearer"),
            expires_in=token_response.get("expires_in"),
            scope=token_response.get("scope")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al refrescar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al refrescar token: {str(e)}"
        )


@oauth_router.get("/oauth/me")
async def get_oauth_user_info(current_user: dict = Depends(get_current_user)):
    """
    Obtiene información del usuario actual autenticado con OAuth.
    
    Args:
        current_user: Usuario actual (obtenido del token)
        
    Returns:
        Información del usuario
    """
    return {
        "email": current_user.get("email"),
        "sub": current_user.get("sub"),
        "name": current_user.get("name"),
        "picture": current_user.get("picture"),
        "email_verified": current_user.get("email_verified", False),
        "role": current_user.get("role", "user")
    }

