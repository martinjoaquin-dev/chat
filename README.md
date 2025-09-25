# Chat Grupal TCP — Servidor + Clientes en Python

> **Versión:** 0.1.0  

---

## 📑 Descripción general
Este proyecto implementa un **chat grupal punto-a-punto** donde:

* Un **servidor TCP** escucha en un puerto configurable, acepta múltiples clientes y **solo recibe** sus mensajes (no los re‑envía).  
* Cada cliente envía texto; el servidor añade *timestamp* e ID de cliente y **persiste** todo en un log rotativo.  
* Se usa exclusivamente la biblioteca estándar de Python 3 (`socket`, `threading`, `queue`, `logging`).  

Su propósito es servir de ejemplo claro y mínimo de comunicación concurrente con hilos y sockets.

---

## 🏛️ Arquitectura

```
Servidor (main)
│
├─ accept()              ← bucle principal
│   └─ ClientHandler ── hilo por cliente
│        └─ recv()        ← lectura de mensajes
│
└─ LoggerThread ── escribe en chat.log
```

* **Thread‑per‑connection**: simplicidad > consumo de memoria (apto hasta ≈ 1 000 clientes).  
* **Cola thread‑safe** (`queue.Queue`) desacopla E/S de red y disco.  
* **Protocolo**: `| 4 bytes BE length | UTF‑8 payload |` (evita fragmentación de mensajes).  

---

## 🚀 Primeros pasos

### 1. Prerrequisitos

| Requisito | Versión mínima |
|-----------|----------------|
| Python    | 3.10 |
| SO        | Linux, macOS o Windows |

> **Tip:** crear un entorno virtual:  
> `python -m venv .venv && source .venv/bin/activate`

### 2. Ejecutar el sistema

```bash
# 1. Arrancar el servidor (Terminal 1)
python server.py --port 9000

# 2. Conectar cliente (Terminal 2)
python client.py --host 127.0.0.1 --port 9000

# 3. Escribir mensajes
Hola mundo 👋
Mensaje desde cliente 1

# 4. Conectar más clientes (Terminal 3, 4, etc.)
python client.py --host 127.0.0.1 --port 9000
Hola desde cliente 2
```

### 3. Ver los resultados

**En el servidor verás:**
```
🚀 Servidor escuchando en 0.0.0.0:9000
📝 Logs guardándose en: chat.log
💡 Presiona Ctrl+C para detener el servidor
Cliente conectado: 127.0.0.1:52344
2025-01-24 20:15:42,923 | 127.0.0.1:52344 | Hola mundo 👋
2025-01-24 20:15:45,123 | 127.0.0.1:52344 | Mensaje desde cliente 1
Cliente conectado: 127.0.0.1:52350
2025-01-24 20:15:48,456 | 127.0.0.1:52350 | Hola desde cliente 2
```

**En el cliente verás:**
```
✅ Conectado a 127.0.0.1:9000
💬 Escribe mensajes y presiona Enter (Ctrl+D para salir)
──────────────────────────────────────────────────
Hola mundo 👋
✔ Mensaje enviado
```

---

## ⚙️ Configuración rápida

### Servidor (`server.py`)

| Opción CLI          | Valor por defecto | Descripción                                |
|---------------------|-------------------|--------------------------------------------|
| `--host`            | `0.0.0.0`         | IP en la que el servidor escuchará         |
| `--port`            | `9000`            | Puerto TCP                                 |
| `--log-file`        | `chat.log`        | Ruta del archivo de log                    |
| `--max-bytes`       | `5_000_000`       | Tamaño máx. de cada archivo de log         |
| `--backups`         | `3`               | Nº máximo de archivos rotados              |

### Cliente (`client.py`)

| Opción CLI          | Valor por defecto | Descripción                                |
|---------------------|-------------------|--------------------------------------------|
| `--host`            | `127.0.0.1`       | IP del servidor                            |
| `--port`            | `9000`            | Puerto del servidor                        |

### Ejemplos de uso

```bash
# Servidor en puerto personalizado
python server.py --port 5000 --log-file mi_chat.log

# Cliente conectándose a servidor remoto
python client.py --host 192.168.1.100 --port 5000

# Servidor con logs más grandes
python server.py --max-bytes 10000000 --backups 5
```

---

## 📝 Estructura del repositorio

```
chat/
├── client.py        # CLI para enviar mensajes
├── server.py        # Servidor multihilo
├── README.md
└── tests/           # Unit y stress tests
```

---

## 🛠️ Guía de desarrollo

1. **Instalar dependencias de test**  
   ```bash
   pip install -r tests/requirements.txt
   ```
2. **Ejecutar pruebas**  
   ```bash
   pytest -q
   ```
3. **Lint + seguridad**  
   ```bash
   pip install ruff bandit
   ruff .
   bandit -r .
   ```

---

## 📂 Logging & persistencia

### Formato de logs

Cada entrada se registra con timestamp, ID del cliente y mensaje:
```
2025-01-24 20:15:42,923 | 127.0.0.1:52344 | Hola mundo 👋
2025-01-24 20:15:45,123 | 127.0.0.1:52350 | Mensaje desde cliente 2
```

### Características

* **Doble salida**: Los mensajes se muestran tanto en consola como en archivo
* **Rotación automática**: `RotatingFileHandler` evita crecimiento ilimitado
* **Configuración flexible**: Tamaño máximo y número de archivos de respaldo
* **Thread-safe**: Múltiples clientes pueden escribir simultáneamente

### Archivos generados

```
chat.log          # Log actual
chat.log.1        # Primer respaldo
chat.log.2        # Segundo respaldo
chat.log.3        # Tercer respaldo
```

> **Tip para producción**: Monta `/logs` en un volumen independiente para mejor rendimiento.

---

## 🛡️ Buenas prácticas de seguridad

* No ejecutar el servidor como **root**.  
* Limitar el tamaño máximo de mensaje (ej. 4 096 B) para mitigar DoS.  
* Establecer *timeouts* con `socket.settimeout(1)` para que los hilos no queden bloqueados.  
* Si se sustituye el log por BBDD, validar/escapar datos antes de insertar.

---

## 🤝 Contribuir

1. **Fork → branch → PR** con nombre descriptivo (`feature/add-tls`).  
2. Seguir la convención **Conventional Commits**.  
3. Incluir tests y actualización de documentación cuando aplique.

---

## ❓ FAQ

| Pregunta | Respuesta corta |
|----------|-----------------|
| ¿Por qué no usar `asyncio`? | El objetivo didáctico es mostrar hilos + sockets; `asyncio` añade complejidad innecesaria. |
| ¿Se puede convertir en broadcast? | Sí: guarda los sockets de los clientes y re‑envía con `sendall()` a cada uno. |
| ¿TLS/SSL? | Se puede envolver el socket con `ssl.wrap_socket()` o usar un proxy como `stunnel`. |
| ¿Por qué no veo mensajes en el servidor? | Asegúrate de que el servidor esté corriendo y que los clientes se conecten al puerto correcto. |
| ¿Cómo salir del cliente sin error? | Usa `Ctrl+D` (Linux/macOS) o `Ctrl+Z` + `Enter` (Windows). |
| ¿El servidor puede manejar muchos clientes? | Sí, hasta ~1000 clientes simultáneos con la configuración actual. |

---

## 📜 Licencia

Distribuido bajo la licencia **(DEFINIR NOMBRE)**. Consulta el archivo `LICENSE` para más detalles.

---

