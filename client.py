import asyncio
import argparse
import hashlib

def cifrar_mensaje(mensaje: str) -> str:
    """Cifra el mensaje con SHA-256."""
    return hashlib.sha256(mensaje.encode('utf-8')).hexdigest()

async def enviar_mensajes(writer: asyncio.StreamWriter, usar_hash: bool):
    print("💬 Escribe mensajes y presiona Enter (Ctrl+D para salir)")
    try:
        while True:
            mensaje = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
            if not mensaje:
                continue
            if usar_hash:
                mensaje = cifrar_mensaje(mensaje)
            data = mensaje.encode("utf-8")
            length = len(data).to_bytes(4, "big")
            writer.write(length + data)
            await writer.drain()
            print("✔ Mensaje enviado")
    except (EOFError, KeyboardInterrupt):
        print("\n👋 Cerrando conexión...")
        writer.close()
        await writer.wait_closed()

async def main():
    parser = argparse.ArgumentParser(description="Cliente TCP asíncrono con SHA-256")
    parser.add_argument("--host", default="127.0.0.1", help="Host del servidor")
    parser.add_argument("--port", type=int, default=9000, help="Puerto del servidor")
    parser.add_argument("--hash", action="store_true", help="Activar cifrado SHA-256")
    args = parser.parse_args()

    print(f"🔌 Conectando a {args.host}:{args.port} ...")
    reader, writer = await asyncio.open_connection(args.host, args.port)
    print("✅ Conectado")
    modo = "CIFRADO (SHA-256)" if args.hash else "TEXTO PLANO"
    print(f"💬 Modo: {modo}\n──────────────────────────────")
    await enviar_mensajes(writer, usar_hash=args.hash)

if __name__ == "__main__":
    asyncio.run(main())