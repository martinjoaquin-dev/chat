# 🔴 Solución: Error 400 redirect_uri_mismatch

Si ves este error de Google:
```
Error 400: redirect_uri_mismatch
Acceso bloqueado: la solicitud de esta aplicación no es válida
```

Significa que el **redirect URI que envías a Google NO coincide** exactamente con el que tienes configurado en Google Cloud Console.

---

## ✅ Solución Paso a Paso

### 1. Verificar el URI en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. **APIs & Services** > **Credentials**
3. Haz clic en tu **OAuth 2.0 Client ID**
4. Mira la sección **"URIs de redireccionamiento autorizados"**

**Debe tener EXACTAMENTE:**
```
http://localhost:8000/api/auth/google/callback
```

⚠️ **IMPORTANTE:**
- Sin espacios
- Sin barra al final (`/`)
- Exactamente como se muestra arriba
- Con `http://` (no `https://`)
- Con el puerto `8000`

---

### 2. Verificar el URI en tu `.env`

Tu archivo `.env` debe tener:

```env
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

**Verifica que:**
- No tenga espacios al inicio o final
- No tenga comillas (a menos que estén entre comillas dobles todo el valor)
- Coincida EXACTAMENTE con el de Google Cloud Console

---

### 3. Verificar que el Email esté en Test Users

Si tu app está en **modo Testing**, necesitas agregar tu email a los test users:

1. Ve a **APIs & Services** > **OAuth consent screen**
2. Haz clic en **"Test users"** (en el menú lateral o en la sección)
3. Haz clic en **"+ ADD USERS"**
4. Agrega tu email: `20233tn170@utez.edu.mx`
5. Haz clic en **"ADD"**
6. Haz clic en **"SAVE"**

---

### 4. Reiniciar el Servidor

Después de hacer los cambios:

1. **Detén el servidor** (Ctrl + C)
2. **Inícialo nuevamente**:
   ```powershell
   python backend/api.py
   ```

---

## 🔍 Verificación Detallada

### En Google Cloud Console:

Tu **"URIs de redireccionamiento autorizados"** debe verse así:

```
URI 1: http://localhost:8000/api/auth/google/callback
URI 2: http://localhost:4200/auth-callback  (opcional)
```

### En tu `.env`:

```env
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

### Comparación:

```
Google Cloud Console:  http://localhost:8000/api/auth/google/callback
Tu .env:              http://localhost:8000/api/auth/google/callback
                      ✅ Deben ser IDÉNTICOS (carácter por carácter)
```

---

## 🐛 Errores Comunes

### ❌ Error 1: Espacio al final
```
Google Cloud: http://localhost:8000/api/auth/google/callback
Tu .env:      http://localhost:8000/api/auth/google/callback ← espacio al final
```

### ❌ Error 2: Barra al final
```
Google Cloud: http://localhost:8000/api/auth/google/callback
Tu .env:      http://localhost:8000/api/auth/google/callback/
```

### ❌ Error 3: https en vez de http
```
Google Cloud: http://localhost:8000/api/auth/google/callback
Tu .env:      https://localhost:8000/api/auth/google/callback
```

### ❌ Error 4: Puerto incorrecto
```
Google Cloud: http://localhost:8000/api/auth/google/callback
Tu .env:      http://localhost:8080/api/auth/google/callback
```

### ❌ Error 5: Path incorrecto
```
Google Cloud: http://localhost:8000/api/auth/google/callback
Tu .env:      http://localhost:8000/auth/google/callback  ← falta /api
```

---

## ✅ Checklist

Antes de intentar nuevamente, verifica:

- [ ] Google Cloud Console tiene: `http://localhost:8000/api/auth/google/callback`
- [ ] Tu `.env` tiene: `GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback`
- [ ] Ambos coinciden EXACTAMENTE (sin espacios, sin barras al final)
- [ ] Si tu app está en modo Testing, agregaste tu email a test users
- [ ] Reiniciaste el servidor backend después de cambiar `.env`

---

## 🔧 Solución Rápida

1. **Copia exactamente esto** (sin espacios, sin nada extra):
   ```
   http://localhost:8000/api/auth/google/callback
   ```

2. **Pégalo en Google Cloud Console**:
   - APIs & Services > Credentials > Tu OAuth Client ID
   - "URIs de redireccionamiento autorizados"
   - Haz clic en "+ Agregar URI" si no existe
   - Pega exactamente: `http://localhost:8000/api/auth/google/callback`
   - Haz clic en "GUARDAR"

3. **Pégalo en tu `.env`**:
   ```env
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
   ```
   (Sin espacios, sin comillas extra)

4. **Agrega tu email como test user** (si tu app está en modo Testing):
   - OAuth consent screen > Test users
   - Agrega: `20233tn170@utez.edu.mx`

5. **Reinicia el servidor**

---

## 🎯 Después de Corregir

Una vez corregido, intenta iniciar sesión con Google nuevamente. Deberías ver:
- ✅ Redirección a Google
- ✅ Pantalla de consentimiento
- ✅ Redirección de vuelta al backend
- ✅ Tokens recibidos en el frontend

¡Prueba de nuevo después de hacer estos cambios!

