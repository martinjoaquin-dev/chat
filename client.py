# client.py - Versión Asíncrona
"""
Cliente de chat TCP asíncrono con cifrado simétrico.
Utiliza asyncio para comunicación no bloqueante con el servidor.
"""

import asyncio
import struct
import sys
import argparse
from crypto_utils import SymmetricCrypto

async def send_message(writer, crypto, message):
    """
    Cifra y envía un mensaje al servidor.
    
    Args:
        writer: StreamWriter para escribir datos
        crypto: Instancia de SymmetricCrypto para cifrar mensajes
        message: Mensaje de texto a enviar
    """
    try:
        # Cifrar mensaje
        encrypted_payload = crypto.encrypt_message_payload(message)
        
        # Calcular hash SHA256 del mensaje original
        message_hash = crypto.hash_message(message)
        
        import binascii
        print(f'🔐 Datos cifrados: {binascii.hexlify(encrypted_payload[:50]).decode()}...')
        print(f'📏 Tamaño: {len(encrypted_payload)} bytes')
        print(f'🔐 Hash SHA256 del mensaje: {message_hash}')
        
        # Enviar longitud + payload
        data = struct.pack('!I', len(encrypted_payload)) + encrypted_payload
        writer.write(data)
        await writer.drain()
        
        print('✔ Mensaje cifrado y enviado')
        
    except Exception as e:
        print(f'❌ Error al cifrar/enviar mensaje: {e}')

async def read_input():
    """
    Lee entrada del usuario de forma asíncrona.
    
    Returns:
        str: Línea ingresada por el usuario
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sys.stdin.readline)

async def main_client(host, port, crypto):
    """
    Función principal del cliente asíncrono.
    
    Args:
        host: Dirección IP del servidor
        port: Puerto del servidor
        crypto: Instancia de SymmetricCrypto
    """
    try:
        reader, writer = await asyncio.open_connection(host, port)
        
        print(f'✅ Conectado a {host}:{port}')
        print('🔐 Cifrado simétrico AES-256-GCM + HMAC + SHA256 activado')
        print('⚡ Modo asíncrono: Comunicación no bloqueante')
        print('💬 Escribe mensajes y presiona Enter (Ctrl+C para salir)')
        print('─' * 50)
        
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
                    print(f'❌ Error: {e}')
                    break
        
        # Ejecutar loop de entrada
        try:
            await input_loop()
        except KeyboardInterrupt:
            print('\n👋 Interrumpido por el usuario — hasta luego')
        finally:
            writer.close()
            await writer.wait_closed()
            
    except ConnectionRefusedError:
        print(f'❌ No se pudo conectar a {host}:{port}')
        print('💡 ¿Está el servidor corriendo? Verifica con: python server.py')
    except Exception as e:
        print(f'❌ Error: {e}')

def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(description='Cliente de chat TCP asíncrono con cifrado simétrico')
    parser.add_argument('--host', default='127.0.0.1', help='IP del servidor (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=9000, help='Puerto del servidor (default: 9000)')
    parser.add_argument('--password', default='chat_secret_key_2024', help='Contraseña para cifrado (default: chat_secret_key_2024)')
    
    args = parser.parse_args()
    
    crypto = SymmetricCrypto(args.password)
    
    try:
        asyncio.run(main_client(args.host, args.port, crypto))
    except KeyboardInterrupt:
        print('\n👋 Cliente cerrado')

if __name__ == '__main__':
    main()
