# 🔐 Sistema de Chat Seguro con Firma Digital

**Versión 7.0** | **Frontend Angular + Backend Python**

Sistema completo de comunicación segura con cifrado híbrido (RSA + AES), SSL/TLS, firma digital de documentos y frontend moderno con Angular.

---

## 🚀 Inicio Rápido

### Requisitos Previos

- **Python 3.7+**
- **Node.js 18+** y **npm**
- **Angular CLI 17+** (instalar con `npm install -g @angular/cli`)

### Instalación Rápida

#### 1. Backend (Python)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Edita .env con tus configuraciones

# Generar certificados SSL (opcional)
python scripts/generate_ssl_cert.py
```

#### 2. Frontend (Angular)

```bash
# IMPORTANTE: Debes estar en la carpeta frontend/
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start
```

**⚠️ NOTA:** El `package.json` está en `frontend/`, NO en la raíz. Siempre ejecuta `npm install` y `npm start` desde dentro de `frontend/`.

#### 3. Iniciar Servicios

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

### Uso Rápido

1. **Iniciar Sesión**: Usa las credenciales de prueba (ej: `admin` / `admin123`)
2. **Enviar Mensajes**: Escribe en el campo de texto y presiona Enter o el botón de enviar
3. **Ver Historial**: El historial se carga automáticamente al entrar al chat
4. **Subir Archivos**: Ve a "Archivos" para subir y firmar documentos
5. **Finalizar Chat** (solo admin): Haz clic en "Finalizar Chat" para reiniciar el historial

---

## 🔐 Credenciales de Prueba

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `admin123` | Administrador (puede finalizar chat) |
| `usuario1` | `password1` | Usuario |
| `test` | `test123` | Usuario |
| `demo` | `demo123` | Usuario |

**Nota:** Solo el usuario `admin` tiene permisos para finalizar/reiniciar el chat.

---

## 📁 Estructura del Proyecto

```
chat/
├── frontend/              # Frontend Angular
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/    # Componentes (Login, Chat, Files, Dashboard)
│   │   │   ├── services/      # Servicios Angular
│   │   │   ├── guards/        # Guards de autenticación
│   │   │   └── interceptors/  # Interceptores HTTP
│   │   └── styles.scss
│   └── package.json          # ⚠️ npm install se ejecuta AQUÍ
│
├── backend/                 # API REST (FastAPI)
│   └── api.py
│
├── core/                    # Lógica principal
│   ├── server.py            # Servidor TCP/SSL
│   ├── client.py            # Cliente TCP/SSL
│   ├── file_server.py       # Servidor de archivos
│   ├── crypto_utils.py      # Utilidades criptográficas
│   ├── digital_signature.py # Firma digital
│   └── auth.py             # Autenticación
│
├── scripts/                 # Scripts auxiliares
│   ├── generate_ssl_cert.py
│   ├── calcular_md5.py
│   └── ...
│
├── docs/                    # Documentación adicional
│   ├── GUIA_USO.md
│   ├── GUIA_DESPLIEGUE_AWS.md
│   ├── CONTROL_CAMBIOS.txt
│   └── ...
│
├── certificates/            # Certificados SSL
├── uploads/                 # Archivos subidos
├── signatures/              # Firmas digitales
├── logs/                    # Logs del sistema
│
├── requirements.txt         # Dependencias Python
├── .env.example            # Ejemplo de variables de entorno
└── README.md               # Este archivo
```

---

## 🎨 Características

### Frontend Angular
- ✅ Diseño moderno y minimalista
- ✅ Angular Material para componentes UI
- ✅ Responsive design
- ✅ Buenas prácticas UX/UI (Nielsen's 12 Heuristics)
- ✅ **Autenticación OAuth 2.0 con Google (Authorization Code + PKCE)**
- ✅ Autenticación integrada con roles (admin/usuario)
- ✅ Chat en tiempo real con historial persistente
- ✅ Gestión de archivos con firma digital
- ✅ Notificaciones personalizadas (snackbars) con colores por tipo
- ✅ Modal de confirmación personalizado
- ✅ Funcionalidad de administración (finalizar chat)

### Backend Python
- ✅ **OAuth 2.0 con Google usando Authlib**
- ✅ **Verificación de tokens con JWKS (JSON Web Key Set)**
- ✅ **Flujo Authorization Code con PKCE**
- ✅ Cifrado híbrido (RSA + AES)
- ✅ Validación SHA256 obligatoria
- ✅ SSL/TLS para transporte seguro
- ✅ Firma digital de documentos
- ✅ API REST con FastAPI
- ✅ Arquitectura asíncrona
- ✅ Historial de mensajes con persistencia en JSON
- ✅ TTL (Time To Live) configurable para mensajes
- ✅ Límite de mensajes configurable
- ✅ Endpoints de administración (solo admin)
- ✅ Endpoints OAuth (/auth/google/login, /auth/google/callback, /auth/refresh)

---

## 🔒 Seguridad

### Algoritmos Utilizados
- **RSA-2048**: Cifrado asimétrico para intercambio seguro de claves
- **AES-256-GCM**: Cifrado simétrico autenticado para mensajes
- **HMAC-SHA256**: Verificación de integridad del payload
- **SHA256**: Hash de mensajes para verificación adicional
- **SSL/TLS**: Cifrado de transporte

### Características de Seguridad
- ✅ Validación SHA256 obligatoria en cada mensaje
- ✅ Doble capa de seguridad: SSL/TLS + Cifrado híbrido
- ✅ Sin contraseñas compartidas (intercambio de claves RSA)
- ✅ Firma digital RSA-PSS con SHA256
- ✅ Variables de entorno (sin valores hardcodeados)

---

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

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
SSL_CERT_FILE=certificates/server.crt
SSL_KEY_FILE=certificates/server.key

# Criptografía
HMAC_SALT=tu_salt_secreto_aqui

# Directorios
UPLOAD_DIR=uploads
SIGNATURES_DIR=signatures

# Historial de Mensajes (Opcional)
MESSAGE_HISTORY_FILE=chat_history.json  # Archivo donde se guarda el historial
MESSAGE_TTL_HOURS=24                   # Horas antes de eliminar mensajes (0 = sin límite)
MESSAGE_MAX_COUNT=1000                  # Máximo de mensajes a mantener

# OAuth 2.0 con Google (Requerido para autenticación OAuth)
GOOGLE_CLIENT_ID=tu_google_client_id_aqui
GOOGLE_CLIENT_SECRET=tu_google_client_secret_aqui
GOOGLE_REDIRECT_URI=http://localhost:4200/auth-callback
GOOGLE_SCOPES="openid email profile"
GOOGLE_DISCOVERY=https://accounts.google.com/.well-known/openid-configuration
```

### 🔐 Configuración OAuth 2.0 con Google

El proyecto incluye integración completa con OAuth 2.0 usando Google como proveedor de identidad. Para configurar OAuth:

#### 1. Crear un Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **Google+ API** o **Google Identity Platform**

#### 2. Configurar OAuth 2.0 Credentials

1. Ve a **APIs & Services** > **Credentials**
2. Haz clic en **Create Credentials** > **OAuth 2.0 Client ID**
3. Si es la primera vez, configura la **OAuth consent screen**:
   - Selecciona **External** (para desarrollo) o **Internal** (para G Suite)
   - Completa la información requerida (nombre de la app, email de soporte, etc.)
   - En **Scopes**, añade `openid`, `email`, `profile`
   - Añade test users si es necesario (para modo de prueba)

4. Crea el **OAuth 2.0 Client ID**:
   - **Application type**: Web application
   - **Name**: Chat Seguro (o el nombre que prefieras)
   - **Authorized JavaScript origins**:
     - `http://localhost:4200`
     - `http://localhost:8000` (para desarrollo)
   - **Authorized redirect URIs**:
     - `http://localhost:4200/auth-callback`
     - `http://localhost:8000/api/auth/google/callback` (para el backend)

5. Copia el **Client ID** y **Client Secret** generados

#### 3. Configurar Variables de Entorno

Edita tu archivo `.env` y añade:

```env
GOOGLE_CLIENT_ID=tu_client_id_aqui.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu_client_secret_aqui
GOOGLE_REDIRECT_URI=http://localhost:4200/auth-callback
GOOGLE_SCOPES="openid email profile"
GOOGLE_DISCOVERY=https://accounts.google.com/.well-known/openid-configuration
```

**📚 ¿Necesitas ayuda con la configuración?** 
- ⚡ **¿Tienes prisa?** → [Resumen Rápido OAuth](docs/RESUMEN_RAPIDO_OAUTH.md) (3 pasos esenciales)
- 📖 **¿Quieres detalles?** → [Guía Completa de Configuración OAuth](docs/CONFIGURACION_OAUTH.md) (paso a paso con ejemplos)
- 🔍 **¿No encuentras OAuth Consent Screen?** → [Solución: No encuentro OAuth](docs/SOLUCION_NO_ENCUENTRO_OAUTH.md) (métodos alternativos)

**⚠️ NOTA**: Para OAuth básico (email + perfil), **NO necesitas habilitar APIs adicionales** en Google Cloud Console. Puedes saltar directamente a configurar el OAuth Consent Screen.

#### 4. Características de OAuth 2.0 Implementadas

- ✅ **Authorization Code Flow con PKCE**: Flujo seguro con Proof Key for Code Exchange
- ✅ **Verificación de Tokens con JWKS**: Verificación automática de id_token usando JSON Web Key Set
- ✅ **Refresh Token**: Renovación automática de access_token cuando expira
- ✅ **Discovery Document**: Conexión automática al discovery document de Google
- ✅ **Compatibilidad Dual**: Funciona junto con autenticación tradicional (username/password)

#### 5. Endpoints OAuth Disponibles

- `GET /api/auth/google/login`: Inicia el flujo OAuth y devuelve la URL de autorización
- `GET /api/auth/google/callback`: Callback que recibe el código de autorización de Google
- `POST /api/auth/refresh`: Refresca un access_token usando un refresh_token
- `GET /api/auth/oauth/me`: Obtiene información del usuario autenticado con OAuth

#### 6. Uso en el Frontend

El frontend Angular incluye:
- Botón "Iniciar sesión con Google" en la pantalla de login
- Componente `AuthCallbackComponent` que maneja la redirección de Google
- Interceptor HTTP que añade automáticamente el token Bearer a las peticiones
- Guard que protege rutas y verifica autenticación (tradicional u OAuth)

---

## 💡 Funcionalidades Principales

### Historial de Mensajes
- Los mensajes se guardan automáticamente en `chat_history.json`
- El historial persiste entre reinicios del servidor
- Los mensajes antiguos se eliminan automáticamente según el TTL configurado
- El historial se carga automáticamente al navegar entre secciones

### Funcionalidad de Administración
- El usuario `admin` puede finalizar/reiniciar el chat
- Al finalizar, se eliminan todos los mensajes del historial
- Se muestra un modal de confirmación antes de eliminar
- Solo disponible para usuarios con rol de administrador

### Notificaciones
- Mensajes de éxito: Verde (operaciones exitosas)
- Mensajes de advertencia: Naranja (advertencias)
- Mensajes de error: Rojo (errores)
- Aparecen en la esquina superior derecha
- Diseño minimalista y moderno

---
## 🐛 Solución de Problemas

### Error: "Could not read package.json"
**Solución:** Debes ejecutar `npm install` desde dentro de `frontend/`:
```bash
cd frontend
npm install
```

### Error: "Module not found" (Python)
**Solución:** Instala las dependencias:
```bash
pip install -r requirements.txt
```

### Frontend no se conecta a la API
**Solución:**
1. Verifica que `backend/api.py` esté corriendo en el puerto 8000
2. Revisa la consola del navegador para errores CORS
3. Verifica que la URL de la API en los servicios Angular sea correcta

### Error: "Port already in use"
**Solución:** Cambia los puertos en `.env` o cierra los procesos que están usando esos puertos.

---

## 📚 Documentación Adicional

- [Guía de Uso](docs/GUIA_USO.md) - Instrucciones detalladas de uso
- [Guía de Despliegue AWS](docs/GUIA_DESPLIEGUE_AWS.md) - Despliegue en AWS
- [Guía de VM Local](docs/GUIA_VM_LOCAL.md) - Despliegue en máquina virtual
- [Control de Cambios](docs/CONTROL_CAMBIOS.txt) - Historial de versiones
- [Resumen Ejecutivo](docs/RESUMEN_EJECUTIVO.md) - Documentación ejecutiva
- [Project Charter](docs/PROJECT_CHARTER.md) - Carta del proyecto
- [Presupuestos](docs/PRESUPUESTOS.md) - Análisis de costos

---

## 🔄 Versiones

| Versión | Fecha | Cambios Principales |
|---------|-------|---------------------|
| 7.0 | 2025-11-20 | Frontend Angular + API REST, Historial persistente, Funcionalidad admin |
| 6.0 | 2025-11-19 | Firma digital y servidor de archivos |
| 5.0 | 2025-11-19 | SSL/TLS y variables de entorno |
| 4.0 | 2025-11-19 | Validación SHA256 obligatoria |
| 3.0 | 2025-11-19 | Cifrado híbrido (RSA + AES) |

### 🔍 Verificación de Integridad (MD5)

Los MD5 de los archivos principales se documentan en `docs/CONTROL_CAMBIOS.txt` para control de versiones e integridad:

| Archivo | MD5 | Fecha |
|---------|-----|-------|
| `backend/api.py` | `5001e5cdfb8f827ea10ff48b63e37e18` | 2025-11-20 |
| `core/auth.py` | `468c0722cbd5c487e16680a94fdfa8d0` | 2025-11-19 |
| `core/server.py` | `68546676c84817304a76eaf3040ffb22` | 2025-11-19 |
| `core/client.py` | `bc78e8e9341a4177815133b0d89e2924` | 2025-11-19 |
| `core/crypto_utils.py` | `2fe800977b7e5b67185cf7a5c145f31c` | 2025-11-19 |
| `core/digital_signature.py` | `c953bd6d2cb0660280eb55ce3aa93ca0` | 2025-11-19 |
| `core/file_server.py` | `bb49604167130accc8ee6f0bb6114140` | 2025-11-19 |
| `scripts/calcular_md5.py` | `31af28b959f500400752d1d618426e42` | 2025-11-20 |

**Nota:** Para calcular los MD5 de todos los archivos, ejecuta:
```bash
python scripts/calcular_md5.py
```

Ver la tabla completa en `docs/CONTROL_CAMBIOS.txt`.

### Versión 7.0 - Detalles

#### Nuevas Funcionalidades
- ✅ **Historial de Mensajes Persistente**: Los mensajes se guardan en `chat_history.json` y persisten entre reinicios
- ✅ **TTL Configurable**: Los mensajes antiguos se eliminan automáticamente según el tiempo configurado
- ✅ **Límite de Mensajes**: Configuración para mantener solo los N mensajes más recientes
- ✅ **Funcionalidad Admin**: El usuario `admin` puede finalizar/reiniciar el chat
- ✅ **Modal Personalizado**: Diálogo de confirmación con diseño del sistema
- ✅ **Notificaciones Mejoradas**: Snackbars con colores (verde/naranja/rojo) y posición superior derecha
- ✅ **Carga Automática de Historial**: El historial se carga automáticamente al navegar entre secciones
- ✅ **Mejoras UX**: Iconos centrados, mejor espaciado, diseño más pulido

---

## 🛠️ Tecnologías

### Frontend
- Angular 17
- Angular Material
- angular-oauth2-oidc (OAuth 2.0 / OpenID Connect)
- TypeScript
- SCSS

### Backend
- Python 3.7+
- FastAPI (API REST)
- Authlib (OAuth 2.0 / OpenID Connect)
- PyJWT (Verificación de tokens JWT)
- asyncio (Servidor TCP)
- aiohttp (Servidor de archivos)
- cryptography (Cifrado)

---

## 🔍 Verificación de Integridad (MD5)

El proyecto incluye un script para verificar la integridad de los archivos mediante MD5:

```bash
# Calcular MD5 de todos los archivos .py
python scripts/calcular_md5.py
```

Este script:
- Calcula el hash MD5 de todos los archivos `.py` del proyecto
- Muestra los resultados en formato tabular
- Útil para verificar que los archivos no han sido modificados
- Los MD5 se documentan en `docs/CONTROL_CAMBIOS.txt` para control de versiones

**Nota:** Los MD5 de los archivos principales se documentan en `docs/CONTROL_CAMBIOS.txt` para referencia y control de integridad.

---

## 📝 Licencia

Este proyecto es de uso educativo y demostrativo.

---

**⚠️ Advertencia de Seguridad:** Este es un proyecto educativo. Para uso en producción, implementa medidas de seguridad adicionales como autenticación robusta, rotación de claves, y auditoría de seguridad.
