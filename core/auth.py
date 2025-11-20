#!/usr/bin/env python3
"""
Módulo de autenticación con usuarios estáticos.
"""

# Base de datos de usuarios estáticos
# Formato: username: password
USERS_DB = {
    "admin": "admin123",
    "usuario1": "password1",
    "usuario2": "password2",
    "test": "test123",
    "demo": "demo123"
}

def authenticate(username: str, password: str) -> bool:
    """
    Autentica un usuario con credenciales estáticas.
    
    Args:
        username: Nombre de usuario
        password: Contraseña
        
    Returns:
        True si las credenciales son válidas, False en caso contrario
    """
    if not username or not password:
        return False
    
    # Verificar si el usuario existe y la contraseña coincide
    stored_password = USERS_DB.get(username)
    if stored_password and stored_password == password:
        return True
    
    return False

def user_exists(username: str) -> bool:
    """
    Verifica si un usuario existe en la base de datos.
    
    Args:
        username: Nombre de usuario
        
    Returns:
        True si el usuario existe, False en caso contrario
    """
    return username in USERS_DB

def get_user_list() -> list:
    """
    Obtiene la lista de usuarios disponibles.
    
    Returns:
        Lista de nombres de usuario
    """
    return list(USERS_DB.keys())

def is_admin(username: str) -> bool:
    """
    Verifica si un usuario es administrador.
    
    Args:
        username: Nombre de usuario
        
    Returns:
        True si el usuario es admin, False en caso contrario
    """
    return username.lower() == "admin"

