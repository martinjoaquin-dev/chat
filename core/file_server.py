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
        
        # Variables para almacenar datos
        filename = None
        file_content = None
        signer_name = None
        signer_email = None
        size = 0
        
        # Leer todos los campos del multipart
        while True:
            field = await reader.next()
            if field is None:
                break
            
            if field.name == 'file':
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
                
                # Leer contenido del archivo
                file_chunks = []
                while True:
                    chunk = await field.read_chunk()
                    if not chunk:
                        break
                        
                    size += len(chunk)
                    if size > MAX_FILE_SIZE:
                        return web.json_response(
                            {'error': f'Archivo demasiado grande. Máximo: {MAX_FILE_SIZE} bytes'},
                            status=413
                        )
                    
                    # Convertir chunk a bytes si es bytearray
                    if isinstance(chunk, bytearray):
                        chunk = bytes(chunk)
                    file_chunks.append(chunk)
                
                # Convertir todos los chunks a bytes después de leerlos todos
                file_content = b''.join(file_chunks)
                
            elif field.name == 'signer_name':
                signer_name_bytes = await field.read()
                if signer_name_bytes:
                    # Convertir a string correctamente, manejando bytearray, bytes o string
                    if isinstance(signer_name_bytes, bytearray):
                        signer_name = signer_name_bytes.decode('utf-8')
                    elif isinstance(signer_name_bytes, bytes):
                        signer_name = signer_name_bytes.decode('utf-8')
                    else:
                        signer_name = str(signer_name_bytes)
                    
            elif field.name == 'signer_email':
                signer_email_bytes = await field.read()
                if signer_email_bytes:
                    # Convertir a string correctamente, manejando bytearray, bytes o string
                    if isinstance(signer_email_bytes, bytearray):
                        signer_email = signer_email_bytes.decode('utf-8')
                    elif isinstance(signer_email_bytes, bytes):
                        signer_email = signer_email_bytes.decode('utf-8')
                    else:
                        signer_email = str(signer_email_bytes)
        
        if not filename or file_content is None:
            return web.json_response(
                {'error': 'Campo "file" requerido'},
                status=400
            )
        
        # Guardar archivo original
        file_path = os.path.join(UPLOAD_DIR, filename)
        file_ext = Path(filename).suffix.lower()
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Firmar archivo con información del firmante
        signature_path = os.path.join(SIGNATURES_DIR, f"{Path(filename).stem}.sig.json")
        signed_file_path = None
        
        try:
            # Verificar que el archivo se guardó correctamente
            if not os.path.exists(file_path):
                return web.json_response(
                    {'error': 'Error al guardar archivo'},
                    status=500
                )
            
            if file_ext == '.txt':
                signed_file_path = signer.sign_txt_file(file_path, signature_path, signer_name=signer_name, signer_email=signer_email)
            elif file_ext == '.pdf':
                signed_file_path = signer.sign_pdf_file(file_path, signature_path, signer_name=signer_name, signer_email=signer_email)
            elif file_ext == '.zip':
                signed_file_path = signer.sign_zip_file(file_path, signature_path, signer_name=signer_name, signer_email=signer_email)
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            print(f"Error al firmar archivo: {error_traceback}")
            
            # Limpiar archivo si existe
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            
            # Extraer el mensaje de error más útil
            error_msg = str(e)
            if 'bytearray' in error_msg.lower() or 'JSON' in error_msg:
                error_msg = f'Error de serialización al firmar: {error_msg}. Detalles: {error_traceback[:200]}'
            
            return web.json_response(
                {'error': f'Error al firmar archivo: {error_msg}'},
                status=500
            )
        
        # Leer información de la firma
        try:
            with open(signature_path, 'r', encoding='utf-8') as f:
                signature_data = json.load(f)
        except Exception as e:
            print(f"Error al leer firma desde {signature_path}: {e}")
            signature_data = {}
        
        # Preparar respuesta con URL del archivo firmado si existe
        # Asegurar que todos los valores sean serializables
        response_data = {
            'success': True,
            'filename': str(filename),
            'size': int(size),
            'signature_path': str(signature_path),
            'signature': signature_data,  # Ya debería ser serializable (viene de JSON)
            'signer_name': str(signer_name or signature_data.get('signer_name', '') or ''),
            'signer_email': str(signer_email or signature_data.get('signer_email', '') or ''),
            'uploaded_at': str(datetime.now().isoformat())
        }
        
        # Si hay un archivo firmado, agregar su URL
        if signed_file_path and os.path.exists(signed_file_path):
            import urllib.parse
            signed_filename = os.path.basename(signed_file_path)
            # Codificar el nombre del archivo para URL (por si tiene caracteres especiales)
            encoded_filename = urllib.parse.quote(signed_filename, safe='')
            # Usar localhost para descarga desde el frontend (CORS)
            response_data['signed_file_url'] = str(f"http://localhost:{SERVER_PORT}/download/{encoded_filename}")
            response_data['signed_filename'] = str(signed_filename)
        
        # Verificar que todos los valores sean serializables antes de devolver
        def ensure_serializable(obj):
            """Asegura que un objeto sea serializable a JSON."""
            if isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            elif isinstance(obj, bytes):
                return obj.hex()
            elif isinstance(obj, bytearray):
                return bytes(obj).hex()
            elif isinstance(obj, dict):
                return {str(k): ensure_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [ensure_serializable(item) for item in obj]
            else:
                return str(obj)
        
        # Asegurar que la respuesta sea serializable
        serializable_response = ensure_serializable(response_data)
        
        return web.json_response(serializable_response)
        
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
    seen_files = set()  # Para evitar duplicados (archivos _signed)
    
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                # FILTRAR archivos _signed (solo mostrar el original)
                if filename.endswith('_signed.pdf') or filename.endswith('_signed.txt'):
                    continue
                
                # Obtener el nombre base (sin extensión)
                base_name = Path(filename).stem
                
                # Si ya procesamos este archivo base, saltarlo
                if base_name in seen_files:
                    continue
                
                stat = os.stat(file_path)
                
                # Verificar si existe firma para este archivo (usar nombre base)
                signature_path = os.path.join(SIGNATURES_DIR, f"{base_name}.sig.json")
                has_signature = os.path.exists(signature_path)
                
                # Verificar si existe versión firmada visible
                file_ext = Path(filename).suffix.lower()
                signed_filename = filename.replace(file_ext, f'_signed{file_ext}')
                signed_file_path = os.path.join(UPLOAD_DIR, signed_filename)
                has_signed_version = os.path.exists(signed_file_path)
                
                files.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'uploaded_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'signed': has_signature,
                    'has_signed_version': has_signed_version,
                    'signed_filename': signed_filename if has_signed_version else None
                })
                
                seen_files.add(base_name)
    
    # Ordenar por fecha de subida (más recientes primero)
    files.sort(key=lambda x: x['uploaded_at'], reverse=True)
    
    return web.json_response({
        'files': files,
        'count': len(files)
    })


async def download_file(request):
    """
    Endpoint para descargar archivos firmados.
    GET /download/{filename}
    """
    import urllib.parse
    
    filename = request.match_info.get('filename')
    
    if not filename:
        return web.json_response(
            {'error': 'Nombre de archivo requerido'},
            status=400
        )
    
    # Buscar el archivo comparando nombres decodificados
    # Los archivos pueden estar guardados con nombres codificados (%20) pero se buscan decodificados
    original_filename = filename
    decoded_filename = None
    
    try:
        decoded_filename = urllib.parse.unquote(filename)
    except Exception as e:
        print(f"Advertencia: Error al decodificar filename: {e}")
        decoded_filename = filename
    
    # Intentar buscar el archivo con ambos nombres
    file_path = None
    
    # Primero intentar con el nombre tal como viene (puede estar codificado)
    file_path_original = os.path.join(UPLOAD_DIR, original_filename)
    if os.path.exists(file_path_original):
        file_path = file_path_original
        filename = original_filename
        print(f"DEBUG: Archivo encontrado con nombre original (codificado): {filename}")
    # Si no existe, intentar con el nombre decodificado
    else:
        file_path_decoded = os.path.join(UPLOAD_DIR, decoded_filename)
        if os.path.exists(file_path_decoded):
            file_path = file_path_decoded
            filename = decoded_filename
            print(f"DEBUG: Archivo encontrado con nombre decodificado: {filename}")
        else:
            # Buscar en la lista de archivos disponibles comparando nombres decodificados
            available_files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
            
            # Buscar coincidencia comparando nombres decodificados
            for available_file in available_files:
                try:
                    # Decodificar el nombre del archivo disponible
                    decoded_available = urllib.parse.unquote(available_file)
                    
                    # Comparar nombres decodificados
                    if decoded_available == decoded_filename:
                        file_path = os.path.join(UPLOAD_DIR, available_file)
                        filename = available_file  # Usar el nombre real del archivo (codificado)
                        print(f"DEBUG: Archivo encontrado por coincidencia de nombre decodificado: {filename} (buscado: {decoded_filename})")
                        break
                except Exception as e:
                    # Si no se puede decodificar, comparar directamente
                    if available_file == decoded_filename or available_file == original_filename:
                        file_path = os.path.join(UPLOAD_DIR, available_file)
                        filename = available_file
                        print(f"DEBUG: Archivo encontrado por coincidencia exacta: {filename}")
                        break
    
    # Si aún no se encontró, mostrar error
    if not file_path or not os.path.exists(file_path):
        # Listar archivos disponibles para debug
        available_files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
        print(f"DEBUG: Archivo no encontrado. Buscado: '{original_filename}' o '{decoded_filename}'")
        print(f"DEBUG: Archivos disponibles: {available_files[:5]}")
        
        return web.json_response(
            {
                'error': 'Archivo no encontrado',
                'requested_file': original_filename,
                'requested_file_decoded': decoded_filename,
                'available_files': available_files[:10]  # Devolver primeros 10 para debug
            },
            status=404
        )
    
    # Verificar que no se salga del directorio permitido (seguridad)
    abs_upload_dir = os.path.abspath(UPLOAD_DIR)
    abs_file_path = os.path.abspath(file_path)
    
    if not abs_file_path.startswith(abs_upload_dir):
        return web.json_response(
            {'error': 'Acceso no permitido'},
            status=403
        )
    
    # Servir el archivo
    return web.FileResponse(
        path=file_path,
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    )


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
    app.router.add_get('/download/{filename}', download_file)
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

