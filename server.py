# server.py
import logging
from logging.handlers import RotatingFileHandler
import queue
import socket
import struct
import threading
import argparse
from crypto_utils_asymmetric import AsymmetricCrypto

HOST, PORT = '0.0.0.0', 9000
msg_queue = queue.Queue()
stop_event = threading.Event()

def logger():
    log = logging.getLogger('chat')
    log.setLevel(logging.INFO)
    
    file_handler = RotatingFileHandler('chat.log', maxBytes=5_000_000, backupCount=3)
    file_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
    log.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
    log.addHandler(console_handler)
    
    while not stop_event.is_set() or not msg_queue.empty():
        try:
            client_id, text = msg_queue.get(timeout=1)
            log.info('%s | %s', client_id, text)
        except queue.Empty:
            pass

class ClientHandler(threading.Thread):
    def __init__(self, conn, addr, crypto):
        super().__init__(daemon=True)
        self.conn, self.addr = conn, addr
        self.crypto = crypto
        self.client_rsa_public = None
        self.client_ecdh_public = None
        self.shared_secret_computed = False

    def run(self):
        with self.conn:
            client_id = f'{self.addr[0]}:{self.addr[1]}'
            print(f'Cliente conectado: {client_id}')
            
            try:
                print(f'🔄 Iniciando intercambio de claves con {client_id}...')
                
                rsa_len_data = self.conn.recv(4)
                if not rsa_len_data:
                    return
                rsa_len = struct.unpack('!I', rsa_len_data)[0]
                
                client_rsa_pem = b''
                while len(client_rsa_pem) < rsa_len:
                    chunk = self.conn.recv(rsa_len - len(client_rsa_pem))
                    if not chunk:
                        return
                    client_rsa_pem += chunk
                
                ecdh_len_data = self.conn.recv(4)
                if not ecdh_len_data:
                    return
                ecdh_len = struct.unpack('!I', ecdh_len_data)[0]
                
                client_ecdh_bytes = b''
                while len(client_ecdh_bytes) < ecdh_len:
                    chunk = self.conn.recv(ecdh_len - len(client_ecdh_bytes))
                    if not chunk:
                        return
                    client_ecdh_bytes += chunk
                
                print(f'📥 Claves públicas de {client_id} recibidas')
                
                self.client_rsa_public = self.crypto.load_peer_rsa_public_key(client_rsa_pem)
                self.client_ecdh_public = self.crypto.load_peer_ecdh_public_key(client_ecdh_bytes)
                
                server_rsa_pem = self.crypto.get_rsa_public_key_pem()
                server_ecdh_bytes = self.crypto.get_ecdh_public_key_bytes()
                
                self.conn.sendall(struct.pack('!I', len(server_rsa_pem)) + server_rsa_pem)
                print(f'📤 Clave pública RSA enviada a {client_id}')
                
                self.conn.sendall(struct.pack('!I', len(server_ecdh_bytes)) + server_ecdh_bytes)
                print(f'📤 Clave pública ECDH enviada a {client_id}')
                
                self.crypto.compute_shared_secret(self.client_ecdh_public)
                self.shared_secret_computed = True
                print(f'🤝 Secreto compartido ECDH calculado para {client_id}')
                print(f'✅ Intercambio de claves completado con {client_id}')
                print()
                
                while not stop_event.is_set():
                    try:
                        raw_len = self.conn.recv(4)
                        if not raw_len:
                            break
                        (length,) = struct.unpack('!I', raw_len)
                        
                        buf = bytearray()
                        while len(buf) < length:
                            chunk = self.conn.recv(length - len(buf))
                            if not chunk:
                                break
                            buf.extend(chunk)
                        
                        if len(buf) == length:
                            try:
                                sig_len_data = self.conn.recv(4)
                                if not sig_len_data:
                                    break
                                sig_len = struct.unpack('!I', sig_len_data)[0]
                                
                                signature = b''
                                while len(signature) < sig_len:
                                    chunk = self.conn.recv(sig_len - len(signature))
                                    if not chunk:
                                        break
                                    signature += chunk
                                
                                if len(signature) == sig_len:
                                    import binascii
                                    print(f'📡 Datos cifrados recibidos de {client_id}: {binascii.hexlify(buf[:50]).decode()}...')
                                    print(f'📏 Tamaño recibido: {len(buf)} bytes')
                                    print(f'✍️ Firma recibida: {binascii.hexlify(signature[:20]).decode()}...')
                                    
                                    plaintext = self.crypto.decrypt_message(buf)
                                    
                                    signature_valid = self.crypto.verify_signature(plaintext, signature, self.client_rsa_public)
                                    
                                    if signature_valid:
                                        msg_queue.put((client_id, plaintext))
                                        print(f'🔓 Mensaje descifrado y verificado: "{plaintext}"')
                                        print(f'✅ Firma digital válida de {client_id}')
                                    else:
                                        print(f'❌ Firma digital inválida de {client_id}')
                                        
                            except ValueError as e:
                                print(f'❌ Error de descifrado de {client_id}: {e}')
                            except Exception as e:
                                print(f'❌ Error inesperado de {client_id}: {e}')
                    except (ConnectionError, struct.error, OSError):
                        break
                        
            except Exception as e:
                print(f'❌ Error en intercambio de claves con {client_id}: {e}')
            finally:
                print(f'Cliente desconectado: {client_id}')

def main():
    parser = argparse.ArgumentParser(description='Servidor de chat TCP con cifrado asimétrico')
    parser.add_argument('--host', default='0.0.0.0', help='IP de escucha (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=9000, help='Puerto de escucha (default: 9000)')
    parser.add_argument('--log-file', default='chat.log', help='Archivo de log (default: chat.log)')
    parser.add_argument('--max-bytes', type=int, default=5_000_000, help='Tamaño máximo del archivo de log (default: 5MB)')
    parser.add_argument('--backups', type=int, default=3, help='Número de archivos de respaldo (default: 3)')
    parser.add_argument('--key-size', type=int, default=4096, help='Tamaño de clave RSA (default: 4096)')
    
    args = parser.parse_args()
    
    global HOST, PORT
    HOST, PORT = args.host, args.port
    
    crypto = AsymmetricCrypto(args.key_size)
    crypto.generate_rsa_keys()
    crypto.generate_ecdh_keys()
    
    def logger():
        log = logging.getLogger('chat')
        log.setLevel(logging.INFO)
        
        file_handler = RotatingFileHandler(args.log_file, maxBytes=args.max_bytes, backupCount=args.backups)
        file_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
        log.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
        log.addHandler(console_handler)
        
        while not stop_event.is_set() or not msg_queue.empty():
            try:
                client_id, text = msg_queue.get(timeout=1)
                log.info('%s | %s', client_id, text)
            except queue.Empty:
                pass
    
    threading.Thread(target=logger, daemon=True).start()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f'🚀 Servidor escuchando en {HOST}:{PORT}')
        print(f'🔐 Cifrado asimétrico RSA-4096 + ECDH P-384 + AES-256-GCM activado')
        print(f'🆔 ID Servidor: {crypto.get_public_key_hash()}')
        print(f'📝 Logs guardándose en: {args.log_file}')
        print('💡 Presiona Ctrl+C para detener el servidor')
        try:
            while True:
                conn, addr = s.accept()
                ClientHandler(conn, addr, crypto).start()
        except KeyboardInterrupt:
            print('\n🛑 Deteniendo servidor...')
            stop_event.set()

if __name__ == '__main__':
    main()