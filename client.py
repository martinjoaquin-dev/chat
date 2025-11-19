# client.py - Versión Asíncrona con Cifrado Híbrido y SSL/TLS
"""
Cliente de chat TCP asíncrono con cifrado híbrido (RSA + AES) y SSL/TLS.
Utiliza asyncio para comunicación no bloqueante con el servidor.
Variables de entorno reemplazan valores hardcodeados.
"""

import asyncio
import struct
import sys
import argparse
import os
import ssl
from crypto_utils import HybridCrypto
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración desde variables de entorno
CLIENT_HOST = os.getenv('CLIENT_HOST', '127.0.0.1')
CLIENT_PORT = int(os.getenv('CLIENT_PORT', '9000'))
SSL_ENABLED = os.getenv('SSL_ENABLED', 'true').lower() == 'true'
SSL_CA_FILE = os.getenv('SSL_CA_FILE', 'certificates/ca.crt')

async def exchange_keys(reader, writer, client_crypto):
    """
    Intercambia claves públicas RSA y establece la clave AES compartida.
    
    Args:
        reader: StreamReader para leer datos
        writer: StreamWriter para escribir datos
        client_crypto: Instancia de HybridCrypto del cliente
        
    Returns:
        bool: True si el intercambio fue exitoso
    """
    try:
        # 1. Recibir clave pública del servidor
        raw_len = await reader.readexactly(4)
        server_key_len = struct.unpack('!I', raw_len)[0]
        server_public_key = await reader.readexactly(server_key_len)
        client_crypto.load_peer_public_key(server_public_key)
        
        # 2. Enviar clave pública del cliente al servidor
        client_public_key = client_crypto.get_public_key_pem()
        key_len = len(client_public_key)
        writer.write(struct.pack('!I', key_len) + client_public_key)
        await writer.drain()
        
        # 3. Generar y cifrar clave AES, enviarla al servidor
        encrypted_aes_key = client_crypto.generate_and_encrypt_aes_key()
        writer.write(struct.pack('!I', len(encrypted_aes_key)) + encrypted_aes_key)
        await writer.drain()
        
        return True
    except Exception as e:
        print(f'Error en intercambio de claves: {e}')
        return False

async def send_message(writer, crypto, message):
    """
    Cifra y envía un mensaje al servidor con validación SHA256.
    
    Args:
        writer: StreamWriter para escribir datos
        crypto: Instancia de HybridCrypto para cifrar mensajes
        message: Mensaje de texto a enviar
    """
    try:
        # Calcular hash SHA256 del mensaje original ANTES de cifrar
        message_hash = crypto.hash_message(message)
        message_hash_bytes = bytes.fromhex(message_hash)
        
        # Cifrar mensaje
        encrypted_payload = crypto.encrypt_message_payload(message)
        
        import binascii
        print(f'Datos cifrados: {binascii.hexlify(encrypted_payload[:50]).decode()}...')
        print(f'Tamano: {len(encrypted_payload)} bytes')
        print(f'Hash SHA256 del mensaje: {message_hash}')
        
        # Construir payload: hash SHA256 (32 bytes) + payload cifrado
        full_payload = message_hash_bytes + encrypted_payload
        total_length = len(full_payload)
        
        # Enviar longitud + hash SHA256 + payload cifrado
        data = struct.pack('!I', total_length) + full_payload
        writer.write(data)
        await writer.drain()
        
        print('Mensaje cifrado y enviado con hash SHA256')
        
    except Exception as e:
        print(f'Error al cifrar/enviar mensaje: {e}')

async def read_input():
    """
    Lee entrada del usuario de forma asíncrona.
    
    Returns:
        str: Línea ingresada por el usuario
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sys.stdin.readline)

def create_ssl_context():
    """
    Crea contexto SSL/TLS para el cliente.
    
    Returns:
        ssl.SSLContext o None si SSL está deshabilitado
    """
    if not SSL_ENABLED:
        return None
    
    try:
        context = ssl.create_default_context()
        # Para desarrollo con certificados self-signed
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Si existe archivo CA, cargarlo
        if os.path.exists(SSL_CA_FILE):
            context.load_verify_locations(SSL_CA_FILE)
        
        return context
    except Exception as e:
        print(f'Error al crear contexto SSL: {e}')
        print('Continuando sin SSL...')
        return None

async def main_client(host=None, port=None, ssl_context=None):
    """
    Función principal del cliente asíncrono.
    
    Args:
        host: Dirección IP del servidor
        port: Puerto del servidor
        ssl_context: Contexto SSL/TLS (opcional)
    """
    host = host or CLIENT_HOST
    port = port or CLIENT_PORT
    
    try:
        reader, writer = await asyncio.open_connection(host, port, ssl=ssl_context)
        
        # Verificar si la conexión usa SSL
        ssl_info = writer.get_extra_info('sslcontext')
        protocol = "SSL/TLS" if ssl_info else "TCP"
        
        print(f'Conectado a {host}:{port} ({protocol})')
        
        # Crear instancia de cifrado híbrido
        crypto = HybridCrypto()
        
        # Intercambiar claves RSA y establecer clave AES
        print('Intercambiando claves con el servidor...')
        if not await exchange_keys(reader, writer, crypto):
            print('Error en intercambio de claves')
            return
        
        print('Claves intercambiadas exitosamente')
        print('Cifrado hibrido RSA + AES-256-GCM + HMAC + SHA256 activado')
        if ssl_info:
            print('SSL/TLS activado: Conexion de transporte cifrada')
        print('Modo asincrono: Comunicacion no bloqueante')
        print('Escribe mensajes y presiona Enter (Ctrl+C para salir)')
        print('-' * 50)
        
        # Tarea para leer entrada del usuario
        async def input_loop():
            while True:
                try:
                    line = await read_input()
                    if not line:
                        break
                    message = line.rstrip()
                    if message:
                        await send_message(writer, crypto, message)
                except EOFError:
                    break
                except Exception as e:
                    print(f'Error: {e}')
                    break
        
        # Ejecutar loop de entrada
        try:
            await input_loop()
        except KeyboardInterrupt:
            print('\nInterrumpido por el usuario - hasta luego')
        finally:
            writer.close()
            await writer.wait_closed()
            
    except ConnectionRefusedError:
        print(f'No se pudo conectar a {host}:{port}')
        print('¿Esta el servidor corriendo? Verifica con: python server.py')
    except ssl.SSLError as e:
        print(f'Error SSL: {e}')
        print('Verifica que los certificados SSL esten generados: python generate_ssl_cert.py')
    except Exception as e:
        print(f'Error: {e}')

def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(description='Cliente de chat TCP asíncrono con cifrado híbrido y SSL/TLS')
    parser.add_argument('--host', default=None, help=f'IP del servidor (default: {CLIENT_HOST} desde .env)')
    parser.add_argument('--port', type=int, default=None, help=f'Puerto del servidor (default: {CLIENT_PORT} desde .env)')
    parser.add_argument('--no-ssl', action='store_true', help='Deshabilitar SSL/TLS (usar TCP sin cifrado de transporte)')
    
    args = parser.parse_args()
    
    # Crear contexto SSL si está habilitado
    ssl_context = None
    if not args.no_ssl and SSL_ENABLED:
        ssl_context = create_ssl_context()
    
    try:
        asyncio.run(main_client(args.host, args.port, ssl_context))
    except KeyboardInterrupt:
        print('\nCliente cerrado')

if __name__ == '__main__':
    main()
