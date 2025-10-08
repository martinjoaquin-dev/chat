# client.py
import socket, struct, sys, argparse
from crypto_utils_asymmetric import AsymmetricCrypto

def main():
    parser = argparse.ArgumentParser(description='Cliente de chat TCP con cifrado asimétrico')
    parser.add_argument('--host', default='127.0.0.1', help='IP del servidor (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=9000, help='Puerto del servidor (default: 9000)')
    parser.add_argument('--key-size', type=int, default=4096, help='Tamaño de clave RSA (default: 4096)')
    
    args = parser.parse_args()
    
    crypto = AsymmetricCrypto(args.key_size)
    crypto.generate_rsa_keys()
    crypto.generate_ecdh_keys()
    
    try:
        with socket.create_connection((args.host, args.port)) as s:
            print(f'✅ Conectado a {args.host}:{args.port}')
            print('🔐 Cifrado asimétrico RSA-4096 + ECDH P-384 + AES-256-GCM activado')
            print(f'🆔 ID Cliente: {crypto.get_public_key_hash()}')
            print('💬 Escribe mensajes y presiona Enter (Ctrl+D para salir)')
            print('─' * 50)
            
            print('🔄 Iniciando intercambio de claves...')
            
            client_rsa_pem = crypto.get_rsa_public_key_pem()
            client_ecdh_bytes = crypto.get_ecdh_public_key_bytes()
            
            s.sendall(struct.pack('!I', len(client_rsa_pem)) + client_rsa_pem)
            print('📤 Clave pública RSA enviada')
            
            s.sendall(struct.pack('!I', len(client_ecdh_bytes)) + client_ecdh_bytes)
            print('📤 Clave pública ECDH enviada')

            rsa_len_data = s.recv(4)
            if not rsa_len_data:
                raise ConnectionError("Conexión cerrada durante intercambio de claves")
            rsa_len = struct.unpack('!I', rsa_len_data)[0]
            
            server_rsa_pem = b''
            while len(server_rsa_pem) < rsa_len:
                chunk = s.recv(rsa_len - len(server_rsa_pem))
                if not chunk:
                    raise ConnectionError("Conexión cerrada durante intercambio de claves")
                server_rsa_pem += chunk
            
            ecdh_len_data = s.recv(4)
            if not ecdh_len_data:
                raise ConnectionError("Conexión cerrada durante intercambio de claves")
            ecdh_len = struct.unpack('!I', ecdh_len_data)[0]
            
            server_ecdh_bytes = b''
            while len(server_ecdh_bytes) < ecdh_len:
                chunk = s.recv(ecdh_len - len(server_ecdh_bytes))
                if not chunk:
                    raise ConnectionError("Conexión cerrada durante intercambio de claves")
                server_ecdh_bytes += chunk
            
            print('📥 Claves públicas del servidor recibidas')
            
            server_rsa_public = crypto.load_peer_rsa_public_key(server_rsa_pem)
            server_ecdh_public = crypto.load_peer_ecdh_public_key(server_ecdh_bytes)
            
            crypto.compute_shared_secret(server_ecdh_public)
            print('🤝 Secreto compartido ECDH calculado')
            print('✅ Intercambio de claves completado')
            print()
            
            for line in sys.stdin:
                plaintext = line.rstrip()
                if plaintext:
                    try:
                        encrypted_payload = crypto.encrypt_message_payload(plaintext)
                        
                        signature = crypto.sign_message(plaintext)
                        
                        import binascii
                        print(f'🔐 Datos cifrados: {binascii.hexlify(encrypted_payload[:50]).decode()}...')
                        print(f'📏 Tamaño: {len(encrypted_payload)} bytes')
                        print(f'✍️ Firma digital: {binascii.hexlify(signature[:20]).decode()}...')
                        
                        message_data = struct.pack('!I', len(encrypted_payload)) + encrypted_payload + struct.pack('!I', len(signature)) + signature
                        s.sendall(message_data)
                        print('✔ Mensaje cifrado, firmado y enviado')
                    except Exception as e:
                        print(f'❌ Error al cifrar/firmar mensaje: {e}')
                    
    except KeyboardInterrupt:
        print('\n👋 Interrumpido por el usuario — hasta luego')
    except ConnectionRefusedError:
        print(f'❌ No se pudo conectar a {args.host}:{args.port}')
        print('💡 ¿Está el servidor corriendo? Verifica con: python server.py')
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    main()