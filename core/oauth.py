#!/usr/bin/env python3
"""
Módulo de autenticación OAuth 2.0 con Google usando Authlib.
Implementa flujo Authorization Code con PKCE y verificación de tokens con JWKS.
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from urllib.parse import urlencode
import secrets
import hashlib
import base64
import jwt
from authlib.integrations.httpx_client import AsyncOAuth2Client
import httpx
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

logger = logging.getLogger(__name__)

# Configuración de OAuth 2.0
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:4200/auth-callback")
GOOGLE_SCOPES = os.getenv("GOOGLE_SCOPES", "openid email profile").split()
GOOGLE_DISCOVERY = os.getenv(
    "GOOGLE_DISCOVERY", 
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Almacenamiento de sesiones OAuth (en producción usar Redis)
oauth_sessions: Dict[str, Dict[str, Any]] = {}
refresh_tokens: Dict[str, Dict[str, Any]] = {}

# Security
security = HTTPBearer(auto_error=False)

# Cache para el discovery document y JWKS
_discovery_doc: Optional[Dict[str, Any]] = None
_jwks_client: Optional[Any] = None


async def get_discovery_document() -> Dict[str, Any]:
    """Obtiene el discovery document de Google y lo cachea."""
    global _discovery_doc
    
    if _discovery_doc is None:
        try:
            # Configurar cliente HTTP con verificación SSL
            # En desarrollo, podemos deshabilitar la verificación SSL si hay problemas
            verify_ssl = os.getenv("OAUTH_VERIFY_SSL", "true").lower() == "true"
            
            async with httpx.AsyncClient(verify=verify_ssl, timeout=10.0) as client:
                response = await client.get(GOOGLE_DISCOVERY)
                response.raise_for_status()
                _discovery_doc = response.json()
                logger.info("Discovery document cargado exitosamente")
        except httpx.HTTPError as e:
            logger.error(f"Error HTTP al cargar discovery document: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"No se pudo conectar con Google OAuth: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error al cargar discovery document: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error al conectar con Google OAuth: {str(e)}"
            )
    
    return _discovery_doc


async def get_jwks_client():
    """Obtiene el cliente JWKS para verificar tokens."""
    global _jwks_client
    
    if _jwks_client is None:
        try:
            from authlib.jose import jwt as authlib_jwt
            from authlib.jose.rfc7517.jwk import JsonWebKey
            
            discovery = await get_discovery_document()
            jwks_uri = discovery.get("jwks_uri")
            
            if not jwks_uri:
                raise ValueError("jwks_uri no encontrado en discovery document")
            
            # Configurar cliente HTTP con verificación SSL
            verify_ssl = os.getenv("OAUTH_VERIFY_SSL", "true").lower() == "true"
            
            async with httpx.AsyncClient(verify=verify_ssl, timeout=10.0) as client:
                response = await client.get(jwks_uri)
                response.raise_for_status()
                jwks = response.json()
            
            # Crear cliente JWKS
            _jwks_client = JsonWebKey.import_key_set(jwks)
            logger.info("JWKS cargado exitosamente")
        except Exception as e:
            logger.error(f"Error al cargar JWKS: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo cargar las claves públicas de Google"
            )
    
    return _jwks_client


async def verify_id_token(id_token: str) -> Dict[str, Any]:
    """
    Verifica un id_token de Google usando JWKS.
    
    Args:
        id_token: Token ID de Google
        
    Returns:
        Claims del token si es válido
        
    Raises:
        HTTPException: Si el token es inválido
    """
    try:
        discovery = await get_discovery_document()
        jwks_client = await get_jwks_client()
        
        # Obtener el issuer esperado
        issuer = discovery.get("issuer")
        
        # Decodificar y verificar el token
        from authlib.jose import jwt as authlib_jwt
        import time
        
        # Leeway para manejar diferencias de reloj entre servidores
        leeway = 300  # 5 minutos de margen
        
        try:
            # Intentar decodificar con validación completa
            claims = authlib_jwt.decode(
                id_token,
                jwks_client,
                claims_options={
                    "iss": {"essential": True, "value": issuer},
                    "exp": {"essential": True},
                    "aud": {"essential": True, "value": GOOGLE_CLIENT_ID},
                },
                claims_cls=None,
            )
        except Exception as decode_error:
            # Si falla por problemas de reloj (iat/nbf), intentar sin validar esos campos
            error_str = str(decode_error).lower()
            if "future" in error_str or "iat" in error_str or "issued" in error_str:
                logger.warning(f"Error de reloj detectado, usando validación flexible: {decode_error}")
                
                # Decodificar sin validar iat/nbf (permite diferencias de reloj)
                claims = authlib_jwt.decode(
                    id_token,
                    jwks_client,
                    claims_options={
                        "iss": {"essential": True, "value": issuer},
                        "exp": {"essential": False},  # Validar manualmente después
                        "aud": {"essential": True, "value": GOOGLE_CLIENT_ID},
                        "iat": {"essential": False},  # No validar iat (issued at)
                        "nbf": {"essential": False},  # No validar nbf (not before)
                    },
                    claims_cls=None,
                )
                
                # Validar exp manualmente con leeway
                exp = claims.get("exp")
                if exp and exp < (time.time() - leeway):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token expirado"
                    )
            else:
                # Si es otro tipo de error, relanzarlo
                raise
        
        # Validar exp manualmente si no se validó antes
        exp = claims.get("exp")
        if exp and exp < (time.time() - leeway):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        
        logger.info(f"Token verificado para usuario: {claims.get('email')}")
        return claims
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except (jwt.InvalidTokenError, Exception) as e:
        # Verificar si es un error de reloj (iat/nbf)
        error_str = str(e).lower()
        if "future" in error_str or "iat" in error_str or "issued" in error_str or "nbf" in error_str:
            logger.warning(f"Error de reloj detectado, intentando validación flexible: {e}")
            
            # Intentar decodificar sin validar iat/nbf
            try:
                from authlib.jose import jwt as authlib_jwt
                import time
                
                leeway = 300  # 5 minutos de margen
                
                discovery = await get_discovery_document()
                jwks_client = await get_jwks_client()
                issuer = discovery.get("issuer")
                
                claims = authlib_jwt.decode(
                    id_token,
                    jwks_client,
                    claims_options={
                        "iss": {"essential": True, "value": issuer},
                        "exp": {"essential": False},  # Validar manualmente
                        "aud": {"essential": True, "value": GOOGLE_CLIENT_ID},
                        "iat": {"essential": False},  # No validar iat
                        "nbf": {"essential": False},  # No validar nbf
                    },
                    claims_cls=None,
                )
                
                # Validar exp manualmente con leeway
                exp = claims.get("exp")
                if exp and exp < (time.time() - leeway):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token expirado"
                    )
                
                logger.info(f"Token verificado con validación flexible para usuario: {claims.get('email')}")
                return claims
                
            except Exception as retry_error:
                logger.error(f"Error al verificar token con validación flexible: {retry_error}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al verificar token: {str(retry_error)}"
                )
        else:
            # Si no es error de reloj, lanzar error normal
            logger.warning(f"Token inválido: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token inválido: {str(e)}"
            )


async def verify_access_token(access_token: str) -> Dict[str, Any]:
    """
    Verifica un access_token de Google.
    
    Args:
        access_token: Access token de Google
        
    Returns:
        Información del usuario si el token es válido
        
    Raises:
        HTTPException: Si el token es inválido
    """
    try:
        # Configurar cliente HTTP con verificación SSL
        verify_ssl = os.getenv("OAUTH_VERIFY_SSL", "true").lower() == "true"
        
        # Verificar el token con Google
        async with httpx.AsyncClient(verify=verify_ssl, timeout=10.0) as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token de acceso inválido"
                )
            
            user_info = response.json()
            logger.info(f"Access token verificado para usuario: {user_info.get('email')}")
            return user_info
            
    except httpx.HTTPError as e:
        logger.error(f"Error al verificar access token: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error al conectar con Google API"
        )


def generate_pkce_pair() -> tuple[str, str]:
    """
    Genera un par code_verifier y code_challenge para PKCE.
    
    Returns:
        Tupla (code_verifier, code_challenge)
    """
    # Generar code_verifier (43-128 caracteres)
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    # Generar code_challenge (SHA256 del code_verifier)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    
    return code_verifier, code_challenge


def create_oauth_session(code_verifier: str, code_challenge: str) -> str:
    """
    Crea una sesión OAuth y almacena el code_verifier.
    
    Args:
        code_verifier: Code verifier para PKCE
        code_challenge: Code challenge para PKCE
        
    Returns:
        Session ID
    """
    session_id = secrets.token_urlsafe(32)
    oauth_sessions[session_id] = {
        "code_verifier": code_verifier,
        "code_challenge": code_challenge,
        "created_at": datetime.now().isoformat()
    }
    logger.info(f"Sesión OAuth creada: {session_id}")
    return session_id


async def exchange_code_for_tokens(code: str, state: Optional[str] = None) -> Dict[str, Any]:
    """
    Intercambia un código de autorización por tokens usando PKCE.
    
    Args:
        code: Código de autorización
        state: Estado de la sesión OAuth
        
    Returns:
        Tokens (access_token, id_token, refresh_token, etc.)
        
    Raises:
        HTTPException: Si el intercambio falla
    """
    try:
        discovery = await get_discovery_document()
        token_endpoint = discovery.get("token_endpoint")
        
        if not token_endpoint:
            raise ValueError("token_endpoint no encontrado en discovery document")
        
        # Obtener code_verifier de la sesión
        if not state or state not in oauth_sessions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sesión OAuth inválida o expirada"
            )
        
        session_data = oauth_sessions[state]
        code_verifier = session_data["code_verifier"]
        
        # Configurar verificación SSL
        verify_ssl = os.getenv("OAUTH_VERIFY_SSL", "true").lower() == "true"
        
        # Crear cliente OAuth2 con Authlib
        async with AsyncOAuth2Client(
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            verify=verify_ssl
        ) as client:
            # Intercambiar código por tokens
            token_response = await client.fetch_token(
                token_endpoint,
                code=code,
                redirect_uri=GOOGLE_REDIRECT_URI,
                code_verifier=code_verifier,
            )
        
        # Limpiar sesión
        del oauth_sessions[state]
        
        # Verificar id_token
        id_token = token_response.get("id_token")
        if id_token:
            claims = await verify_id_token(id_token)
            token_response["user_info"] = claims
        
        # Guardar refresh_token si existe
        refresh_token = token_response.get("refresh_token")
        if refresh_token and id_token:
            email = claims.get("email")
            if email:
                refresh_tokens[email] = {
                    "refresh_token": refresh_token,
                    "access_token": token_response.get("access_token"),
                    "expires_at": (datetime.now() + timedelta(seconds=token_response.get("expires_in", 3600))).isoformat()
                }
        
        logger.info(f"Tokens obtenidos exitosamente para: {claims.get('email') if id_token else 'N/A'}")
        return token_response
        
    except Exception as e:
        logger.error(f"Error al intercambiar código por tokens: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener tokens: {str(e)}"
        )


async def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """
    Refresca un access_token usando un refresh_token.
    
    Args:
        refresh_token: Refresh token
        
    Returns:
        Nuevos tokens
    """
    try:
        discovery = await get_discovery_document()
        token_endpoint = discovery.get("token_endpoint")
        
        if not token_endpoint:
            raise ValueError("token_endpoint no encontrado en discovery document")
        
        # Configurar verificación SSL
        verify_ssl = os.getenv("OAUTH_VERIFY_SSL", "true").lower() == "true"
        
        async with AsyncOAuth2Client(
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            verify=verify_ssl
        ) as client:
            token_response = await client.refresh_token(
                token_endpoint,
                refresh_token=refresh_token,
            )
        
        logger.info("Token refrescado exitosamente")
        return token_response
        
    except Exception as e:
        logger.error(f"Error al refrescar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al refrescar token: {str(e)}"
        )


def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Extrae información del usuario desde un token almacenado.
    
    Args:
        token: Token de acceso o ID
        
    Returns:
        Información del usuario o None
    """
    # Buscar en refresh_tokens
    for email, token_data in refresh_tokens.items():
        if token_data.get("access_token") == token:
            return {
                "email": email,
                "access_token": token,
                "refresh_token": token_data.get("refresh_token")
            }
    
    # Si no está, intentar decodificar el token (sin verificar para obtener info básica)
    try:
        # Decodificar sin verificar para obtener claims básicos
        decoded = jwt.decode(token, options={"verify_signature": False})
        return {
            "email": decoded.get("email"),
            "sub": decoded.get("sub"),
            "name": decoded.get("name"),
            "picture": decoded.get("picture")
        }
    except:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Dependencia de FastAPI para obtener el usuario actual desde el token.
    
    Args:
        credentials: Credenciales HTTP Bearer
        
    Returns:
        Información del usuario
        
    Raises:
        HTTPException: Si no hay token o es inválido
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Intentar verificar como id_token primero
        try:
            claims = await verify_id_token(token)
            return {
                "email": claims.get("email"),
                "sub": claims.get("sub"),
                "name": claims.get("name"),
                "picture": claims.get("picture"),
                "email_verified": claims.get("email_verified", False)
            }
        except:
            # Si falla, intentar como access_token
            user_info = await verify_access_token(token)
            return {
                "email": user_info.get("email"),
                "sub": user_info.get("id"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
                "email_verified": user_info.get("verified_email", False)
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )


def require_role(allowed_roles: list[str]):
    """
    Crea una dependencia para requerir roles específicos.
    
    Args:
        allowed_roles: Lista de roles permitidos (ej: ['admin', 'user'])
        
    Returns:
        Dependencia de FastAPI
    """
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        email = current_user.get("email", "").lower()
        
        # Verificar si el usuario es admin (puedes extender esta lógica)
        # Por ahora, asumimos que admin es si el email contiene "admin" o está en una lista
        # En producción, esto debería venir de una base de datos
        from core.auth import is_admin
        
        user_role = "admin" if is_admin(email.split("@")[0]) else "user"
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de los siguientes roles: {allowed_roles}"
            )
        
        current_user["role"] = user_role
        return current_user
    
    return role_checker


# Función helper para obtener URL de autorización
async def get_authorization_url(state: str) -> str:
    """
    Genera la URL de autorización de Google.
    
    Args:
        state: Session ID (state)
        
    Returns:
        URL de autorización
    """
    discovery = await get_discovery_document()
    authorization_endpoint = discovery.get("authorization_endpoint")
    
    if not authorization_endpoint:
        raise ValueError("authorization_endpoint no encontrado en discovery document")
    
    if state not in oauth_sessions:
        raise ValueError(f"Sesión OAuth no encontrada: {state}")
    
    code_challenge = oauth_sessions[state]["code_challenge"]
    
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(GOOGLE_SCOPES),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "access_type": "offline",  # Para obtener refresh_token
        "prompt": "consent",  # Para forzar consentimiento y obtener refresh_token
    }
    
    query_string = urlencode(params)
    return f"{authorization_endpoint}?{query_string}"

