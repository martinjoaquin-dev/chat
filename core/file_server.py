# file_server.py - Servidor para Subir y Firmar Archivos
"""
Servidor HTTP asíncrono para subir archivos y aplicar firmas digitales.
Diseñado para ejecutarse en AWS o máquina virtual.
"""

import asyncio
import aiohttp
from aiohttp import web
import os
import json
from pathlib import Path
from datetime import datetime
import sys
import os
# Agregar directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.digital_signature import DigitalSignature
from dotenv import load_dotenv

load_dotenv()

# Configuración desde variables de entorno
UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')
SIGNATURES_DIR = os.getenv('SIGNATURES_DIR', 'signatures')
PRIVATE_KEY_PATH = os.getenv('SIGNING_PRIVATE_KEY', 'signing_keys/signing_private_key.pem')
PUBLIC_KEY_PATH = os.getenv('SIGNING_PUBLIC_KEY', 'signing_keys/signing_public_key.pem')
SERVER_HOST = os.getenv('FILE_SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('FILE_SERVER_PORT', '8080'))
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '10485760'))  # 10MB default

# Crear directorios necesarios
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SIGNATURES_DIR, exist_ok=True)

# Inicializar firmador digital
signer = None
try:
    signer = DigitalSignature(PRIVATE_KEY_PATH, PUBLIC_KEY_PATH)
    print(f"Firmador digital inicializado con clave: {PRIVATE_KEY_PATH}")
except Exception as e:
    print(f"ADVERTENCIA: No se pudo cargar clave de firma: {e}")
    print("Genera claves con: python -c 'from digital_signature import generate_signing_key_pair; generate_signing_key_pair()'")


async def upload_file(request):
    """
    Endpoint para subir archivos.
    POST /upload
    """
    if not signer:
        return web.json_response(
            {'error': 'Servicio de firma no disponible'},
            status=503
        )
    
    try:
        reader = await request.multipart()
        field = await reader.next()
        
        if field.name != 'file':
            return web.json_response(
                {'error': 'Campo "file" requerido'},
                status=400
            )
        
        filename = field.filename
        if not filename:
            return web.json_response(
                {'error': 'Nombre de archivo requerido'},
                status=400
            )
        
        # Validar extensión
        file_ext = Path(filename).suffix.lower()
        allowed_extensions = ['.txt', '.pdf', '.zip']
        if file_ext not in allowed_extensions:
            return web.json_response(
                {'error': f'Extensión no permitida. Permitidas: {", ".join(allowed_extensions)}'},
                status=400
            )
        
        # Guardar archivo
        file_path = os.path.join(UPLOAD_DIR, filename)
        size = 0
        
        with open(file_path, 'wb') as f:
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    os.remove(file_path)
                    return web.json_response(
                        {'error': f'Archivo demasiado grande. Máximo: {MAX_FILE_SIZE} bytes'},
                        status=413
                    )
                f.write(chunk)
        
        # Firmar archivo
        signature_path = os.path.join(SIGNATURES_DIR, f"{Path(filename).stem}.sig.json")
        
        try:
            if file_ext == '.txt':
                signer.sign_txt_file(file_path, signature_path)
            elif file_ext == '.pdf':
                signer.sign_pdf_file(file_path, signature_path)
            elif file_ext == '.zip':
                signer.sign_zip_file(file_path, signature_path)
        except Exception as e:
            os.remove(file_path)
            return web.json_response(
                {'error': f'Error al firmar archivo: {str(e)}'},
                status=500
            )
        
        # Leer información de la firma
        with open(signature_path, 'r') as f:
            signature_data = json.load(f)
        
        return web.json_response({
            'success': True,
            'filename': filename,
            'size': size,
            'signature_path': signature_path,
            'signature': signature_data,
            'uploaded_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return web.json_response(
            {'error': f'Error al procesar archivo: {str(e)}'},
            status=500
        )


async def verify_file(request):
    """
    Endpoint para verificar firma de archivo.
    POST /verify
    """
    if not signer:
        return web.json_response(
            {'error': 'Servicio de verificación no disponible'},
            status=503
        )
    
    try:
        data = await request.json()
        filename = data.get('filename')
        signature_path = data.get('signature_path')
        
        if not filename:
            return web.json_response(
                {'error': 'Nombre de archivo requerido'},
                status=400
            )
        
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        if not os.path.exists(file_path):
            return web.json_response(
                {'error': 'Archivo no encontrado'},
                status=404
            )
        
        # Si no se proporciona signature_path, buscar en el directorio de firmas
        if not signature_path:
            signature_path = os.path.join(SIGNATURES_DIR, f"{Path(filename).stem}.sig.json")
        
        if not os.path.exists(signature_path):
            return web.json_response(
                {'error': 'Firma no encontrada'},
                status=404
            )
        
        # Verificar firma
        is_valid = signer.verify_file(file_path, signature_path)
        
        return web.json_response({
            'filename': filename,
            'signature_valid': is_valid,
            'verified_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return web.json_response(
            {'error': f'Error al verificar: {str(e)}'},
            status=500
        )


async def list_files(request):
    """
    Endpoint para listar archivos subidos.
    GET /files
    """
    files = []
    
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                
                # Verificar si existe firma para este archivo
                signature_path = os.path.join(SIGNATURES_DIR, f"{Path(filename).stem}.sig.json")
                has_signature = os.path.exists(signature_path)
                
                files.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'uploaded_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'signed': has_signature
                })
    
    return web.json_response({
        'files': files,
        'count': len(files)
    })


async def health_check(request):
    """
    Endpoint de salud del servidor.
    GET /health
    """
    return web.json_response({
        'status': 'healthy',
        'signer_available': signer is not None,
        'timestamp': datetime.now().isoformat()
    })


def create_app():
    """Crea la aplicación web."""
    app = web.Application()
    
    app.router.add_post('/upload', upload_file)
    app.router.add_post('/verify', verify_file)
    app.router.add_get('/files', list_files)
    app.router.add_get('/health', health_check)
    
    return app


async def main():
    """Función principal del servidor."""
    app = create_app()
    
    print(f"Servidor de archivos iniciando en {SERVER_HOST}:{SERVER_PORT}")
    print(f"Directorio de uploads: {UPLOAD_DIR}")
    print(f"Directorio de firmas: {SIGNATURES_DIR}")
    print(f"Tamaño máximo de archivo: {MAX_FILE_SIZE} bytes")
    
    if signer:
        print("Servicio de firma digital: ACTIVO")
    else:
        print("Servicio de firma digital: INACTIVO (genera claves primero)")
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, SERVER_HOST, SERVER_PORT)
    await site.start()
    
    print(f"\nServidor corriendo en http://{SERVER_HOST}:{SERVER_PORT}")
    print("Endpoints disponibles:")
    print("  POST /upload - Subir y firmar archivo")
    print("  POST /verify - Verificar firma de archivo")
    print("  GET  /files - Listar archivos subidos")
    print("  GET  /health - Estado del servidor")
    print("\nPresiona Ctrl+C para detener")
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\nDeteniendo servidor...")
    finally:
        await runner.cleanup()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServidor detenido")

