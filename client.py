# client.py
import socket, struct, sys, argparse
from crypto_utils import SymmetricCrypto

def main():
    parser = argparse.ArgumentParser(description='Cliente de chat TCP con cifrado simétrico')
    parser.add_argument('--host', default='127.0.0.1', help='IP del servidor (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=9000, help='Puerto del servidor (default: 9000)')
    parser.add_argument('--password', default='chat_secret_key_2024', help='Contraseña para cifrado (default: chat_secret_key_2024)')
    
    args = parser.parse_args()
    
    crypto = SymmetricCrypto(args.password)
    
    try:
        with socket.create_connection((args.host, args.port)) as s:
            print(f'✅ Conectado a {args.host}:{args.port}')
            print('🔐 Cifrado simétrico AES-256-GCM + HMAC activado')
            print('💬 Escribe mensajes y presiona Enter (Ctrl+D para salir)')
            print('─' * 50)
            
            for line in sys.stdin:
                plaintext = line.rstrip()
                if plaintext:
                    try:
                        encrypted_payload = crypto.encrypt_message_payload(plaintext)
                        
                        import binascii
                        print(f'🔐 Datos cifrados: {binascii.hexlify(encrypted_payload[:50]).decode()}...')
                        print(f'📏 Tamaño: {len(encrypted_payload)} bytes')
                        
                        s.sendall(struct.pack('!I', len(encrypted_payload)) + encrypted_payload)
                        print('✔ Mensaje cifrado y enviado')
                    except Exception as e:
                        print(f'❌ Error al cifrar mensaje: {e}')
                    
    except KeyboardInterrupt:
        print('\n👋 Interrumpido por el usuario — hasta luego')
    except ConnectionRefusedError:
        print(f'❌ No se pudo conectar a {args.host}:{args.port}')
        print('💡 ¿Está el servidor corriendo? Verifica con: python server.py')
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    main()
