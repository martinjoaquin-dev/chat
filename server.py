# server.py - Versión Asíncrona
"""
Servidor de chat TCP asíncrono con cifrado simétrico.
Utiliza asyncio para manejar múltiples clientes de forma eficiente.
"""

import asyncio
import logging
from logging.handlers import RotatingFileHandler
import struct
import argparse
from datetime import datetime
from crypto_utils import SymmetricCrypto

# Configuración global
HOST, PORT = '0.0.0.0', 9000
connected_clients = set()
log = None

def setup_logger(log_file='chat.log', max_bytes=5_000_000, backups=3):
    """Configura el logger con rotación de archivos."""
    global log
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

async def handle_client(reader, writer, crypto):
    """
    Maneja la comunicación con un cliente conectado.
    
    Args:
        reader: StreamReader para leer datos del cliente
        writer: StreamWriter para escribir datos al cliente
        crypto: Instancia de SymmetricCrypto para descifrar mensajes
    """
    addr = writer.get_extra_info('peername')
    client_id = f'{addr[0]}:{addr[1]}'
    connected_clients.add(writer)
    
    print(f'✅ Cliente conectado: {client_id}')
    
    try:
        while True:
            # Leer longitud del mensaje (4 bytes)
            raw_len = await reader.readexactly(4)
            if not raw_len:
                break
            
            length = struct.unpack('!I', raw_len)[0]
            
            # Leer el payload completo
            encrypted_data = await reader.readexactly(length)
            
            if len(encrypted_data) == length:
                try:
                    import binascii
                    print(f'📡 Datos cifrados recibidos de {client_id}: {binascii.hexlify(encrypted_data[:50]).decode()}...')
                    print(f'📏 Tamaño recibido: {len(encrypted_data)} bytes')
                    
                    # Descifrar mensaje
                    plaintext = crypto.decrypt_message(encrypted_data)
                    
                    # Verificar hash SHA256 del mensaje descifrado
                    message_hash = crypto.hash_message(plaintext)
                    print(f'🔐 Hash SHA256 del mensaje: {message_hash}')
                    
                    # Registrar en log
                    log.info('%s | %s | Hash: %s', client_id, plaintext, message_hash)
                    print(f'🔓 Mensaje descifrado: "{plaintext}"')
                    
                except ValueError as e:
                    print(f'❌ Error de descifrado de {client_id}: {e}')
                    log.warning('%s | Error de descifrado: %s', client_id, str(e))
                except Exception as e:
                    print(f'❌ Error inesperado de {client_id}: {e}')
                    log.error('%s | Error inesperado: %s', client_id, str(e))
                    
    except asyncio.IncompleteReadError:
        # Cliente desconectado normalmente
        pass
    except Exception as e:
        print(f'❌ Error en conexión con {client_id}: {e}')
        log.error('%s | Error de conexión: %s', client_id, str(e))
    finally:
        connected_clients.discard(writer)
        writer.close()
        await writer.wait_closed()
        print(f'👋 Cliente desconectado: {client_id}')

async def main_server(host, port, crypto, log_file, max_bytes, backups):
    """
    Función principal del servidor asíncrono.
    
    Args:
        host: Dirección IP de escucha
        port: Puerto de escucha
        crypto: Instancia de SymmetricCrypto
        log_file: Nombre del archivo de log
        max_bytes: Tamaño máximo del archivo de log
        backups: Número de archivos de respaldo
    """
    setup_logger(log_file, max_bytes, backups)
    
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, crypto),
        host, port
    )
    
    addr = server.sockets[0].getsockname()
    print(f'🚀 Servidor asíncrono escuchando en {addr[0]}:{addr[1]}')
    print(f'🔐 Cifrado simétrico AES-256-GCM + HMAC + SHA256 activado')
    print(f'📝 Logs guardándose en: {log_file}')
    print(f'⚡ Modo asíncrono: Manejo eficiente de múltiples clientes')
    print('💡 Presiona Ctrl+C para detener el servidor')
    
    async with server:
        try:
            await server.serve_forever()
        except KeyboardInterrupt:
            print('\n🛑 Deteniendo servidor...')
            # Cerrar todas las conexiones
            for writer in connected_clients.copy():
                writer.close()
                await writer.wait_closed()

def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(description='Servidor de chat TCP asíncrono con cifrado simétrico')
    parser.add_argument('--host', default='0.0.0.0', help='IP de escucha (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=9000, help='Puerto de escucha (default: 9000)')
    parser.add_argument('--log-file', default='chat.log', help='Archivo de log (default: chat.log)')
    parser.add_argument('--max-bytes', type=int, default=5_000_000, help='Tamaño máximo del archivo de log (default: 5MB)')
    parser.add_argument('--backups', type=int, default=3, help='Número de archivos de respaldo (default: 3)')
    parser.add_argument('--password', default='chat_secret_key_2024', help='Contraseña para cifrado (default: chat_secret_key_2024)')
    
    args = parser.parse_args()
    
    crypto = SymmetricCrypto(args.password)
    
    try:
        asyncio.run(main_server(
            args.host, 
            args.port, 
            crypto, 
            args.log_file, 
            args.max_bytes, 
            args.backups
        ))
    except KeyboardInterrupt:
        print('\n👋 Servidor detenido')

if __name__ == '__main__':
    main()
