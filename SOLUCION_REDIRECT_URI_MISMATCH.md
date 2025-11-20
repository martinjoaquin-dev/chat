# 🔴 SOLUCIÓN: Error 400 redirect_uri_mismatch

Este error significa que el **redirect URI que envías a Google NO coincide** exactamente con el que tienes en Google Cloud Console.

---

## ✅ PASOS PARA SOLUCIONARLO

### 1. Verifica tu `.env` (ya está correcto)

Tu `.env` tiene:
```env
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

✅ Esto está correcto.

---

### 2. ACTUALIZA Google Cloud Console (ESTO ES LO QUE FALTA)

**Tienes que agregar este URI exacto en Google Cloud Console:**

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. **APIs & Services** > **Credentials**
3. Haz clic en tu **OAuth 2.0 Client ID**
4. En la sección **"URIs de redireccionamiento autorizados"**:

   **DEBES TENER ESTOS DOS URIs:**
   
   ```
   URI 1: http://localhost:8000/api/auth/google/callback   ← ESTE ES EL MÁS IMPORTANTE
   URI 2: http://localhost:4200/auth-callback               ← Este ya lo tienes
   ```

5. Si NO está el primero (`http://localhost:8000/api/auth/google/callback`):
   - Haz clic en **"+ Agregar URI"**
   - Escribe EXACTAMENTE (sin espacios, sin barra al final):
     ```
     http://localhost:8000/api/auth/google/callback
     ```
   - Presiona Enter

6. Haz clic en **"GUARDAR"** o **"SAVE"** (en la parte inferior)

---

### 3. Agregar tu Email como Test User (IMPORTANTE)

Si tu app está en **modo Testing**, necesitas agregar tu email:

1. Ve a **APIs & Services** > **OAuth consent screen**
2. Haz clic en **"Test users"** (en el menú lateral)
3. Haz clic en **"+ ADD USERS"**
4. Agrega tu email: `20233tn170@utez.edu.mx`
5. Haz clic en **"ADD"**
6. Haz clic en **"SAVE"**

---

### 4. Reiniciar el Servidor

Después de actualizar Google Cloud Console:

1. **Detén el servidor** (Ctrl + C)
2. **Inícialo nuevamente**:
   ```powershell
   python backend/api.py
   ```

---

## 🔍 Verificación

### En Google Cloud Console debe estar:

**"URIs de redireccionamiento autorizados":**
- `http://localhost:8000/api/auth/google/callback` ✅
- `http://localhost:4200/auth-callback` ✅

**"Test users"** (si tu app está en modo Testing):
- `20233tn170@utez.edu.mx` ✅

### En tu `.env` debe estar:

```env
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

✅ Ya lo tienes correcto.

---

## ⚠️ IMPORTANTE: Coincidencia Exacta

Los URIs deben coincidir **EXACTAMENTE**, carácter por carácter:

```
Google Cloud Console: http://localhost:8000/api/auth/google/callback
Tu .env:              http://localhost:8000/api/auth/google/callback
```

**Verifica que:**
- ❌ No tenga espacios al inicio o final
- ❌ No tenga barra al final (`/`)
- ❌ No tenga comillas extra en el `.env`
- ❌ No use `https://` en vez de `http://`
- ❌ No tenga el puerto incorrecto

---

## 📝 Resumen Rápido

1. ✅ Tu `.env` ya está correcto
2. 🔧 **AGREGA en Google Cloud Console**: `http://localhost:8000/api/auth/google/callback`
3. 👤 **AGREGA tu email** como test user: `20233tn170@utez.edu.mx`
4. 🔄 **REINICIA** el servidor backend

---

## 🎯 Después de Hacer los Cambios

Intenta iniciar sesión con Google nuevamente. El error `redirect_uri_mismatch` debería desaparecer.

¡Dime cuando hayas agregado el URI en Google Cloud Console y probamos de nuevo!

