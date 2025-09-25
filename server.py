# server.py
import logging
from logging.handlers import RotatingFileHandler
import queue
import socket
import struct
import threading
import argparse

HOST, PORT = '0.0.0.0', 9000
msg_queue = queue.Queue()
stop_event = threading.Event()

def logger():
    log = logging.getLogger('chat')
    log.setLevel(logging.INFO)
    
    # Handler para archivo rotativo
    file_handler = RotatingFileHandler('chat.log', maxBytes=5_000_000, backupCount=3)
    file_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
    log.addHandler(file_handler)
    
    # Handler para consola
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
    def __init__(self, conn, addr):
        super().__init__(daemon=True)
        self.conn, self.addr = conn, addr

    def run(self):
        with self.conn:
            client_id = f'{self.addr[0]}:{self.addr[1]}'
            print(f'Cliente conectado: {client_id}')
            while not stop_event.is_set():
                try:
                    raw_len = self.conn.recv(4)
                    if not raw_len:
                        break
                    (length,) = struct.unpack('!I', raw_len)
                    
                    # Leer el mensaje completo
                    buf = bytearray()
                    while len(buf) < length:
                        chunk = self.conn.recv(length - len(buf))
                        if not chunk:
                            break
                        buf.extend(chunk)
                    
                    if len(buf) == length:
                        data = buf.decode()
                        msg_queue.put((client_id, data))
                except (ConnectionError, struct.error, OSError):
                    break
            print(f'Cliente desconectado: {client_id}')

def main():
    parser = argparse.ArgumentParser(description='Servidor de chat TCP')
    parser.add_argument('--host', default='0.0.0.0', help='IP de escucha (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=9000, help='Puerto de escucha (default: 9000)')
    parser.add_argument('--log-file', default='chat.log', help='Archivo de log (default: chat.log)')
    parser.add_argument('--max-bytes', type=int, default=5_000_000, help='Tamaño máximo del archivo de log (default: 5MB)')
    parser.add_argument('--backups', type=int, default=3, help='Número de archivos de respaldo (default: 3)')
    
    args = parser.parse_args()
    
    global HOST, PORT
    HOST, PORT = args.host, args.port
    
    # Actualizar el handler de archivo con los argumentos
    def logger():
        log = logging.getLogger('chat')
        log.setLevel(logging.INFO)
        
        # Handler para archivo rotativo
        file_handler = RotatingFileHandler(args.log_file, maxBytes=args.max_bytes, backupCount=args.backups)
        file_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
        log.addHandler(file_handler)
        
        # Handler para consola
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
        print(f'📝 Logs guardándose en: {args.log_file}')
        print('💡 Presiona Ctrl+C para detener el servidor')
        try:
            while True:
                conn, addr = s.accept()
                ClientHandler(conn, addr).start()
        except KeyboardInterrupt:
            print('\n🛑 Deteniendo servidor...')
            stop_event.set()

if __name__ == '__main__':
    main()
