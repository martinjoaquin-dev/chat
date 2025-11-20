# 📝 Guía Paso a Paso: Crear OAuth Client ID

Estás en la página **"Crear ID de cliente de OAuth"**. Sigue estos pasos exactos:

---

## ✅ Paso 1: Tipo de aplicación (Ya está correcto)

- **Campo**: "Tipo de aplicación *"
- **Valor actual**: "Aplicación web" ✅
- **Acción**: **NO CAMBIES NADA** - Ya está correcto

---

## ✅ Paso 2: Nombre del Cliente

- **Campo**: "Nombre *"
- **Valor actual**: "Cliente web 1" (prellenado)
- **Acción**: 
  - Puedes dejarlo así, O
  - Cambiarlo a algo más descriptivo como: `Chat Seguro Web Client`

---

## ✅ Paso 3: Orígenes autorizados de JavaScript

Esto define desde qué URL puede ejecutarse tu aplicación.

1. **Busca la sección**: "Orígenes autorizados de JavaScript"
2. **Haz clic en el botón azul**: **"+ Agregar URI"**
3. **Escribe** (o copia y pega):
   ```
   http://localhost:4200
   ```
4. **Presiona Enter** o haz clic fuera del campo
5. ✅ Verás que se agrega a la lista

---

## ✅ Paso 4: URIs de redirección autorizadas

Esto define a dónde Google redirigirá después del login. **ES MUY IMPORTANTE.**

1. **Busca la sección**: "URIs de redirección autorizadas" (puede estar más abajo)
   - Si no la ves, desplázate hacia abajo en la página
2. **Haz clic en el botón**: **"+ Agregar URI"**
3. **Escribe EXACTAMENTE** (copia y pega para evitar errores):
   ```
   http://localhost:4200/auth-callback
   ```
4. **Presiona Enter** o haz clic fuera del campo
5. ✅ Verás que se agrega a la lista

⚠️ **IMPORTANTE**: 
- Debe ser **EXACTAMENTE** así (con http, sin https)
- Sin espacios al inicio o final
- Con el puerto `4200`
- Con la ruta `/auth-callback`

---

## ✅ Paso 5: Crear el Cliente

1. **Desplázate hacia abajo** en la página
2. **Busca los botones** en la parte inferior:
   - "Cancelar" (Cancel)
   - **"CREAR"** o **"CREATE"** (botón azul)
3. **Haz clic en "CREAR"**

---

## 🎯 Resultado Esperado

Después de hacer clic en "CREAR", verás una **ventana modal** o **popup** con:

```
✅ Tu ID de cliente de OAuth 2.0 se ha creado

ID de cliente: 123456789-abcdefghijklmnop.apps.googleusercontent.com
Secreto de cliente: GOCSPX-abcdefghijklmnopqrstuvwxyz
```

**⚠️ MUY IMPORTANTE:**
1. **COPIA INMEDIATAMENTE** estos dos valores
2. **Guárdalos en un lugar seguro** (un archivo de texto, un documento)
3. **El "Secreto de cliente" NO podrás verlo nuevamente** después de cerrar esta ventana

---

## 📋 Checklist Antes de Crear

Antes de hacer clic en "CREAR", verifica que tengas:

- [ ] Tipo de aplicación: "Aplicación web" ✅
- [ ] Nombre: "Cliente web 1" o "Chat Seguro Web Client"
- [ ] Orígenes autorizados: `http://localhost:4200` agregado
- [ ] URIs de redirección: `http://localhost:4200/auth-callback` agregado

---

## ⚠️ Errores Comunes a Evitar

### ❌ Error: URI de redirección incorrecta
- ✅ Correcto: `http://localhost:4200/auth-callback`
- ❌ Incorrecto: `http://localhost:4200/auth-callback/` (con barra al final)
- ❌ Incorrecto: `https://localhost:4200/auth-callback` (con https)
- ❌ Incorrecto: `localhost:4200/auth-callback` (sin http://)

### ❌ Error: Origen JavaScript incorrecto
- ✅ Correcto: `http://localhost:4200`
- ❌ Incorrecto: `http://localhost:4200/` (con barra al final)
- ❌ Incorrecto: `https://localhost:4200` (con https)

---

## 🎉 Después de Crear

Una vez que tengas el **Client ID** y **Client Secret**, necesitas:

1. **Copiarlos** al archivo `.env` de tu proyecto
2. Actualizar estas variables:
   ```env
   GOOGLE_CLIENT_ID=el_id_que_copiaste.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-el_secret_que_copiaste
   ```

¡Ya casi terminamos! 🚀

