# 📖 GUÍA PASO A PASO - Sistema de Chat Seguro con Firma Digital

**Versión 6.0** | **Fecha: 2025-11-19**

---

## 📋 ÍNDICE

1. [Preparación Inicial](#1-preparación-inicial)
2. [Usar el Chat Seguro](#2-usar-el-chat-seguro)
3. [Usar el Servidor de Archivos y Firma Digital](#3-usar-el-servidor-de-archivos-y-firma-digital)
4. [Verificar Firmas](#4-verificar-firmas)
5. [Solución de Problemas](#5-solución-de-problemas)

---

## 1. PREPARACIÓN INICIAL

### Paso 1.1: Verificar que tienes todo instalado

```bash
# Verificar Python
python --version
# Debe mostrar: Python 3.7 o superior

# Verificar dependencias
pip install -r requirements.txt
```

### Paso 1.2: Verificar archivo .env

Abre el archivo `.env` y verifica que tenga estas variables:

```bash
# Configuración del servidor de chat
SERVER_HOST=0.0.0.0
SERVER_PORT=9000

# Configuración del cliente
CLIENT_HOST=127.0.0.1
CLIENT_PORT=9000

# SSL/TLS
SSL_ENABLED=true
SSL_CERT_FILE=certificates/server.crt
SSL_KEY_FILE=certificates/server.key
SSL_CA_FILE=certificates/ca.crt

# Servidor de archivos
UPLOAD_DIR=uploads
SIGNATURES_DIR=signatures
SIGNING_PRIVATE_KEY=signing_keys/signing_private_key.pem
SIGNING_PUBLIC_KEY=signing_keys/signing_public_key.pem
FILE_SERVER_HOST=0.0.0.0
FILE_SERVER_PORT=8080
MAX_FILE_SIZE=10485760
```

### Paso 1.3: Verificar certificados SSL

```bash
# Si no existen, generarlos:
python generate_ssl_cert.py
```

### Paso 1.4: Verificar claves de firma

```bash
# Si no existen, generarlas:
python -c "from digital_signature import generate_signing_key_pair; generate_signing_key_pair()"
```

---

## 2. USAR EL CHAT SEGURO

### Paso 2.1: Iniciar el Servidor de Chat

**Abre una terminal (Terminal 1):**

```bash
cd "C:\Users\anton\Seguridad informatica\chat"
python server.py
```

**Deberías ver:**
```
Servidor asincrono escuchando en 0.0.0.0:9000 (SSL/TLS)
Cifrado hibrido RSA + AES-256-GCM + HMAC + SHA256 activado
SSL/TLS activado: certificates/server.crt
Logs guardandose en: chat.log
Modo asincrono: Manejo eficiente de multiples clientes
Presiona Ctrl+C para detener el servidor
```

✅ **¡Servidor listo!** No cierres esta terminal.

### Paso 2.2: Conectar un Cliente

**Abre otra terminal (Terminal 2):**

```bash
cd "C:\Users\anton\Seguridad informatica\chat"
python client.py
```

**Deberías ver:**
```
Conectado a 127.0.0.1:9000 (SSL/TLS)
Intercambiando claves con el servidor...
Claves intercambiadas exitosamente
Cifrado hibrido RSA + AES-256-GCM + HMAC + SHA256 activado
SSL/TLS activado: Conexion de transporte cifrada
Escribe tu mensaje (o 'quit' para salir):
```

### Paso 2.3: Enviar Mensajes

**En la Terminal 2 (cliente), escribe mensajes:**

```
Escribe tu mensaje: Hola, este es un mensaje seguro
Escribe tu mensaje: Probando cifrado hibrido
Escribe tu mensaje: Mensaje con validacion SHA256
```

**En la Terminal 1 (servidor), verás:**
```
Cliente conectado: 127.0.0.1:XXXXX (SSL/TLS)
Hash SHA256 recibido: abc123...
Hash SHA256 calculado: abc123...
[VALIDACION EXITOSA] Hash SHA256 verificado correctamente
Mensaje recibido: Hola, este es un mensaje seguro
```

### Paso 2.4: Conectar Múltiples Clientes (Opcional)

**Abre una tercera terminal (Terminal 3):**

```bash
python client.py
```

Ahora tienes 2 clientes conectados al mismo servidor.

### Paso 2.5: Salir del Chat

**En cualquier cliente, escribe:**
```
quit
```

**Para detener el servidor:**
- Presiona `Ctrl+C` en la Terminal 1

---

## 3. USAR EL SERVIDOR DE ARCHIVOS Y FIRMA DIGITAL

### Paso 3.1: Iniciar el Servidor de Archivos

**Abre una terminal (Terminal 1):**

```bash
cd "C:\Users\anton\Seguridad informatica\chat"
python file_server.py
```

**Deberías ver:**
```
Firmador digital inicializado con clave: signing_keys/signing_private_key.pem
Servidor de archivos iniciando en 0.0.0.0:8080
Directorio de uploads: uploads
Directorio de firmas: signatures
Tamaño máximo de archivo: 10485760 bytes
Servicio de firma digital: ACTIVO

Servidor corriendo en http://0.0.0.0:8080
Endpoints disponibles:
  POST /upload - Subir y firmar archivo
  POST /verify - Verificar firma de archivo
  GET  /files - Listar archivos subidos
  GET  /health - Estado del servidor

Presiona Ctrl+C para detener
```

✅ **¡Servidor de archivos listo!** No cierres esta terminal.

### Paso 3.2: Crear un Archivo de Prueba

**Crea un archivo de texto:**

```bash
# Opción 1: Usando PowerShell
echo "Este es un documento importante para firmar" > documento.txt

# Opción 2: Crea el archivo manualmente con cualquier editor de texto
```

### Paso 3.3: Subir y Firmar un Archivo

**Opción A: Usando PowerShell (Windows)**

```powershell
# Subir archivo TXT
$filePath = "documento.txt"
$uri = "http://localhost:8080/upload"

# Crear el contenido multipart
$boundary = [System.Guid]::NewGuid().ToString()
$fileBytes = [System.IO.File]::ReadAllBytes($filePath)
$fileName = [System.IO.Path]::GetFileName($filePath)

$bodyLines = @(
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
    "Content-Type: application/octet-stream",
    "",
    [System.Text.Encoding]::GetEncoding('iso-8859-1').GetString($fileBytes),
    "--$boundary--"
) -join "`r`n"

$bodyBytes = [System.Text.Encoding]::GetEncoding('iso-8859-1').GetBytes($bodyLines)

Invoke-RestMethod -Uri $uri -Method Post -ContentType "multipart/form-data; boundary=$boundary" -Body $bodyBytes
```

**Opción B: Usando Python (Más fácil)**

Crea un archivo `subir_archivo.py`:

```python
import requests

# Subir archivo
file_path = "documento.txt"
url = "http://localhost:8080/upload"

with open(file_path, 'rb') as f:
    files = {'file': (file_path, f, 'application/octet-stream')}
    response = requests.post(url, files=files)

print("Status:", response.status_code)
print("Response:", response.json())
```

Ejecuta:
```bash
python subir_archivo.py
```

**Opción C: Usando curl (Si está instalado)**

```bash
curl -X POST -F "file=@documento.txt" http://localhost:8080/upload
```

### Paso 3.4: Ver la Respuesta

**Deberías recibir algo como:**

```json
{
  "success": true,
  "filename": "documento.txt",
  "size": 45,
  "signature_path": "signatures/documento.sig.json",
  "signature": {
    "file_path": "uploads/documento.txt",
    "signature": "abc123...",
    "hash": "def456...",
    "timestamp": "2025-11-19T13:22:22.550247",
    "algorithm": "RSA-PSS-SHA256"
  },
  "uploaded_at": "2025-11-19T13:22:22.573284"
}
```

✅ **¡Archivo subido y firmado exitosamente!**

### Paso 3.5: Verificar que se Guardaron los Archivos

```bash
# Ver archivo subido
dir uploads

# Ver firma generada
dir signatures
```

Deberías ver:
- `uploads/documento.txt` - El archivo original
- `signatures/documento.sig.json` - La firma digital

---

## 4. VERIFICAR FIRMAS

### Paso 4.1: Verificar Firma de un Archivo

**Opción A: Usando Python**

Crea `verificar_firma.py`:

```python
import requests
import json

# Verificar firma
filename = "documento.txt"
url = "http://localhost:8080/verify"

data = {
    'filename': filename
}

response = requests.post(
    url,
    json=data,
    headers={'Content-Type': 'application/json'}
)

print("Status:", response.status_code)
result = response.json()
print("Response:", json.dumps(result, indent=2))

if result.get('signature_valid'):
    print("\n[OK] Firma valida - El archivo no ha sido modificado")
else:
    print("\n[ERROR] Firma invalida - El archivo fue modificado")
```

Ejecuta:
```bash
python verificar_firma.py
```

**Opción B: Usando PowerShell**

```powershell
$uri = "http://localhost:8080/verify"
$body = @{
    filename = "documento.txt"
} | ConvertTo-Json

Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "application/json"
```

**Opción C: Usando curl**

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"filename":"documento.txt"}' \
  http://localhost:8080/verify
```

### Paso 4.2: Interpretar el Resultado

**Si la firma es válida:**
```json
{
  "filename": "documento.txt",
  "signature_valid": true,
  "verified_at": "2025-11-19T13:22:24.622334"
}
```
✅ **El archivo NO ha sido modificado desde que se firmó.**

**Si la firma es inválida:**
```json
{
  "filename": "documento.txt",
  "signature_valid": false,
  "verified_at": "2025-11-19T13:22:24.622334"
}
```
❌ **El archivo FUE MODIFICADO después de firmarse.**

### Paso 4.3: Listar Archivos Subidos

**Usando Python:**

```python
import requests

response = requests.get("http://localhost:8080/files")
print(response.json())
```

**Usando PowerShell:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8080/files" -Method Get
```

**Usando curl:**

```bash
curl http://localhost:8080/files
```

---

## 5. SOLUCIÓN DE PROBLEMAS

### Problema: "No se puede conectar al servidor"

**Solución:**
1. Verifica que el servidor esté corriendo
2. Verifica el puerto en `.env` (9000 para chat, 8080 para archivos)
3. Verifica que no haya firewall bloqueando

### Problema: "Servicio de firma no disponible"

**Solución:**
1. Verifica que existan las claves:
   ```bash
   dir signing_keys
   ```
2. Si no existen, genera las claves:
   ```bash
   python -c "from digital_signature import generate_signing_key_pair; generate_signing_key_pair()"
   ```

### Problema: "Error al firmar archivo PDF"

**Solución:**
1. Verifica que PyPDF2 esté instalado:
   ```bash
   pip install PyPDF2
   ```

### Problema: "SSL/TLS error"

**Solución:**
1. Genera certificados SSL:
   ```bash
   python generate_ssl_cert.py
   ```
2. O desactiva SSL temporalmente en `.env`:
   ```
   SSL_ENABLED=false
   ```

### Problema: "Archivo demasiado grande"

**Solución:**
1. Verifica `MAX_FILE_SIZE` en `.env` (default: 10MB)
2. Aumenta el valor si necesitas archivos más grandes

---

## 📝 RESUMEN RÁPIDO

### Para Chat:
1. `python server.py` (Terminal 1)
2. `python client.py` (Terminal 2)
3. Escribe mensajes y presiona Enter

### Para Firma Digital:
1. `python file_server.py` (Terminal 1)
2. Sube archivo con Python/curl/PowerShell
3. Verifica firma con Python/curl/PowerShell

---

## 🔗 ENDPOINTS DEL SERVIDOR DE ARCHIVOS

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Estado del servidor |
| POST | `/upload` | Subir y firmar archivo |
| POST | `/verify` | Verificar firma |
| GET | `/files` | Listar archivos |

---

**¿Necesitas más ayuda?** Revisa el `README.md` para documentación técnica completa.

