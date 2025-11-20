# 🖥️ GUÍA COMPLETA: Desplegar en Máquina Virtual Local (VirtualBox)

**Versión:** 1.0  
**Fecha:** 2025-11-19  
**Tiempo estimado:** 1-2 horas  
**Dificultad:** ⭐⭐ (Fácil)

---

## 📋 TABLA DE CONTENIDOS

1. [Instalar VirtualBox](#1-instalar-virtualbox)
2. [Descargar Ubuntu Server](#2-descargar-ubuntu-server)
3. [Crear Máquina Virtual](#3-crear-máquina-virtual)
4. [Instalar Ubuntu Server](#4-instalar-ubuntu-server)
5. [Configurar Red y Port Forwarding](#5-configurar-red-y-port-forwarding)
6. [Conectar por SSH desde Windows](#6-conectar-por-ssh-desde-windows)
7. [Preparar el Servidor](#7-preparar-el-servidor)
8. [Subir el Código](#8-subir-el-código)
9. [Configurar la Aplicación](#9-configurar-la-aplicación)
10. [Configurar Servicio Systemd](#10-configurar-servicio-systemd)
11. [Probar el Servidor](#11-probar-el-servidor)
12. [Acceder desde tu Navegador](#12-acceder-desde-tu-navegador)

---

## 1. INSTALAR VIRTUALBOX

### Paso 1.1: Descargar VirtualBox

1. Ve a: https://www.virtualbox.org/wiki/Downloads
2. Haz clic en **"Windows hosts"** para descargar
3. El archivo se llamará algo como: `VirtualBox-7.x.x-xxxxx-Win.exe`

### Paso 1.2: Instalar VirtualBox

1. Ejecuta el instalador descargado
2. Haz clic en **"Next"** (Siguiente)
3. Acepta los términos y haz clic en **"Next"**
4. **IMPORTANTE:** Deja marcadas todas las opciones (USB, red, etc.)
5. Te preguntará si quieres instalar controladores de red → Haz clic en **"Yes"** (Sí)
6. Haz clic en **"Install"** (Instalar)
7. Espera a que termine (puede tardar unos minutos)
8. Cuando termine, haz clic en **"Finish"**
9. **Reinicia tu computadora** si te lo pide

### Paso 1.3: Verificar Instalación

1. Busca "VirtualBox" en el menú de inicio
2. Abre **"Oracle VM VirtualBox Manager"**
3. Si se abre sin errores, ¡perfecto!

---

## 2. DESCARGAR UBUNTU SERVER

### Paso 2.1: Descargar ISO

1. Ve a: https://ubuntu.com/download/server
2. Haz clic en **"Download"** (botón grande)
3. Se descargará un archivo `.iso` (aproximadamente 2-3 GB)
4. **Anota dónde se guardó** (normalmente en `Downloads`)

**Nombre del archivo:** `ubuntu-22.04.x-live-server-amd64.iso` (o similar)

### Paso 2.2: Verificar Descarga

- El archivo debe tener extensión `.iso`
- El tamaño debe ser aproximadamente 2-3 GB
- Si no se descargó completo, vuelve a intentar

---

## 3. CREAR MÁQUINA VIRTUAL

### Paso 3.1: Abrir VirtualBox

1. Abre **Oracle VM VirtualBox Manager**

### Paso 3.2: Crear Nueva VM

1. Haz clic en el botón **"Nueva"** (arriba a la izquierda, icono de estrella)

### Paso 3.3: Nombre y Tipo

1. **Nombre:** `Chat Server` (o el que prefieras)
2. **Carpeta de máquinas:** Deja la predeterminada
3. **Tipo:** `Linux`
4. **Versión:** `Ubuntu (64-bit)`
5. Haz clic en **"Next"** (Siguiente)

### Paso 3.4: Memoria (RAM)

1. **Tamaño de memoria:** Arrastra el slider a **2048 MB** (2 GB)
   - O escribe `2048` en el campo
2. Haz clic en **"Next"**

**Nota:** Si tu PC tiene poca RAM, puedes usar 1024 MB (1 GB), pero 2 GB es mejor.

### Paso 3.5: Disco Duro

1. Selecciona **"Crear un disco duro virtual ahora"**
2. Haz clic en **"Create"** (Crear)

### Paso 3.6: Tipo de Archivo de Disco

1. Selecciona **"VDI (VirtualBox Disk Image)"**
2. Haz clic en **"Next"**

### Paso 3.7: Almacenamiento en Disco Físico

1. Selecciona **"Reservado dinámicamente"**
2. Haz clic en **"Next"**

### Paso 3.8: Ubicación y Tamaño

1. **Ubicación del archivo:** Deja la predeterminada
2. **Tamaño:** Arrastra a **20.00 GB** (o escribe `20`)
3. Haz clic en **"Create"** (Crear)

### Paso 3.9: Verificar Creación

Deberías ver tu nueva VM en la lista:
- Nombre: `Chat Server`
- Estado: `Powered Off`

---

## 4. INSTALAR UBUNTU SERVER

### Paso 4.1: Configurar la VM

1. Selecciona tu VM (`Chat Server`)
2. Haz clic en **"Configuración"** (Settings) o presiona `Ctrl+S`

### Paso 4.2: Configurar Almacenamiento

1. Ve a **"Storage"** (Almacenamiento) en el menú izquierdo
2. En **"Controller: IDE"**, haz clic en el icono de disco vacío
3. En **"Attributes"**, haz clic en el icono de disco (📀)
4. Haz clic en **"Choose a disk file..."**
5. Navega a donde descargaste Ubuntu Server (`.iso`)
6. Selecciona el archivo `.iso`
7. Haz clic en **"Open"**
8. Haz clic en **"OK"**

### Paso 4.3: Configurar Red (Importante)

1. En **"Configuración"**, ve a **"Network"** (Red)
2. **Adaptador 1:**
   - ✅ Marca **"Enable Network Adapter"**
   - **Attached to:** `NAT`
   - Haz clic en **"Advanced"** (Avanzado)
   - **Adapter Type:** `Intel PRO/1000 MT Desktop`
   - Haz clic en **"Port Forwarding"** (Reenvío de puertos)

3. **Agregar Reglas de Port Forwarding:**

   **Regla 1 - SSH:**
   - Haz clic en el icono **"+"** (agregar)
   - **Name:** `SSH`
   - **Protocol:** `TCP`
   - **Host IP:** `127.0.0.1` (o déjalo vacío)
   - **Host Port:** `2222`
   - **Guest IP:** (déjalo vacío)
   - **Guest Port:** `22`
   - Haz clic en **"OK"**

   **Regla 2 - HTTP (Servidor):**
   - Haz clic en el icono **"+"** (agregar)
   - **Name:** `HTTP`
   - **Protocol:** `TCP`
   - **Host IP:** `127.0.0.1` (o déjalo vacío)
   - **Host Port:** `8080`
   - **Guest IP:** (déjalo vacío)
   - **Guest Port:** `8080`
   - Haz clic en **"OK"**

   **Regla 3 - HTTP (Nginx):**
   - Haz clic en el icono **"+"** (agregar)
   - **Name:** `HTTP_Nginx`
   - **Protocol:** `TCP`
   - **Host IP:** `127.0.0.1` (o déjalo vacío)
   - **Host Port:** `80`
   - **Guest IP:** (déjalo vacío)
   - **Guest Port:** `80`
   - Haz clic en **"OK"**

4. Haz clic en **"OK"** para cerrar la configuración

### Paso 4.4: Iniciar la VM

1. Selecciona tu VM (`Chat Server`)
2. Haz clic en **"Iniciar"** (Start) o presiona `Enter`

### Paso 4.5: Instalador de Ubuntu

**La VM se iniciará y verás el instalador de Ubuntu Server.**

1. **Seleccionar idioma:**
   - Elige **"English"** o **"Español"**
   - Presiona `Enter`

2. **Actualizar instalador (si pregunta):**
   - Si pregunta si quieres actualizar, elige **"Continue without updating"** o **"Continuar sin actualizar"**

3. **Teclado:**
   - Selecciona tu distribución de teclado
   - Presiona `Enter`

4. **Tipo de instalación:**
   - Selecciona **"Ubuntu Server"**
   - Presiona `Enter`

5. **Configuración de red:**
   - Deja la configuración predeterminada
   - Presiona `Enter` para continuar

6. **Proxy (si aparece):**
   - Déjalo vacío
   - Presiona `Enter`

7. **Ubuntu archive mirror:**
   - Deja la predeterminada
   - Presiona `Enter`

8. **Storage configuration:**
   - Selecciona **"Use an entire disk"** o **"Usar un disco completo"**
   - Presiona `Enter`
   - Confirma con `Enter`

9. **Profile setup:**
   - **Your name:** `admin` (o el que prefieras)
   - **Server name:** `chat-server` (o el que prefieras)
   - **Username:** `admin` (o el que prefieras)
   - **Password:** `admin123` (o una contraseña segura - **ANÓTALA**)
   - Confirma la contraseña
   - Presiona `Enter`

10. **SSH Setup:**
    - ✅ **IMPORTANTE:** Marca **"Install OpenSSH server"**
    - Presiona `Enter`

11. **Featured Server Snaps:**
    - No selecciones nada (o selecciona lo que quieras)
    - Presiona `Enter` para continuar

12. **Instalación:**
    - Espera a que termine la instalación (10-20 minutos)
    - Verás el progreso en la pantalla

13. **Finalizar:**
    - Cuando termine, verás **"Reboot"** o **"Reiniciar"**
    - Presiona `Enter`
    - La VM se reiniciará

14. **Después del reinicio:**
    - Verás la pantalla de login
    - Ingresa tu **username:** `admin`
    - Ingresa tu **password:** `admin123` (o la que pusiste)
    - Presiona `Enter`

**¡Felicidades! Ubuntu Server está instalado.**

---

## 5. CONFIGURAR RED Y PORT FORWARDING

### Paso 5.1: Verificar IP de la VM

Dentro de la VM (después de hacer login), ejecuta:

```bash
ip addr show
```

Busca la línea que dice `inet` (ejemplo: `inet 10.0.2.15/24`)

**Anota esta IP** (será algo como `10.0.2.15`)

### Paso 5.2: Verificar que SSH Funciona

Dentro de la VM:

```bash
sudo systemctl status ssh
```

Debería mostrar `active (running)`

Si no está activo:
```bash
sudo systemctl start ssh
sudo systemctl enable ssh
```

---

## 6. CONECTAR POR SSH DESDE WINDOWS

### Paso 6.1: Abrir PowerShell en Windows

1. Presiona `Win + X`
2. Selecciona **"Windows PowerShell"** o **"Terminal"**

### Paso 6.2: Conectarte por SSH

```powershell
ssh admin@127.0.0.1 -p 2222
```

**O si prefieres usar la IP de la VM:**

```powershell
ssh admin@10.0.2.15
```

### Paso 6.3: Aceptar Fingerprint

La primera vez te preguntará:
```
The authenticity of host '127.0.0.1 (127.0.0.1)' can't be established.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Escribe: `yes` y presiona `Enter`

### Paso 6.4: Ingresar Contraseña

Te pedirá la contraseña:
```
admin@127.0.0.1's password:
```

Ingresa tu contraseña (`admin123` o la que pusiste) y presiona `Enter`

**¡Deberías estar conectado!** Verás algo como:
```
Welcome to Ubuntu 22.04.3 LTS...
admin@chat-server:~$
```

---

## 7. PREPARAR EL SERVIDOR

### Paso 7.1: Actualizar el Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

Esto puede tardar unos minutos.

### Paso 7.2: Instalar Python y Dependencias

```bash
sudo apt install python3 python3-pip python3-venv git -y
```

### Paso 7.3: Verificar Instalación

```bash
python3 --version
pip3 --version
git --version
```

Deberías ver las versiones instaladas.

### Paso 7.4: Instalar Nginx (Opcional pero Recomendado)

```bash
sudo apt install nginx -y
sudo systemctl status nginx
```

---

## 8. SUBIR EL CÓDIGO

Tienes 3 opciones:

### Opción A: Usando SCP (Desde PowerShell de Windows)

**En PowerShell de Windows (NUEVA ventana, no la SSH):**

```powershell
# Navegar a tu proyecto
cd "C:\Users\anton\Seguridad informatica\chat"

# Subir todo el proyecto
scp -r -P 2222 . admin@127.0.0.1:~/chat-server
```

Te pedirá la contraseña. Ingresa `admin123` (o la que pusiste).

### Opción B: Usando WinSCP (Más Fácil Visualmente)

1. Descarga WinSCP: https://winscp.net/eng/download.php
2. Instala WinSCP
3. Abre WinSCP
4. **Nueva sesión:**
   - **File protocol:** SFTP
   - **Host name:** `127.0.0.1`
   - **Port number:** `2222`
   - **User name:** `admin`
   - **Password:** `admin123`
   - Haz clic en **"Login"**
5. Arrastra todos los archivos de tu proyecto a `/home/admin/chat-server/`

### Opción C: Usando Git (Si tienes repositorio)

**Dentro de la VM (por SSH):**

```bash
cd ~
mkdir chat-server
cd chat-server
git clone https://tu-repositorio.git .
```

### Verificar que los Archivos Están

**Dentro de la VM (por SSH):**

```bash
cd ~/chat-server
ls -la
```

Deberías ver:
- `core/`
- `frontend/`
- `backend/`
- `scripts/`
- `requirements.txt`
- etc.

---

## 9. CONFIGURAR LA APLICACIÓN

### Paso 9.1: Instalar Dependencias Python

**Dentro de la VM (por SSH):**

```bash
cd ~/chat-server
pip3 install --user -r requirements.txt
```

### Paso 9.2: Crear Archivo .env

```bash
# Copiar el ejemplo
cp config/.env.example .env

# Editar el archivo
nano .env
```

**Configuración mínima en .env:**
```bash
# Servidor de archivos
FILE_SERVER_HOST=0.0.0.0
FILE_SERVER_PORT=8080
UPLOAD_DIR=uploads
SIGNATURES_DIR=signatures
SIGNING_PRIVATE_KEY=signing_keys/signing_private_key.pem
SIGNING_PUBLIC_KEY=signing_keys/signing_public_key.pem
MAX_FILE_SIZE=10485760
```

**Guardar:** `Ctrl+O`, `Enter`, `Ctrl+X`

### Paso 9.3: Crear Directorios

```bash
mkdir -p uploads signatures logs certificates signing_keys
```

### Paso 9.4: Generar Claves de Firma

```bash
python3 -c "from core.digital_signature import generate_signing_key_pair; generate_signing_key_pair()"
```

Deberías ver:
```
Par de claves generado:
  Clave privada: signing_keys/signing_private_key.pem
  Clave pública: signing_keys/signing_public_key.pem
```

### Paso 9.5: Probar que el Servidor Funciona

```bash
# Iniciar el servidor manualmente
python3 core/file_server.py
```

Deberías ver:
```
Firmador digital inicializado...
Servidor de archivos iniciando en 0.0.0.0:8080
...
Servidor corriendo en http://0.0.0.0:8080
```

**Presiona `Ctrl+C` para detener.**

---

## 10. CONFIGURAR SERVICIO SYSTEMD

### Paso 10.1: Crear Archivo de Servicio

```bash
sudo nano /etc/systemd/system/file-server.service
```

Pega este contenido:

```ini
[Unit]
Description=Servidor de Archivos y Firma Digital
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/chat-server
Environment="PATH=/usr/bin:/usr/local/bin:/home/admin/.local/bin"
ExecStart=/usr/bin/python3 /home/admin/chat-server/core/file_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**IMPORTANTE:** Ajusta `admin` si usaste otro usuario.

**Guardar:** `Ctrl+O`, `Enter`, `Ctrl+X`

### Paso 10.2: Recargar y Activar

```bash
sudo systemctl daemon-reload
sudo systemctl enable file-server
sudo systemctl start file-server
```

### Paso 10.3: Verificar Estado

```bash
sudo systemctl status file-server
```

Deberías ver `active (running)`

### Paso 10.4: Ver Logs

```bash
sudo journalctl -u file-server -f
```

**Presiona `Ctrl+C` para salir.**

---

## 11. PROBAR EL SERVIDOR

### Prueba 1: Desde la VM

**Dentro de la VM (por SSH):**

```bash
curl http://localhost:8080/health
```

Deberías recibir:
```json
{"status": "healthy", "signer_available": true, "timestamp": "..."}
```

### Prueba 2: Desde Windows

**En PowerShell de Windows:**

```powershell
curl http://127.0.0.1:8080/health
```

Deberías recibir la misma respuesta JSON.

---

## 12. ACCEDER DESDE TU NAVEGADOR

### Paso 12.1: Abrir Navegador

1. Abre tu navegador (Chrome, Firefox, Edge)
2. Ve a: `http://127.0.0.1:8080/health`
3. Deberías ver el JSON de respuesta

### Paso 12.2: Probar Endpoints

**Health Check:**
```
http://127.0.0.1:8080/health
```

**Listar Archivos:**
```
http://127.0.0.1:8080/files
```

**Subir Archivo (desde PowerShell):**
```powershell
# Crear archivo de prueba
echo "Test file" > test.txt

# Subirlo
curl -X POST -F "file=@test.txt" http://127.0.0.1:8080/upload
```

---

## ✅ CHECKLIST FINAL

- [ ] VirtualBox instalado
- [ ] Ubuntu Server instalado en la VM
- [ ] Port forwarding configurado (SSH, HTTP)
- [ ] Conexión SSH funcionando desde Windows
- [ ] Python y dependencias instalados
- [ ] Código subido a la VM
- [ ] Archivo .env configurado
- [ ] Claves de firma generadas
- [ ] Servidor funciona manualmente
- [ ] Servicio systemd creado y activo
- [ ] Acceso desde navegador funciona

---

## 🎉 ¡FELICIDADES!

Si llegaste hasta aquí, **tu servidor está funcionando en una máquina virtual local**.

**Próximos pasos opcionales:**
- Configurar Nginx como reverso proxy
- Configurar SSL/HTTPS
- Configurar backup automático

---

## 🔧 COMANDOS ÚTILES

```bash
# Ver estado del servicio
sudo systemctl status file-server

# Reiniciar servicio
sudo systemctl restart file-server

# Ver logs
sudo journalctl -u file-server -f

# Detener VM (desde VirtualBox)
# Cerrar VM (desde dentro)
sudo shutdown -h now
```

---

**¿Tienes problemas?** Revisa la sección de solución de problemas o pregunta.

