# ⚠️ IMPORTANTE: Configuración de Redirect URI

## 🔴 Problema Común

Si ves el error **"No se recibieron tokens de autenticación"**, significa que el flujo OAuth no está configurado correctamente.

---

## ✅ Solución: Redirect URI debe apuntar al BACKEND

### Configuración Correcta

El **`GOOGLE_REDIRECT_URI`** debe apuntar al **BACKEND**, NO al frontend:

```env
# ✅ CORRECTO - Apunta al backend
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# ❌ INCORRECTO - Apunta al frontend (causará el error)
GOOGLE_REDIRECT_URI=http://localhost:4200/auth-callback
```

---

## 🔄 Flujo OAuth Correcto

1. **Frontend** → Usuario hace clic en "Iniciar sesión con Google"
2. **Frontend** → Llama a `/api/auth/google/login`
3. **Backend** → Genera URL de Google con `redirect_uri=http://localhost:8000/api/auth/google/callback`
4. **Usuario** → Es redirigido a Google y autoriza
5. **Google** → Redirige al **BACKEND** (`/api/auth/google/callback`) con el código
6. **Backend** → Intercambia código por tokens
7. **Backend** → Redirige al **FRONTEND** (`http://localhost:4200/auth-callback`) con tokens en el fragment
8. **Frontend** → Extrae tokens del fragment y los almacena

---

## 📝 Pasos para Corregir

### 1. Actualizar `.env`

Edita tu archivo `.env` y cambia:

```env
# Cambiar de esto:
GOOGLE_REDIRECT_URI=http://localhost:4200/auth-callback

# A esto:
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

### 2. Actualizar Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. **APIs & Services** > **Credentials**
3. Haz clic en tu **OAuth 2.0 Client ID**
4. En **"Authorized redirect URIs"**, asegúrate de tener:
   - `http://localhost:8000/api/auth/google/callback` ✅ (para el backend)
   - `http://localhost:4200/auth-callback` (para el frontend - solo para referencia, Google no redirigirá aquí)
5. Haz clic en **"SAVE"**

### 3. Reiniciar el Servidor

Después de cambiar el `.env`, reinicia el servidor backend:

```bash
# Presiona Ctrl+C para detener
python backend/api.py
```

---

## ✅ Verificación

Después de hacer estos cambios:

1. **Reinicia el backend**
2. **Intenta iniciar sesión con Google nuevamente**
3. **Deberías ver en los logs del backend**:
   ```
   INFO:core.oauth:Tokens obtenidos exitosamente para usuario: tu-email@gmail.com
   INFO:oauth_routes:Redirigiendo al frontend con tokens en fragment
   ```
4. **El frontend debería recibir los tokens** y redirigirte al chat

---

## 🔍 Diagnóstico

Si aún ves "No se recibieron tokens de autenticación":

1. **Verifica los logs del backend** - ¿Aparece el mensaje "Tokens obtenidos exitosamente"?
2. **Abre la consola del navegador** (F12) y mira la pestaña Network
3. **Verifica la URL del callback** - Debe tener tokens en el fragment (#access_token=...)
4. **Verifica que el redirect URI en Google Cloud Console coincida** exactamente con `http://localhost:8000/api/auth/google/callback`

---

## 📌 Resumen

- **Redirect URI en `.env`**: Debe ser `http://localhost:8000/api/auth/google/callback` (backend)
- **Redirect URI en Google Cloud**: Debe incluir `http://localhost:8000/api/auth/google/callback`
- **El frontend `auth-callback`**: Solo recibe tokens del backend, no de Google directamente

