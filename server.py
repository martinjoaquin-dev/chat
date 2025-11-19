# server.py - Versión Asíncrona con Cifrado Híbrido y SSL/TLS
"""
Servidor de chat TCP asíncrono con cifrado híbrido (RSA + AES) y SSL/TLS.
Utiliza asyncio para manejar múltiples clientes de forma eficiente.
Variables de entorno reemplazan valores hardcodeados.
"""

import asyncio
import logging
from logging.handlers import RotatingFileHandler
import struct
import argparse
import os
import ssl
from datetime import datetime
from crypto_utils import HybridCrypto
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración desde variables de entorno
HOST = os.getenv('SERVER_HOST', '0.0.0.0')
PORT = int(os.getenv('SERVER_PORT', '9000'))
LOG_FILE = os.getenv('LOG_FILE', 'chat.log')
LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '5000000'))
LOG_BACKUPS = int(os.getenv('LOG_BACKUPS', '3'))
SSL_ENABLED = os.getenv('SSL_ENABLED', 'true').lower() == 'true'
SSL_CERT_FILE = os.getenv('SSL_CERT_FILE', 'certificates/server.crt')
SSL_KEY_FILE = os.getenv('SSL_KEY_FILE', 'certificates/server.key')

connected_clients = set()
log = None

def setup_logger(log_file=None, max_bytes=None, backups=None):
    """Configura el logger con rotación de archivos."""
    global log
    log_file = log_file or LOG_FILE
    max_bytes = max_bytes or LOG_MAX_BYTES
    backups = backups or LOG_BACKUPS
    
    log = logging.getLogger('chat')
    log.setLevel(logging.INFO)
    
    # Limpiar handlers existentes
    log.handlers.clear()
    
    file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backups)
    file_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
    log.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
    log.addHandler(console_handler)
    
    return log

def create_ssl_context():
    """
    Crea contexto SSL/TLS para el servidor.
    
    Returns:
        ssl.SSLContext o None si SSL está deshabilitado
    """
    if not SSL_ENABLED:
        return None
    
    try:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(SSL_CERT_FILE, SSL_KEY_FILE)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # Para desarrollo con self-signed
        return context
    except FileNotFoundError as e:
        print(f'ADVERTENCIA: Archivos SSL no encontrados: {e}')
        print('Ejecuta: python generate_ssl_cert.py para generar certificados')
        print('Continuando sin SSL...')
        return None
    except Exception as e:
        print(f'Error al cargar certificados SSL: {e}')
        print('Continuando sin SSL...')
        return None

async def exchange_keys(reader, writer, server_crypto):
    """
    Intercambia claves públicas RSA y establece la clave AES compartida.
    
    Args:
        reader: StreamReader para leer datos
        writer: StreamWriter para escribir datos
        server_crypto: Instancia de HybridCrypto del servidor
        
    Returns:
        bool: True si el intercambio fue exitoso
    """
    try:
        # 1. Enviar clave pública del servidor al cliente
        server_public_key = server_crypto.get_public_key_pem()
        key_len = len(server_public_key)
        writer.write(struct.pack('!I', key_len) + server_public_key)
        await writer.drain()
        
        # 2. Recibir clave pública del cliente
        raw_len = await reader.readexactly(4)
        client_key_len = struct.unpack('!I', raw_len)[0]
        client_public_key = await reader.readexactly(client_key_len)
        server_crypto.load_peer_public_key(client_public_key)
        
        # 3. Recibir clave AES cifrada con RSA
        raw_len = await reader.readexactly(4)
        encrypted_aes_key_len = struct.unpack('!I', raw_len)[0]
        encrypted_aes_key = await reader.readexactly(encrypted_aes_key_len)
        server_crypto.decrypt_and_set_aes_key(encrypted_aes_key)
        
        return True
    except Exception as e:
        print(f'Error en intercambio de claves: {e}')
        return False

async def handle_client(reader, writer):
    """
    Maneja la comunicación con un cliente conectado.
    
    Args:
        reader: StreamReader para leer datos del cliente
        writer: StreamWriter para escribir datos al cliente
    """
    addr = writer.get_extra_info('peername')
    client_id = f'{addr[0]}:{addr[1]}'
    connected_clients.add(writer)
    
    # Verificar si la conexión usa SSL
    ssl_context = writer.get_extra_info('sslcontext')
    ssl_info = "SSL/TLS" if ssl_context else "TCP"
    
    print(f'Cliente conectado: {client_id} ({ssl_info})')
    
    # Crear instancia de cifrado híbrido para este cliente
    crypto = HybridCrypto()
    
    try:
        # Intercambiar claves RSA y establecer clave AES
        print(f'Intercambiando claves con {client_id}...')
        if not await exchange_keys(reader, writer, crypto):
            print(f'Error en intercambio de claves con {client_id}')
            return
        
        print(f'Claves intercambiadas exitosamente con {client_id}')
        print(f'Cifrado hibrido (RSA + AES-256-GCM) activado para {client_id}')
        
        while True:
            # Leer longitud del mensaje (4 bytes)
            raw_len = await reader.readexactly(4)
            if not raw_len:
                break
            
            length = struct.unpack('!I', raw_len)[0]
            
            # Leer el payload completo (hash SHA256 + datos cifrados)
            full_payload = await reader.readexactly(length)
            
            if len(full_payload) == length:
                try:
                    import binascii
                    
                    # Extraer hash SHA256 (primeros 32 bytes) y datos cifrados
                    if length < 32:
                        print(f'[VALIDACION] Mensaje demasiado corto de {client_id}, descartado')
                        log.warning('%s | Mensaje descartado: demasiado corto (sin hash SHA256)', client_id)
                        continue
                    
                    received_hash_bytes = full_payload[0:32]
                    received_hash = received_hash_bytes.hex()
                    encrypted_data = full_payload[32:]
                    
                    print(f'Datos cifrados recibidos de {client_id}: {binascii.hexlify(encrypted_data[:50]).decode()}...')
                    print(f'Tamano recibido: {len(encrypted_data)} bytes')
                    print(f'Hash SHA256 recibido: {received_hash}')
                    
                    # Descifrar mensaje
                    plaintext = crypto.decrypt_message(encrypted_data)
                    
                    # Calcular hash SHA256 del mensaje descifrado
                    calculated_hash = crypto.hash_message(plaintext)
                    print(f'Hash SHA256 calculado: {calculated_hash}')
                    
                    # VALIDACION: Comparar hash recibido con hash calculado
                    if received_hash != calculated_hash:
                        print(f'[VALIDACION FALLIDA] Hash SHA256 no coincide de {client_id}')
                        print(f'  Hash recibido: {received_hash}')
                        print(f'  Hash calculado: {calculated_hash}')
                        print(f'  Mensaje descartado por integridad comprometida')
                        log.warning('%s | Mensaje descartado: Hash SHA256 no coincide | Recibido: %s | Calculado: %s', 
                                  client_id, received_hash, calculated_hash)
                        continue
                    
                    # Hash coincide, mensaje válido
                    print(f'[VALIDACION EXITOSA] Hash SHA256 verificado correctamente')
                    print(f'Mensaje descifrado: "{plaintext}"')
                    
                    # Registrar en log
                    log.info('%s | %s | Hash: %s', client_id, plaintext, calculated_hash)
                    
                except ValueError as e:
                    print(f'Error de descifrado de {client_id}: {e}')
                    log.warning('%s | Error de descifrado: %s', client_id, str(e))
                except Exception as e:
                    print(f'Error inesperado de {client_id}: {e}')
                    log.error('%s | Error inesperado: %s', client_id, str(e))
                    
    except asyncio.IncompleteReadError:
        # Cliente desconectado normalmente
        pass
    except Exception as e:
        print(f'Error en conexion con {client_id}: {e}')
        log.error('%s | Error de conexion: %s', client_id, str(e))
    finally:
        connected_clients.discard(writer)
        writer.close()
        await writer.wait_closed()
        print(f'Cliente desconectado: {client_id}')

async def main_server(host=None, port=None, log_file=None, max_bytes=None, backups=None, ssl_context=None):
    """
    Función principal del servidor asíncrono.
    
    Args:
        host: Dirección IP de escucha
        port: Puerto de escucha
        log_file: Nombre del archivo de log
        max_bytes: Tamaño máximo del archivo de log
        backups: Número de archivos de respaldo
        ssl_context: Contexto SSL/TLS (opcional)
    """
    host = host or HOST
    port = port or PORT
    
    setup_logger(log_file, max_bytes, backups)
    
    server = await asyncio.start_server(
        handle_client,
        host, port,
        ssl=ssl_context
    )
    
    addr = server.sockets[0].getsockname()
    protocol = "SSL/TLS" if ssl_context else "TCP"
    print(f'Servidor asincrono escuchando en {addr[0]}:{addr[1]} ({protocol})')
    print(f'Cifrado hibrido RSA + AES-256-GCM + HMAC + SHA256 activado')
    if ssl_context:
        print(f'SSL/TLS activado: {SSL_CERT_FILE}')
    else:
        print(f'SSL/TLS desactivado (conexion TCP sin cifrado de transporte)')
    print(f'Logs guardandose en: {log_file or LOG_FILE}')
    print(f'Modo asincrono: Manejo eficiente de multiples clientes')
    print('Presiona Ctrl+C para detener el servidor')
    
    async with server:
        try:
            await server.serve_forever()
        except KeyboardInterrupt:
            print('\nDeteniendo servidor...')
            # Cerrar todas las conexiones
            for writer in connected_clients.copy():
                writer.close()
                await writer.wait_closed()

def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(description='Servidor de chat TCP asíncrono con cifrado híbrido y SSL/TLS')
    parser.add_argument('--host', default=None, help=f'IP de escucha (default: {HOST} desde .env)')
    parser.add_argument('--port', type=int, default=None, help=f'Puerto de escucha (default: {PORT} desde .env)')
    parser.add_argument('--log-file', default=None, help=f'Archivo de log (default: {LOG_FILE} desde .env)')
    parser.add_argument('--max-bytes', type=int, default=None, help=f'Tamaño máximo del archivo de log (default: {LOG_MAX_BYTES} desde .env)')
    parser.add_argument('--backups', type=int, default=None, help=f'Número de archivos de respaldo (default: {LOG_BACKUPS} desde .env)')
    parser.add_argument('--no-ssl', action='store_true', help='Deshabilitar SSL/TLS (usar TCP sin cifrado de transporte)')
    
    args = parser.parse_args()
    
    # Crear contexto SSL si está habilitado
    ssl_context = None
    if not args.no_ssl and SSL_ENABLED:
        ssl_context = create_ssl_context()
    
    try:
        asyncio.run(main_server(
            args.host, 
            args.port, 
            args.log_file, 
            args.max_bytes, 
            args.backups,
            ssl_context
        ))
    except KeyboardInterrupt:
        print('\nServidor detenido')

if __name__ == '__main__':
    main()
