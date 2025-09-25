# client.py
import socket, struct, sys, argparse

def main():
    parser = argparse.ArgumentParser(description='Cliente de chat TCP')
    parser.add_argument('--host', default='127.0.0.1', help='IP del servidor (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=9000, help='Puerto del servidor (default: 9000)')
    
    args = parser.parse_args()
    
    try:
        with socket.create_connection((args.host, args.port)) as s:
            print(f'✅ Conectado a {args.host}:{args.port}')
            print('💬 Escribe mensajes y presiona Enter (Ctrl+D para salir)')
            print('─' * 50)
            
            for line in sys.stdin:
                data = line.rstrip().encode()
                if data:  # Solo enviar si hay contenido
                    s.sendall(struct.pack('!I', len(data)) + data)
                    print('✔ Mensaje enviado')
                    
    except KeyboardInterrupt:
        print('\n👋 Interrumpido por el usuario — hasta luego')
    except ConnectionRefusedError:
        print(f'❌ No se pudo conectar a {args.host}:{args.port}')
        print('💡 ¿Está el servidor corriendo? Verifica con: python server.py')
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    main()
