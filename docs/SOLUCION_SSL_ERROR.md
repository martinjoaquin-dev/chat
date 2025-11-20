# 🔒 Solución: Error de Certificado SSL con Google OAuth

Si ves este error:
```
ERROR:core.oauth:Error al cargar discovery document: [SSL: CERTIFICATE_VERIFY_FAILED] 
certificate verify failed: unable to get local issuer certificate
```

Significa que Python no puede verificar los certificados SSL de Google en tu sistema (común en Windows).

---

## ✅ Solución Rápida (Solo para Desarrollo)

Agrega esta variable a tu archivo `.env`:

```env
OAUTH_VERIFY_SSL=false
```

Esto deshabilitará la verificación SSL para las conexiones OAuth con Google.

⚠️ **IMPORTANTE**: Esta configuración es **solo para desarrollo**. En producción, siempre debes verificar SSL.

---

## 📋 Pasos para Corregir

### 1. Editar archivo `.env`

Abre tu archivo `.env` (en la raíz del proyecto) y agrega:

```env
# OAuth 2.0 con Google
GOOGLE_CLIENT_ID=tu_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu_client_secret
GOOGLE_REDIRECT_URI=http://localhost:4200/auth-callback
GOOGLE_SCOPES="openid email profile"
GOOGLE_DISCOVERY=https://accounts.google.com/.well-known/openid-configuration

# SSL Verification (false solo para desarrollo, true para producción)
OAUTH_VERIFY_SSL=false
```

### 2. Reiniciar el servidor

Después de agregar la variable, reinicia el servidor backend:

```bash
# Presiona Ctrl+C para detener el servidor
# Luego inícialo nuevamente:
python backend/api.py
```

---

## 🔐 Solución Permanente (Recomendada para Producción)

Para una solución permanente, puedes instalar los certificados SSL del sistema:

### En Windows:

1. **Descargar certificados de Python**:
   - Ve a: https://www.python.org/downloads/
   - Descarga e instala la versión de Python desde python.org (no desde Microsoft Store)
   - Los certificados deberían instalarse automáticamente

2. **O instalar certifi manualmente**:
   ```bash
   pip install --upgrade certifi
   ```

3. **Actualizar certificados en Python**:
   ```python
   import certifi
   import os
   os.environ['SSL_CERT_FILE'] = certifi.where()
   ```

### En Linux/Mac:

Los certificados generalmente se instalan automáticamente con el sistema operativo.

---

## ✅ Verificación

Después de agregar `OAUTH_VERIFY_SSL=false` al `.env`, intenta nuevamente iniciar sesión con Google.

Deberías ver en los logs:
```
INFO:core.oauth:Discovery document cargado exitosamente
INFO:core.oauth:JWKS cargado exitosamente
```

En lugar de:
```
ERROR:core.oauth:Error al cargar discovery document: [SSL: CERTIFICATE_VERIFY_FAILED]
```

---

## ⚠️ Seguridad

- **Desarrollo**: `OAUTH_VERIFY_SSL=false` está bien para desarrollo local
- **Producción**: Siempre usa `OAUTH_VERIFY_SSL=true` o elimina la variable (por defecto es `true`)
- **Nunca** deshabilites la verificación SSL en producción sin una razón muy válida

