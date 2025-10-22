import socket
import threading
import logging
import argparse
from queue import Queue
from logging.handlers import RotatingFileHandler

# ==========================
# Configuración del logger
# ==========================
def configurar_logger(log_file: str, max_bytes: int, backups: int):
    logger = logging.getLogger("ChatServer")
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backups, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger

# ==========================
# Hilo para manejar clientes
# ==========================
def manejar_cliente(conn: socket.socket, addr, cola: Queue):
    try:
        while True:
            length_bytes = conn.recv(4)
            if not length_bytes:
                break
            length = int.from_bytes(length_bytes, "big")
            data = conn.recv(length)
            if not data:
                break
            mensaje = data.decode("utf-8", errors="replace")
            cola.put((addr, mensaje))
    except ConnectionResetError:
        pass
    finally:
        conn.close()

# ==========================
# Hilo logger
# ==========================
def logger_thread(cola: Queue, logger: logging.Logger):
    while True:
        addr, mensaje = cola.get()
        logger.info(f"{addr[0]}:{addr[1]} | {mensaje}")
        cola.task_done()

# ==========================
# Main server
# ==========================
def main():
    parser = argparse.ArgumentParser(description="Servidor de chat TCP con soporte SHA-256")
    parser.add_argument("--host", default="0.0.0.0", help="Host donde escuchar")
    parser.add_argument("--port", type=int, default=9000, help="Puerto del servidor")
    parser.add_argument("--log-file", default="chat.log", help="Archivo de logs")
    parser.add_argument("--max-bytes", type=int, default=5_000_000, help="Tamaño máximo del log")
    parser.add_argument("--backups", type=int, default=3, help="Número de backups del log")
    args = parser.parse_args()

    logger = configurar_logger(args.log_file, args.max_bytes, args.backups)
    cola = Queue()
    threading.Thread(target=logger_thread, args=(cola, logger), daemon=True).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((args.host, args.port))
        s.listen()
        print(f"🚀 Servidor escuchando en {args.host}:{args.port}")
        print(f"📝 Logs guardándose en: {args.log_file}")

        try:
            while True:
                conn, addr = s.accept()
                print(f"Cliente conectado: {addr[0]}:{addr[1]}")
                threading.Thread(target=manejar_cliente, args=(conn, addr, cola), daemon=True).start()
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido.")

if __name__ == "__main__":
    main()