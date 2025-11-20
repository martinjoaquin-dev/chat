# 🔄 Explicación: ¿Por qué necesitas 2 Redirect URIs?

## 📋 Entendiendo el Flujo OAuth

### Flujo Completo:

```
1. Usuario → Frontend (hace clic en "Iniciar sesión con Google")
2. Frontend → Backend (/api/auth/google/login)
3. Backend → Google (con redirect_uri=http://localhost:8000/api/auth/google/callback)
4. Google → Backend (http://localhost:8000/api/auth/google/callback?code=XXX&state=YYY)
5. Backend intercambia código por tokens
6. Backend → Frontend (http://localhost:4200/auth-callback#access_token=ZZZ)
7. Frontend extrae tokens y autentica al usuario
```

---

## ✅ Configuración Correcta en Google Cloud Console

Necesitas tener **AMBOS** redirect URIs en Google Cloud Console:

### "Orígenes autorizados de JavaScript":
- `http://localhost:4200` ✅ (para el frontend Angular)

### "URIs de redireccionamiento autorizados":
Debes tener **AMBOS**:

1. **`http://localhost:8000/api/auth/google/callback`** ✅ 
   - **Este es el más importante**
   - Es donde Google redirige después de la autorización
   - El backend recibe el código aquí y lo intercambia por tokens

2. **`http://localhost:4200/auth-callback`** ✅ (opcional pero recomendado)
   - Es donde el backend redirige después de obtener los tokens
   - Solo para referencia, Google nunca redirigirá directamente aquí

---

## 📝 Cómo Configurarlo en Google Cloud Console

1. Ve a **APIs & Services** > **Credentials**
2. Haz clic en tu **OAuth 2.0 Client ID**
3. En **"URIs de redireccionamiento autorizados"**, asegúrate de tener:

   ```
   URI 1: http://localhost:8000/api/auth/google/callback  ← MÁS IMPORTANTE
   URI 2: http://localhost:4200/auth-callback              ← Opcional
   ```

4. Si no está el primero, haz clic en **"+ Agregar URI"** y agrégalo
5. Haz clic en **"GUARDAR"** o **"SAVE"**

---

## ⚙️ Configuración en .env

Tu `.env` debe tener:

```env
# Redirect URI para que Google sepa dónde enviar el código
# Este DEBE coincidir con uno de los URIs en Google Cloud Console
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

---

## 🔍 Verificación Rápida

| Componente | URI | ¿Quién lo usa? |
|------------|-----|----------------|
| Google Cloud Console | `http://localhost:8000/api/auth/google/callback` | Google (redirige aquí) |
| Google Cloud Console | `http://localhost:4200/auth-callback` | Backend (redirige aquí después) |
| `.env` | `http://localhost:8000/api/auth/google/callback` | Backend (le dice a Google) |

---

## ✅ Checklist

- [ ] En Google Cloud Console, tienes `http://localhost:8000/api/auth/google/callback` en "URIs de redireccionamiento"
- [ ] En `.env`, tienes `GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback`
- [ ] Ambos coinciden exactamente (sin espacios, sin `/` al final)
- [ ] Reiniciaste el servidor backend después de cambiar `.env`

---

## 🎯 Resumen Simple

**Google necesita saber dónde enviar el código después de que el usuario autoriza.**
- Debe ser el **backend** (`http://localhost:8000/api/auth/google/callback`)
- El backend intercambia el código por tokens
- Luego el backend redirige al **frontend** (`http://localhost:4200/auth-callback`) con los tokens

Por eso necesitas **ambos** URIs, pero el más importante es el del **backend**.

