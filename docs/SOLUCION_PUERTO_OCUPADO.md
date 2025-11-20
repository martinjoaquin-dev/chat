# 🔧 Solución: Puerto 8000 Ocupado

Si ves este error:
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000): 
[winerror 10048] solo se permite un uso de cada dirección de socket
```

Significa que **otro proceso ya está usando el puerto 8000**.

---

## ✅ Solución Rápida

### Método 1: Cerrar el proceso que usa el puerto

1. **Identificar el proceso**:
   ```powershell
   netstat -ano | findstr :8000
   ```
   
   Esto mostrará algo como:
   ```
   TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       29312
   ```
   
   El último número (29312) es el **PID** (Process ID).

2. **Cerrar el proceso**:
   ```powershell
   taskkill /PID 29312 /F
   ```
   
   Reemplaza `29312` con el PID que encontraste.

3. **Verificar que se cerró**:
   ```powershell
   netstat -ano | findstr :8000
   ```
   
   Si no muestra nada, el puerto está libre.

4. **Ejecutar el servidor nuevamente**:
   ```powershell
   python backend/api.py
   ```

---

### Método 2: Usar otro puerto

Si prefieres usar otro puerto en lugar de cerrar el proceso:

1. **Edita el archivo `.env`**:
   ```env
   API_PORT=8001
   ```
   
   O cualquier otro puerto disponible (8001, 8002, etc.)

2. **Ejecuta el servidor**:
   ```powershell
   python backend/api.py
   ```

3. **Actualiza la URL del frontend** si es necesario:
   - En `frontend/src/app/services/auth.service.ts`
   - Cambia `http://localhost:8000` por `http://localhost:8001`

---

### Método 3: Cerrar todos los procesos de Python

Si hay múltiples instancias del servidor corriendo:

```powershell
# Ver todos los procesos de Python
tasklist | findstr python

# Cerrar todos los procesos de Python (¡CUIDADO!)
taskkill /IM python.exe /F
```

⚠️ **Advertencia**: Esto cerrará TODOS los procesos de Python que tengas corriendo.

---

## 🔍 Verificar qué está usando el puerto

Para ver más detalles sobre qué proceso está usando el puerto:

```powershell
# Ver el proceso con nombre
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess | ForEach-Object { Get-Process -Id $_.OwningProcess }
```

---

## 💡 Prevención

Para evitar este problema:

1. **Siempre cierra el servidor correctamente**: 
   - Presiona `Ctrl + C` en la terminal donde está corriendo
   - No cierres la ventana directamente

2. **Usa un script de inicio** que verifique si el puerto está libre antes de iniciar

3. **Usa variables de entorno** para el puerto para poder cambiarlo fácilmente

---

## ✅ Verificación

Después de cerrar el proceso, verifica que el puerto esté libre:

```powershell
netstat -ano | findstr :8000
```

Si **no muestra nada**, el puerto está libre y puedes ejecutar el servidor.

