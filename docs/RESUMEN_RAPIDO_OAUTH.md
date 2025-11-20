# ⚡ Resumen Rápido: Configuración OAuth 2.0 con Google

**¿No tienes tiempo para leer la guía completa?** Este es el resumen de los pasos esenciales.

---

## ✅ Pasos Mínimos Necesarios (3 pasos)

### 1️⃣ Crear Proyecto en Google Cloud
- Ve a [Google Cloud Console](https://console.cloud.google.com/)
- Crea un nuevo proyecto
- ⚠️ **SALTA el paso de habilitar APIs** - No es necesario para OAuth básico

### 2️⃣ Configurar OAuth Consent Screen (OBLIGATORIO)
- Ve a **APIs & Services** > **OAuth consent screen**
- Selecciona **External**
- Completa:
  - App name: `Chat Seguro`
  - User support email: tu email
  - Scopes: `openid`, `email`, `profile`
- Agrega test users (si tu app está en modo Testing)

### 3️⃣ Crear OAuth 2.0 Client ID (OBLIGATORIO)
- Ve a **APIs & Services** > **Credentials**
- **+ CREATE CREDENTIALS** > **OAuth client ID**
- Application type: **Web application**
- **Authorized redirect URIs**: `http://localhost:4200/auth-callback`
- **¡COPIA el Client ID y Client Secret!** (no podrás ver el secret después)

### 4️⃣ Configurar .env
Agrega al archivo `.env`:
```env
GOOGLE_CLIENT_ID=tu_client_id_que_copiaste.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-tu_secret_que_copiaste
GOOGLE_REDIRECT_URI=http://localhost:4200/auth-callback
GOOGLE_SCOPES="openid email profile"
GOOGLE_DISCOVERY=https://accounts.google.com/.well-known/openid-configuration
```

---

## ❌ Lo que NO necesitas

- ❌ Habilitar APIs (Google Identity Platform, People API, etc.)
- ❌ Cloud Identity
- ❌ Cloud Identity-Aware Proxy

**Para OAuth básico (email + perfil), solo necesitas:**
- ✅ Proyecto creado
- ✅ OAuth Consent Screen configurado
- ✅ OAuth 2.0 Client ID creado

---

## 📚 ¿Necesitas más detalles?

Consulta la [Guía Completa de Configuración OAuth](CONFIGURACION_OAUTH.md) para:
- Instrucciones paso a paso detalladas
- Capturas de pantalla y ejemplos
- Solución de problemas

