# client.py - Versión Asíncrona con Cifrado Híbrido
"""
Cliente de chat TCP asíncrono con cifrado híbrido (RSA + AES).
Utiliza asyncio para comunicación no bloqueante con el servidor.
"""

import asyncio
import struct
import sys
import argparse
from crypto_utils import HybridCrypto

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

async def main_client(host, port):
    """
    Función principal del cliente asíncrono.
    
    Args:
        host: Dirección IP del servidor
        port: Puerto del servidor
    """
    try:
        reader, writer = await asyncio.open_connection(host, port)
        
        print(f'Conectado a {host}:{port}')
        
        # Crear instancia de cifrado híbrido
        crypto = HybridCrypto()
        
        # Intercambiar claves RSA y establecer clave AES
        print('Intercambiando claves con el servidor...')
        if not await exchange_keys(reader, writer, crypto):
            print('Error en intercambio de claves')
            return
        
        print('Claves intercambiadas exitosamente')
        print('Cifrado hibrido RSA + AES-256-GCM + HMAC + SHA256 activado')
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
    except Exception as e:
        print(f'Error: {e}')

def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(description='Cliente de chat TCP asíncrono con cifrado híbrido')
    parser.add_argument('--host', default='127.0.0.1', help='IP del servidor (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=9000, help='Puerto del servidor (default: 9000)')
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main_client(args.host, args.port))
    except KeyboardInterrupt:
        print('\nCliente cerrado')

if __name__ == '__main__':
    main()
