# 📦 Guía de Instalación - Versión 7.0

## Requisitos Previos

### Backend (Python)
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Frontend (Angular)
- Node.js 18 o superior
- npm (viene con Node.js)
- Angular CLI 17+

## Instalación Paso a Paso

### 1. Clonar o Descargar el Proyecto

```bash
cd "C:\Users\anton\Seguridad informatica\chat"
```

### 2. Instalar Dependencias del Backend

```bash
# Instalar dependencias Python
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env con tus configuraciones
# (O usar el editor de texto de tu preferencia)
```

**Variables importantes en `.env`:**
```env
# API REST
API_HOST=0.0.0.0
API_PORT=8000

# Servidor de Chat
SERVER_HOST=localhost
SERVER_PORT=8888

# Servidor de Archivos
FILE_SERVER_HOST=localhost
FILE_SERVER_PORT=8080

# SSL/TLS
SSL_ENABLED=false
```

### 4. Generar Certificados SSL (Opcional)

```bash
python scripts/generate_ssl_cert.py
```

### 5. Instalar Dependencias del Frontend

```bash
cd frontend
npm install
```

### 6. Instalar Angular CLI (si no lo tienes)

```bash
npm install -g @angular/cli
```

## Ejecutar el Sistema

### Opción 1: Ejecutar Todo Manualmente

**Terminal 1 - API REST:**
```bash
python backend/api.py
```
Debería iniciar en `http://localhost:8000`

**Terminal 2 - Servidor de Chat TCP:**
```bash
python core/server.py
```

**Terminal 3 - Servidor de Archivos:**
```bash
python core/file_server.py
```

**Terminal 4 - Frontend Angular:**
```bash
cd frontend
npm start
```
Abre `http://localhost:4200` en tu navegador.

### Opción 2: Scripts de Inicio (Recomendado)

Puedes crear scripts batch (.bat) o PowerShell (.ps1) para iniciar todos los servicios:

**start-backend.bat:**
```batch
@echo off
start "API REST" python backend/api.py
start "Chat Server" python core/server.py
start "File Server" python core/file_server.py
```

**start-frontend.bat:**
```batch
@echo off
cd frontend
npm start
```

## Verificar Instalación

1. **API REST**: Abre `http://localhost:8000/api/health` en tu navegador
   - Deberías ver: `{"status":"healthy",...}`

2. **Frontend**: Abre `http://localhost:4200`
   - Deberías ver la pantalla de login

3. **Login de Prueba**:
   - Usuario: `admin`
   - Contraseña: `admin123`

## Solución de Problemas

### Error: "Module not found"
- Asegúrate de haber ejecutado `pip install -r requirements.txt`
- Verifica que estás en el directorio correcto

### Error: "Port already in use"
- Cambia los puertos en `.env`
- O cierra los procesos que están usando esos puertos

### Frontend no se conecta a la API
- Verifica que `backend/api.py` esté corriendo
- Revisa la consola del navegador para errores CORS
- Asegúrate de que la URL de la API en los servicios Angular sea correcta

### Error de certificados SSL
- Genera certificados con `python scripts/generate_ssl_cert.py`
- O desactiva SSL en `.env` (`SSL_ENABLED=false`)

## Próximos Pasos

Una vez instalado y funcionando:
1. Lee la [Guía de Uso](docs/GUIA_USO.md)
2. Revisa la [Documentación Técnica](docs/README.md)
3. Explora las [Características de Seguridad](README.md#-seguridad)

