import asyncio
import argparse
import logging
from logging.handlers import RotatingFileHandler

def configurar_logger(log_file: str, max_bytes: int, backups: int):
    logger = logging.getLogger("AsyncChatServer")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backups, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger

async def manejar_cliente(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, logger: logging.Logger):
    addr = writer.get_extra_info('peername')
    logger.info(f"Cliente conectado: {addr}")
    try:
        while True:
            length_bytes = await reader.readexactly(4)
            length = int.from_bytes(length_bytes, "big")
            data = await reader.readexactly(length)
            mensaje = data.decode("utf-8", errors="replace")
            logger.info(f"{addr[0]}:{addr[1]} | {mensaje}")
    except asyncio.IncompleteReadError:
        pass
    except ConnectionResetError:
        pass
    finally:
        logger.info(f"Cliente desconectado: {addr}")
        writer.close()
        await writer.wait_closed()

async def main():
    parser = argparse.ArgumentParser(description="Servidor TCP asíncrono con SHA-256")
    parser.add_argument("--host", default="0.0.0.0", help="Host donde escuchar")
    parser.add_argument("--port", type=int, default=9000, help="Puerto del servidor")
    parser.add_argument("--log-file", default="chat_async.log", help="Archivo de log")
    parser.add_argument("--max-bytes", type=int, default=5_000_000, help="Tamaño máximo de log")
    parser.add_argument("--backups", type=int, default=3, help="Número de backups de log")
    args = parser.parse_args()

    logger = configurar_logger(args.log_file, args.max_bytes, args.backups)
    server = await asyncio.start_server(
        lambda r, w: manejar_cliente(r, w, logger),
        host=args.host,
        port=args.port
    )

    addr = server.sockets[0].getsockname()
    print(f"🚀 Servidor escuchando en {addr}")
    print(f"📝 Logs guardándose en: {args.log_file}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido.")