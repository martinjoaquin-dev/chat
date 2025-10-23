import socket
import argparse
import hashlib


def cifrar_mensaje(mensaje: str) -> str:
    """Devuelve el hash SHA-256 del mensaje en formato hexadecimal."""
    return hashlib.sha256(mensaje.encode('utf-8')).hexdigest()


def enviar_mensaje(sock: socket.socket, mensaje: str, usar_hash: bool = False):
    """Envía el mensaje (en texto plano o cifrado) al servidor."""
    if usar_hash:
        mensaje = cifrar_mensaje(mensaje)
    payload = mensaje.encode('utf-8')
    length = len(payload).to_bytes(4, 'big')
    sock.sendall(length + payload)


def main():
    parser = argparse.ArgumentParser(description="Cliente de chat TCP con opción de cifrado SHA-256")
    parser.add_argument("--host", default="127.0.0.1", help="IP del servidor")
    parser.add_argument("--port", type=int, default=9000, help="Puerto del servidor")
    parser.add_argument("--hash", action="store_true", help="Enviar mensajes cifrados con SHA-256")
    args = parser.parse_args()

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((args.host, args.port))
        print(f"✅ Conectado a {args.host}:{args.port}")
        modo = "CIFRADO (SHA-256)" if args.hash else "TEXTO PLANO"
        print(f"💬 Modo: {modo}")
        print("──────────────────────────────────────────────────")
        print("Escribe mensajes y presiona Enter (Ctrl+D para salir)")

        while True:
            try:
                mensaje = input("> ")
            except EOFError:
                break
            if not mensaje:
                continue
            enviar_mensaje(sock, mensaje, usar_hash=args.hash)
            print("✔ Mensaje enviado")
    except ConnectionRefusedError:
        print("❌ No se pudo conectar con el servidor.")
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
        print("\n👋 Conexión cerrada.")


if __name__ == "__main__":
    main()