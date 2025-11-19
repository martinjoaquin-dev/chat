# server.py - Versión Asíncrona con Cifrado Híbrido
"""
Servidor de chat TCP asíncrono con cifrado híbrido (RSA + AES).
Utiliza asyncio para manejar múltiples clientes de forma eficiente.
"""

import asyncio
import logging
from logging.handlers import RotatingFileHandler
import struct
import argparse
from datetime import datetime
from crypto_utils import HybridCrypto

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
    
    print(f'Cliente conectado: {client_id}')
    
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

async def main_server(host, port, log_file, max_bytes, backups):
    """
    Función principal del servidor asíncrono.
    
    Args:
        host: Dirección IP de escucha
        port: Puerto de escucha
        log_file: Nombre del archivo de log
        max_bytes: Tamaño máximo del archivo de log
        backups: Número de archivos de respaldo
    """
    setup_logger(log_file, max_bytes, backups)
    
    server = await asyncio.start_server(
        handle_client,
        host, port
    )
    
    addr = server.sockets[0].getsockname()
    print(f'Servidor asincrono escuchando en {addr[0]}:{addr[1]}')
    print(f'Cifrado hibrido RSA + AES-256-GCM + HMAC + SHA256 activado')
    print(f'Logs guardandose en: {log_file}')
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
    parser = argparse.ArgumentParser(description='Servidor de chat TCP asíncrono con cifrado híbrido')
    parser.add_argument('--host', default='0.0.0.0', help='IP de escucha (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=9000, help='Puerto de escucha (default: 9000)')
    parser.add_argument('--log-file', default='chat.log', help='Archivo de log (default: chat.log)')
    parser.add_argument('--max-bytes', type=int, default=5_000_000, help='Tamaño máximo del archivo de log (default: 5MB)')
    parser.add_argument('--backups', type=int, default=3, help='Número de archivos de respaldo (default: 3)')
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main_server(
            args.host, 
            args.port, 
            args.log_file, 
            args.max_bytes, 
            args.backups
        ))
    except KeyboardInterrupt:
        print('\nServidor detenido')

if __name__ == '__main__':
    main()
