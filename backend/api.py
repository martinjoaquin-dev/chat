#!/usr/bin/env python3
"""
API REST con FastAPI para conectar el frontend Angular con el backend TCP.
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import sys
import os
import asyncio
import json
import logging
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.auth import authenticate, get_user_list, is_admin
from core.file_server import SERVER_HOST as FILE_SERVER_HOST, SERVER_PORT as FILE_SERVER_PORT
import aiohttp

# Si FILE_SERVER_HOST es 0.0.0.0, usar localhost para conexiones
FILE_SERVER_CONNECT_HOST = "localhost" if FILE_SERVER_HOST == "0.0.0.0" else FILE_SERVER_HOST

# Configuración
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CHAT_SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
CHAT_SERVER_PORT = int(os.getenv("SERVER_PORT", "8888"))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="Chat Seguro API",
    description="API REST para el sistema de chat seguro con cifrado híbrido",
    version="7.0.0"
)

# CORS para permitir conexiones desde Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:3000"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Incluir DELETE explícitamente
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Modelos Pydantic
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    username: Optional[str] = None
    message: Optional[str] = None

class MessageRequest(BaseModel):
    message: str
    recipient: Optional[str] = None

class MessageResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    timestamp: Optional[str] = None

class ServerStatus(BaseModel):
    running: bool
    host: str
    port: int
    clients_connected: int

class FileInfo(BaseModel):
    filename: str
    size: int
    uploaded_at: str
    signed: bool

class VerifyRequest(BaseModel):
    filename: str

# Almacenamiento en memoria (en producción usar Redis o similar)
active_sessions = {}
chat_connections = {}

# Almacenamiento de mensajes del chat
MESSAGE_HISTORY_FILE = os.getenv("MESSAGE_HISTORY_FILE", "chat_history.json")
MESSAGE_TTL_HOURS = int(os.getenv("MESSAGE_TTL_HOURS", "24"))  # 24 horas por defecto
MESSAGE_MAX_COUNT = int(os.getenv("MESSAGE_MAX_COUNT", "1000"))  # Máximo 1000 mensajes
message_history: List[dict] = []

def load_message_history():
    """Carga el historial de mensajes desde archivo JSON."""
    global message_history
    try:
        if os.path.exists(MESSAGE_HISTORY_FILE):
            with open(MESSAGE_HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                message_history = data.get('messages', [])
                logger.info(f"Historial cargado: {len(message_history)} mensajes")
    except Exception as e:
        logger.error(f"Error al cargar historial: {e}")
        message_history = []

def save_message_history():
    """Guarda el historial de mensajes en archivo JSON."""
    try:
        with open(MESSAGE_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump({'messages': message_history}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error al guardar historial: {e}")

def add_message_to_history(content: str, sender: str, recipient: Optional[str] = None):
    """Agrega un mensaje al historial."""
    global message_history
    message = {
        'id': f"{datetime.now().timestamp()}-{len(message_history)}",
        'content': content,
        'sender': sender,
        'recipient': recipient,
        'timestamp': datetime.now().isoformat(),
        'encrypted': True
    }
    message_history.append(message)
    
    # Limitar cantidad de mensajes
    if len(message_history) > MESSAGE_MAX_COUNT:
        message_history = message_history[-MESSAGE_MAX_COUNT:]
    
    # Guardar en archivo
    save_message_history()

def clean_old_messages():
    """Elimina mensajes más antiguos que el TTL configurado."""
    global message_history
    if MESSAGE_TTL_HOURS <= 0:
        return  # TTL deshabilitado
    
    from datetime import timedelta
    cutoff_time = datetime.now() - timedelta(hours=MESSAGE_TTL_HOURS)
    initial_count = len(message_history)
    
    message_history = [
        msg for msg in message_history
        if datetime.fromisoformat(msg['timestamp']) > cutoff_time
    ]
    
    removed = initial_count - len(message_history)
    if removed > 0:
        logger.info(f"Eliminados {removed} mensajes antiguos (TTL: {MESSAGE_TTL_HOURS}h)")
        save_message_history()

# Cargar historial al iniciar
load_message_history()

# Endpoints de Autenticación
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Autentica un usuario y devuelve un token de sesión."""
    if authenticate(credentials.username, credentials.password):
        # Generar token simple (en producción usar JWT)
        import secrets
        token = secrets.token_urlsafe(32)
        active_sessions[token] = {
            "username": credentials.username,
            "login_time": datetime.now().isoformat()
        }
        return LoginResponse(
            success=True,
            token=token,
            username=credentials.username
        )
    else:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

@app.post("/api/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Cierra la sesión del usuario."""
    token_value = credentials.credentials
    if token_value in active_sessions:
        del active_sessions[token_value]
    return {"success": True, "message": "Sesión cerrada"}

@app.get("/api/auth/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtiene información del usuario actual."""
    token_value = credentials.credentials
    if token_value in active_sessions:
        return {
            "username": active_sessions[token_value]["username"],
            "login_time": active_sessions[token_value]["login_time"]
        }
    raise HTTPException(status_code=401, detail="Token inválido")

# Endpoints de Chat
@app.get("/api/chat/status")
async def get_chat_status():
    """Obtiene el estado del servidor de chat."""
    # Aquí podrías verificar si el servidor TCP está corriendo
    return ServerStatus(
        running=True,  # Simplificado, en producción verificar proceso
        host=CHAT_SERVER_HOST,
        port=CHAT_SERVER_PORT,
        clients_connected=len(chat_connections)
    )

@app.post("/api/chat/send", response_model=MessageResponse)
async def send_message(message: MessageRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Envía un mensaje a través del servidor de chat."""
    token_value = credentials.credentials
    if token_value not in active_sessions:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    username = active_sessions[token_value]["username"]
    
    # Limpiar mensajes antiguos antes de agregar nuevo
    clean_old_messages()
    
    # Agregar mensaje al historial
    add_message_to_history(
        content=message.message,
        sender=username,
        recipient=message.recipient
    )
    
    # Aquí conectarías con el servidor TCP real para enviar el mensaje cifrado
    # Por ahora solo lo guardamos en el historial
    return MessageResponse(
        success=True,
        message=f"Mensaje enviado: {message.message}",
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/chat/messages")
async def get_messages(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtiene los mensajes del chat."""
    token_value = credentials.credentials
    if token_value not in active_sessions:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    # Limpiar mensajes antiguos antes de devolver
    clean_old_messages()
    
    # Devolver historial de mensajes
    return {
        "messages": message_history,
        "count": len(message_history)
    }

@app.delete("/api/chat/messages")
async def clear_chat_history(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Finaliza/reinicia el chat eliminando todo el historial. Solo disponible para admin."""
    token_value = credentials.credentials
    if token_value not in active_sessions:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    username = active_sessions[token_value]["username"]
    
    # Verificar que el usuario sea admin
    if not is_admin(username):
        raise HTTPException(status_code=403, detail="Solo los administradores pueden finalizar el chat")
    
    # Limpiar historial
    global message_history
    message_count = len(message_history)
    message_history = []
    
    # Eliminar archivo de historial si existe
    try:
        if os.path.exists(MESSAGE_HISTORY_FILE):
            os.remove(MESSAGE_HISTORY_FILE)
            logger.info(f"Archivo de historial eliminado: {MESSAGE_HISTORY_FILE}")
    except Exception as e:
        logger.error(f"Error al eliminar archivo de historial: {e}")
    
    logger.info(f"Chat finalizado por admin '{username}'. {message_count} mensajes eliminados.")
    
    return {
        "success": True,
        "message": f"Chat finalizado. {message_count} mensajes eliminados.",
        "count": 0
    }

# Endpoints de Archivos
@app.get("/api/files")
async def list_files(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Lista los archivos disponibles."""
    token_value = credentials.credentials
    if token_value not in active_sessions:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    # Conectar con el servidor de archivos
    try:
        async with aiohttp.ClientSession() as session:
            file_server_url = f"http://{FILE_SERVER_CONNECT_HOST}:{FILE_SERVER_PORT}/files"
            try:
                async with session.get(file_server_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        return {"files": [], "count": 0, "warning": f"Servidor de archivos respondió con código {response.status}"}
            except aiohttp.ClientConnectorError:
                return {"files": [], "count": 0, "warning": f"Servidor de archivos no disponible en {file_server_url}. Ejecuta 'python core/file_server.py'"}
            except asyncio.TimeoutError:
                return {"files": [], "count": 0, "warning": "Timeout al conectar con el servidor de archivos"}
    except Exception as e:
        return {"files": [], "count": 0, "error": str(e)}

@app.post("/api/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Sube un archivo al servidor."""
    token_value = credentials.credentials
    if token_value not in active_sessions:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    # Leer el archivo
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al leer archivo: {str(e)}")
    
    # Subir al servidor de archivos
    try:
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('file', contents, filename=file.filename, content_type=file.content_type or 'application/octet-stream')
            
            file_server_url = f"http://{FILE_SERVER_CONNECT_HOST}:{FILE_SERVER_PORT}/upload"
            
            try:
                logger.info(f"Intentando subir archivo a: {file_server_url}")
                async with session.post(file_server_url, data=data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response_text = await response.text()
                    logger.info(f"Respuesta del servidor de archivos: Status={response.status}, Body={response_text[:200]}")
                    
                    if response.status == 200:
                        try:
                            result = await response.json()
                            return result
                        except:
                            return {"success": True, "message": "Archivo subido exitosamente"}
                    else:
                        raise HTTPException(
                            status_code=response.status, 
                            detail=f"Error del servidor de archivos (código {response.status}): {response_text}"
                        )
            except aiohttp.ClientConnectorError as e:
                logger.error(f"Error de conexión al servidor de archivos: {str(e)}")
                raise HTTPException(
                    status_code=503, 
                    detail=f"Servidor de archivos no disponible en {file_server_url}. Asegúrate de que 'python core/file_server.py' esté corriendo en el puerto {FILE_SERVER_PORT}. Error: {str(e)}"
                )
            except asyncio.TimeoutError:
                logger.error(f"Timeout al conectar con el servidor de archivos: {file_server_url}")
                raise HTTPException(status_code=504, detail="Timeout al conectar con el servidor de archivos")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error en upload_file: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/api/files/verify")
async def verify_signature(
    request: VerifyRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verifica la firma digital de un archivo."""
    token_value = credentials.credentials
    if token_value not in active_sessions:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    filename = request.filename
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{FILE_SERVER_CONNECT_HOST}:{FILE_SERVER_PORT}/verify",
                json={"filename": filename}
            ) as response:
                if response.status == 200:
                    file_server_response = await response.json()
                    # Transformar la respuesta del servidor de archivos al formato esperado por el frontend
                    is_valid = file_server_response.get('signature_valid', False)
                    return {
                        "valid": is_valid,
                        "message": "Firma digital válida. El archivo no ha sido modificado." if is_valid 
                                  else "Firma digital inválida. El archivo puede haber sido alterado.",
                        "timestamp": file_server_response.get('verified_at', datetime.now().isoformat())
                    }
                else:
                    error_text = await response.text()
                    try:
                        error_json = await response.json()
                        error_message = error_json.get('error', 'Error al verificar firma')
                    except:
                        error_message = error_text or 'Error al verificar firma'
                    raise HTTPException(status_code=response.status, detail=error_message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al verificar firma: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al verificar firma: {str(e)}")

# Health check
@app.get("/api/health")
async def health_check():
    """Endpoint de salud del API."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "7.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)

