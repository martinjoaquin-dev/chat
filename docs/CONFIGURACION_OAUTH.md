# 🔐 Guía Paso a Paso: Configuración OAuth 2.0 con Google

Esta guía te explicará **paso a paso** cómo configurar OAuth 2.0 con Google Cloud Console y dónde obtener cada variable de entorno.

**⚡ ¿Tienes prisa?** Consulta el [Resumen Rápido](RESUMEN_RAPIDO_OAUTH.md) primero.

**⚠️ IMPORTANTE**: Para OAuth 2.0 básico (solo email y perfil), **NO necesitas habilitar APIs adicionales**. Puedes saltar el Paso 2.

---

## 📋 Índice

1. [Paso 1: Crear un Proyecto en Google Cloud Console](#paso-1-crear-un-proyecto-en-google-cloud-console)
2. [Paso 2: Habilitar APIs Necesarias](#paso-2-habilitar-apis-necesarias)
3. [Paso 3: Configurar OAuth Consent Screen](#paso-3-configurar-oauth-consent-screen)
4. [Paso 4: Crear OAuth 2.0 Client ID](#paso-4-crear-oauth-20-client-id)
5. [Paso 5: Configurar Variables de Entorno](#paso-5-configurar-variables-de-entorno)
6. [Paso 6: Verificar la Configuración](#paso-6-verificar-la-configuración)
7. [Solución de Problemas](#solución-de-problemas)

---

## Paso 1: Crear un Proyecto en Google Cloud Console

### 1.1 Acceder a Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. **Inicia sesión** con tu cuenta de Google
3. Si es tu primera vez, acepta los términos de servicio

### 1.2 Crear un Nuevo Proyecto

1. En la parte superior de la página, haz clic en el **selector de proyectos** (al lado del logo de Google Cloud)
2. Haz clic en **"NEW PROJECT"** (Nuevo Proyecto)
3. Completa el formulario:
   - **Project name**: `Chat Seguro` (o el nombre que prefieras)
   - **Project ID**: Se genera automáticamente (o personalízalo)
   - **Location**: Deja la opción "No organization" seleccionada
4. Haz clic en **"CREATE"** (Crear)
5. Espera unos segundos mientras se crea el proyecto
6. **Selecciona el proyecto** desde el selector de proyectos en la parte superior

✅ **Resultado**: Ahora tienes un proyecto de Google Cloud creado

---

## Paso 2: Habilitar APIs Necesarias (Opcional)

⚠️ **IMPORTANTE**: Para un flujo OAuth 2.0 básico con Google (solo obtener email y perfil del usuario), **NO es necesario habilitar ninguna API específica**. Puedes saltar este paso e ir directamente al [Paso 3: Configurar OAuth Consent Screen](#paso-3-configurar-oauth-consent-screen).

Solo necesitas habilitar APIs adicionales si quieres:
- Acceder a información adicional del usuario (calendario, contactos, etc.)
- Usar servicios específicos de Google (Gmail API, Drive API, etc.)

### Si Quieres Habilitar APIs Adicionales (Opcional):

Si necesitas acceso a información adicional del usuario, puedes habilitar:

1. **People API** (Recomendado - API moderna):
   - En el menú lateral izquierdo, ve a **"APIs & Services"** > **"Library"** (Biblioteca)
   - En la barra de búsqueda, busca: `People API`
   - Haz clic en el resultado **"People API"**
   - Haz clic en el botón **"ENABLE"** (Habilitar)

2. **O usar Cloud Identity** (si aparece en tu búsqueda):
   - **Cloud Identity** es para gestión empresarial de usuarios
   - Para OAuth 2.0 básico, **NO es necesario**

**Para este proyecto (OAuth básico):** Puedes **SALTAR este paso** y continuar al siguiente.

✅ **Resultado**: Si habilitaste una API, ahora está disponible en tu proyecto. Si no, no pasa nada, puedes continuar igual.

---

## Paso 3: Configurar OAuth Consent Screen

El **OAuth Consent Screen** es la pantalla que ven los usuarios cuando intentan iniciar sesión con Google.

⚠️ **IMPORTANTE**: Debes configurar el **OAuth Consent Screen ANTES** de crear el OAuth Client ID. Si intentas crear el Client ID sin haber configurado el consent screen, Google te mostrará una advertencia.

### 3.1 Ir a OAuth Consent Screen

**⚠️ Si no encuentras "OAuth Consent Screen", sigue estos pasos:**

#### Opción 1: Desde el banner amarillo (LA MÁS FÁCIL)

Si estás en la página de **"Credenciales"** (donde intentaste crear el Client ID), verás un **banner amarillo** arriba que dice:

> ⚠️ **"Recuerda configurar la pantalla de consentimiento de OAuth con información sobre tu app"**

1. **Busca ese banner amarillo** en la parte superior de la página
2. **Haz clic en el botón** **"Configurar pantalla de consentimiento"** (está en el banner amarillo)
3. Esto te llevará directamente a la configuración

#### Opción 2: Desde el menú lateral (si no ves el banner)

1. Mira el **menú lateral izquierdo** (la barra de navegación a la izquierda)
2. Busca la sección que dice **"APIs y servicios"** o **"APIs & Services"**
3. Dentro de esa sección, busca estas opciones:
   - "APIs y servicios habilitados" (o "Enabled APIs")
   - "Biblioteca" (o "Library")
   - **"Credenciales"** (o "Credentials") ← Estás aquí
   - **"Pantalla de consentimiento de OAuth"** ← **¡ESTA ES LA QUE BUSCAS!**
   - "Acuerdos de uso de páginas"

4. Si no ves **"Pantalla de consentimiento de OAuth"**, intenta:
   - **Expandir** la sección "APIs y servicios" (haz clic en la flecha si está colapsada)
   - **Desplazarte hacia abajo** en el menú (puede estar más abajo)
   - **Buscar en inglés**: "OAuth consent screen"

#### Opción 3: Usar la barra de búsqueda

1. En la parte **superior** de Google Cloud Console, hay una **barra de búsqueda**
2. Escribe: `OAuth consent screen` o `pantalla de consentimiento`
3. Haz clic en el primer resultado

#### Opción 4: URL directa (si nada funciona)

1. Copia y pega esta URL en tu navegador:
   ```
   https://console.cloud.google.com/apis/credentials/consent
   ```
2. Asegúrate de que estés en el proyecto correcto (el selector arriba debe decir "Chat Seguro")

#### ¿Qué deberías ver cuando llegues?

Cuando llegues a la página correcta, deberías ver:
- Título: **"Pantalla de consentimiento de OAuth"** o **"OAuth consent screen"**
- Un botón que dice **"CREATE"** o **"CREAR"** o **"CONFIGURAR"**
- Opciones para seleccionar el tipo de usuario (External/Internal)

**💡 CONSEJO**: Si aún no lo encuentras, haz clic en el **banner amarillo** de la página de Credenciales. Ese es el método más directo.

### 3.2 Seleccionar Tipo de Usuario

1. Selecciona **"External"** (para desarrollo/testing) o **"Internal"** (solo para usuarios de tu organización G Suite)
   - **Para desarrollo**: Selecciona **"External"**
2. Haz clic en **"CREATE"**

### 3.3 Completar Información de la Aplicación

Completa los campos obligatorios (marcados con *):

#### **App information** (Información de la aplicación):

- **App name** *: `Chat Seguro` (o el nombre que prefieras)
- **User support email** *: Tu email (ej: `tu-email@gmail.com`)
- **App logo**: (Opcional) Puedes subir un logo más adelante
- **Application home page**: `http://localhost:4200`
- **Application privacy policy link**: (Opcional para desarrollo)
- **Application terms of service link**: (Opcional para desarrollo)
- **Authorized domains**: (Déjalo vacío para desarrollo local)

#### **Developer contact information** (Información de contacto del desarrollador):

- **Email addresses** *: Tu email (ej: `tu-email@gmail.com`)

3. Haz clic en **"SAVE AND CONTINUE"** (Guardar y Continuar)

### 3.4 Configurar Scopes (Ámbitos)

Los **scopes** definen qué información puede solicitar tu aplicación.

1. En la sección **"Scopes"**, verás una lista de scopes comunes
2. Haz clic en **"ADD OR REMOVE SCOPES"**
3. Busca y marca los siguientes scopes:
   - ✅ `openid` (ya está por defecto)
   - ✅ `.../auth/userinfo.email` (email del usuario)
   - ✅ `.../auth/userinfo.profile` (perfil del usuario)
4. Haz clic en **"UPDATE"**
5. Haz clic en **"SAVE AND CONTINUE"**

✅ **Nota**: Los scopes `openid`, `email`, y `profile` son los mínimos necesarios.

### 3.5 Agregar Test Users (Solo para modo de prueba)

Si tu app está en **modo de prueba** (Testing), necesitas agregar usuarios de prueba:

1. En la sección **"Test users"**, haz clic en **"ADD USERS"**
2. Ingresa las direcciones de email de Google de los usuarios que quieres permitir
   - Ejemplo: `usuario@gmail.com`
   - Puedes agregar múltiples usuarios (uno por línea o separados por comas)
3. Haz clic en **"ADD"**
4. Haz clic en **"SAVE AND CONTINUE"**

✅ **Resultado**: Tu OAuth Consent Screen está configurado

---

## Paso 4: Crear OAuth 2.0 Client ID

Aquí es donde obtienes el **GOOGLE_CLIENT_ID** y **GOOGLE_CLIENT_SECRET**.

### 4.1 Ir a Credentials (Credenciales)

1. En el menú lateral izquierdo, ve a **"APIs & Services"** > **"Credentials"**
2. En la parte superior, haz clic en **"+ CREATE CREDENTIALS"**
3. Selecciona **"OAuth client ID"**

### 4.2 Seleccionar Application Type

1. Si te pregunta por el **Application type**, selecciona **"Web application"**
2. Haz clic en **"CREATE"**

### 4.3 Configurar OAuth Client

Completa el formulario:

#### **Name** (Nombre):
- **Name**: `Chat Seguro Web Client` (o el nombre que prefieras)

#### **Authorized JavaScript origins** (Orígenes JavaScript autorizados):
Estos son los dominios desde los que se puede hacer la petición OAuth.

Haz clic en **"+ ADD URI"** y agrega:
- `http://localhost:4200` (para el frontend Angular)
- `http://localhost:8000` (para el backend FastAPI, opcional)

#### **Authorized redirect URIs** (URIs de redirección autorizadas):
Estos son los endpoints donde Google redirige después de la autenticación.

Haz clic en **"+ ADD URI"** y agrega:
- `http://localhost:4200/auth-callback` (para el frontend)
- `http://localhost:8000/api/auth/google/callback` (para el backend, opcional)

✅ **Importante**: Las URIs deben coincidir **exactamente** con las que uses en tu código.

### 4.4 Crear y Obtener Credenciales

1. Haz clic en **"CREATE"** (Crear)
2. **¡Aparecerá una ventana modal con tus credenciales!** 👇

```
Your OAuth 2.0 Client has been created

Client ID: 123456789-abcdefghijklmnop.apps.googleusercontent.com
Client secret: GOCSPX-abcdefghijklmnopqrstuvwxyz
```

3. **¡COPIA ESTOS VALORES INMEDIATAMENTE!** 
   - Haz clic en el ícono de copiar junto a cada valor
   - O anótalos en un lugar seguro
   - ⚠️ **IMPORTANTE**: No podrás ver el Client Secret nuevamente después de cerrar esta ventana

4. Haz clic en **"OK"**

✅ **Resultado**: Ya tienes tu **GOOGLE_CLIENT_ID** y **GOOGLE_CLIENT_SECRET**

---

## Paso 5: Configurar Variables de Entorno

Ahora vamos a configurar las variables de entorno en tu proyecto.

### 5.1 Crear o Editar el Archivo `.env`

1. En la raíz de tu proyecto (donde está `backend/api.py`), busca el archivo `.env`
2. Si no existe, créalo:
   ```bash
   # En la raíz del proyecto
   touch .env
   # O en Windows, crea un archivo llamado ".env" en el explorador
   ```

### 5.2 Agregar Variables OAuth

Abre el archivo `.env` con un editor de texto y agrega las siguientes variables:

```env
# ==========================================
# OAuth 2.0 con Google
# ==========================================

# 🔑 Client ID: Lo obtuviste en el Paso 4.4
# Formato: xxxxxx-xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com

# 🔐 Client Secret: Lo obtuviste en el Paso 4.4
# Formato: GOCSPX-xxxxxxxxxxxxxxxx
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz

# 🌐 Redirect URI: URL donde Google redirige después del login
# Debe coincidir EXACTAMENTE con la configurada en Google Cloud Console (Paso 4.3)
GOOGLE_REDIRECT_URI=http://localhost:4200/auth-callback

# 📋 Scopes: Permisos que solicita tu aplicación
# Estos son los scopes mínimos: openid (identidad), email (correo), profile (perfil)
GOOGLE_SCOPES="openid email profile"

# 🔍 Discovery Document: URL del documento de descubrimiento de Google
# NO CAMBIAR ESTE VALOR - Es la URL oficial de Google
GOOGLE_DISCOVERY=https://accounts.google.com/.well-known/openid-configuration
```

### 5.3 Reemplazar Valores de Ejemplo

**Reemplaza los valores de ejemplo con tus valores reales:**

1. **GOOGLE_CLIENT_ID**: Reemplaza `123456789-abcdefghijklmnop.apps.googleusercontent.com` con el Client ID que copiaste en el Paso 4.4
   - Ejemplo: `GOOGLE_CLIENT_ID=987654321-zyxwvutsrqponml.apps.googleusercontent.com`

2. **GOOGLE_CLIENT_SECRET**: Reemplaza `GOCSPX-abcdefghijklmnopqrstuvwxyz` con el Client Secret que copiaste en el Paso 4.4
   - Ejemplo: `GOOGLE_CLIENT_SECRET=GOCSPX-qwertyuiopasdfghjklzxcvbnm`

3. **GOOGLE_REDIRECT_URI**: Normalmente no necesitas cambiarlo si usas `http://localhost:4200/auth-callback`
   - ⚠️ Debe coincidir **exactamente** con la URI configurada en Google Cloud Console

4. **GOOGLE_SCOPES**: No necesitas cambiarlo (a menos que quieras solicitar permisos adicionales)

5. **GOOGLE_DISCOVERY**: **NO LO CAMBIES** - Es la URL oficial de Google

### 5.4 Ejemplo de Archivo `.env` Completo

Tu archivo `.env` debería verse así (con tus valores reales):

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

# Historial de Mensajes
MESSAGE_HISTORY_FILE=chat_history.json
MESSAGE_TTL_HOURS=24
MESSAGE_MAX_COUNT=1000

# ==========================================
# OAuth 2.0 con Google
# ==========================================
GOOGLE_CLIENT_ID=987654321-zyxwvutsrqponml.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-qwertyuiopasdfghjklzxcvbnm
GOOGLE_REDIRECT_URI=http://localhost:4200/auth-callback
GOOGLE_SCOPES="openid email profile"
GOOGLE_DISCOVERY=https://accounts.google.com/.well-known/openid-configuration
```

✅ **Resultado**: Variables de entorno configuradas

---

## Paso 6: Verificar la Configuración

### 6.1 Verificar que el Archivo `.env` Esté Cargado

1. Asegúrate de que tu backend use `python-dotenv` para cargar variables de entorno
2. En tu código Python (ya está configurado), se carga automáticamente con:
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Esto carga el archivo .env
   ```

### 6.2 Verificar Variables en el Código

Abre `core/oauth.py` y verifica que estas líneas estén correctas:

```python
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:4200/auth-callback")
GOOGLE_SCOPES = os.getenv("GOOGLE_SCOPES", "openid email profile").split()
GOOGLE_DISCOVERY = os.getenv("GOOGLE_DISCOVERY", "https://accounts.google.com/.well-known/openid-configuration")
```

✅ **Ya está configurado en el código**

### 6.3 Probar la Configuración

1. **Inicia el backend**:
   ```bash
   python backend/api.py
   ```

2. **Inicia el frontend**:
   ```bash
   cd frontend
   npm start
   ```

3. **Abre tu navegador** en `http://localhost:4200`

4. **Haz clic en "Iniciar sesión con Google"**

5. **Deberías ver**:
   - Una redirección a Google
   - La pantalla de consentimiento OAuth (si no has iniciado sesión antes)
   - Una redirección de vuelta a tu aplicación con los tokens

---

## 📊 Resumen: Dónde Obtener Cada Variable

| Variable | Dónde Obtenerla | Formato de Ejemplo |
|----------|----------------|-------------------|
| **GOOGLE_CLIENT_ID** | Google Cloud Console > Credentials > OAuth Client ID | `123456789-abc.apps.googleusercontent.com` |
| **GOOGLE_CLIENT_SECRET** | Google Cloud Console > Credentials > OAuth Client ID (al crear) | `GOCSPX-abcdefghijklmnop` |
| **GOOGLE_REDIRECT_URI** | Lo defines tú (debe coincidir con Google Cloud Console) | `http://localhost:4200/auth-callback` |
| **GOOGLE_SCOPES** | Lo defines tú (valores estándar) | `"openid email profile"` |
| **GOOGLE_DISCOVERY** | URL oficial de Google (NO CAMBIAR) | `https://accounts.google.com/.well-known/openid-configuration` |

---

## ❓ Solución de Problemas

### Error: "redirect_uri_mismatch"

**Problema**: La URI de redirección no coincide.

**Solución**:
1. Verifica que `GOOGLE_REDIRECT_URI` en `.env` coincida **exactamente** con la configurada en Google Cloud Console
2. Ve a **Credentials** > Tu OAuth Client > **Authorized redirect URIs**
3. Asegúrate de que `http://localhost:4200/auth-callback` esté en la lista

### Error: "invalid_client"

**Problema**: El Client ID o Client Secret es incorrecto.

**Solución**:
1. Verifica que copiaste correctamente el `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET`
2. Asegúrate de que no haya espacios extra en el archivo `.env`
3. Si perdiste el Client Secret, deberás crear un nuevo OAuth Client ID

### Error: "access_denied"

**Problema**: El usuario no está en la lista de test users (si tu app está en modo Testing).

**Solución**:
1. Ve a **OAuth consent screen** > **Test users**
2. Agrega el email del usuario que intenta iniciar sesión

### Error: "scope_not_granted"

**Problema**: Los scopes solicitados no están configurados.

**Solución**:
1. Verifica que en **OAuth consent screen** > **Scopes** estén agregados:
   - `openid`
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`

### Las Variables de Entorno No Se Cargan

**Problema**: Python no está cargando el archivo `.env`.

**Solución**:
1. Asegúrate de tener instalado `python-dotenv`: `pip install python-dotenv`
2. Verifica que el archivo `.env` esté en la raíz del proyecto
3. Verifica que no haya un `.env.example` que se esté usando por error

---

## 🔒 Seguridad

### ⚠️ IMPORTANTE: Proteger tu Client Secret

1. **NUNCA** subas el archivo `.env` a un repositorio público (GitHub, etc.)
2. Agrega `.env` a tu `.gitignore`:
   ```
   .env
   ```
3. Usa `.env.example` (sin valores reales) para documentar qué variables se necesitan
4. En producción, usa variables de entorno del sistema o servicios de gestión de secretos (AWS Secrets Manager, etc.)

---

## ✅ Checklist Final

Antes de probar OAuth, verifica que tengas:

- [ ] Proyecto creado en Google Cloud Console
- [ ] OAuth Consent Screen configurado (obligatorio)
- [ ] OAuth 2.0 Client ID creado (obligatorio)
- [ ] Client ID y Client Secret copiados (obligatorio)
- [ ] Redirect URI agregada en Google Cloud Console: `http://localhost:4200/auth-callback` (obligatorio)
- [ ] Archivo `.env` creado con todas las variables (obligatorio)
- [ ] Valores reales en `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET` (obligatorio)
- [ ] API adicional habilitada (opcional, solo si necesitas funcionalidades extra)
- [ ] Backend iniciado sin errores
- [ ] Frontend iniciado sin errores

---

¡Ya deberías tener OAuth 2.0 completamente configurado! 🎉

Si tienes algún problema, revisa la sección de **Solución de Problemas** o verifica los logs del backend y del navegador.

