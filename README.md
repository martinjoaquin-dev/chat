# 🔐 Chat TCP Asíncrono con Cifrado Simétrico

Un sistema de chat cliente-servidor TCP **asíncrono** con cifrado simétrico robusto implementado en Python. Utiliza `asyncio` para manejo eficiente de múltiples conexiones simultáneas.

## 🚀 Características

### Seguridad
- **Cifrado AES-256-GCM**: Cifrado autenticado de grado militar
- **HMAC-SHA256**: Verificación adicional de integridad del payload cifrado
- **SHA256 Hash**: Verificación de integridad del mensaje descifrado (nuevo en v2.0)
- **PBKDF2**: Derivación segura de claves desde contraseñas
- **Protección contra tampering**: Detección automática de mensajes alterados
- **IV aleatorio**: Cada mensaje usa un vector de inicialización único

### Funcionalidades
- ✅ **Arquitectura asíncrona** con asyncio (v2.0)
- ✅ Comunicación TCP en tiempo real no bloqueante
- ✅ Cifrado/descifrado transparente
- ✅ **Visualización de datos cifrados** en tiempo real
- ✅ Logging rotativo con archivos de respaldo
- ✅ Manejo robusto de errores
- ✅ Interfaz de línea de comandos configurable
- ✅ Soporte para **miles de clientes simultáneos** (mejorado en v2.0)
- ✅ **Scripts de demostración** del cifrado
- ✅ Hash SHA256 de mensajes para auditoría

## 🏗️ Arquitectura

### Protocolo de Cifrado
```
Mensaje cifrado:
[4 bytes: longitud total]
[12 bytes: IV (nonce)]
[16 bytes: tag de autenticación GCM]
[32 bytes: HMAC-SHA256]
[resto: ciphertext AES-256-GCM]
```

### Flujo de Comunicación
1. **Cliente** → Cifra mensaje con AES-256-GCM + HMAC, calcula hash SHA256
2. **Red** → Transmisión segura de datos cifrados
3. **Servidor** → Verifica HMAC y descifra con AES-256-GCM
4. **Servidor** → Calcula y verifica hash SHA256 del mensaje descifrado
5. **Log** → Almacena mensaje descifrado con hash SHA256 para auditoría

## 📦 Instalación

### Requisitos
- Python 3.7+
- pip (gestor de paquetes)

### Dependencias
```bash
pip install -r requirements.txt
```

### Dependencias incluidas
- `cryptography>=41.0.0`: Librería criptográfica de alto nivel

## 🚀 Uso

### 1. Iniciar el Servidor
```bash
python server.py
```

**Opciones del servidor:**
```bash
python server.py --host 0.0.0.0 --port 9000 --password mi_clave_secreta
```

**Parámetros:**
- `--host`: IP de escucha (default: 0.0.0.0)
- `--port`: Puerto de escucha (default: 9000)
- `--password`: Contraseña para cifrado (default: chat_secret_key_2024)
- `--log-file`: Archivo de log (default: chat.log)
- `--max-bytes`: Tamaño máximo del log (default: 5MB)
- `--backups`: Número de archivos de respaldo (default: 3)

### 2. Conectar Cliente
```bash
python client.py
```

**Opciones del cliente:**
```bash
python client.py --host 127.0.0.1 --port 9000 --password mi_clave_secreta
```

**Parámetros:**
- `--host`: IP del servidor (default: 127.0.0.1)
- `--port`: Puerto del servidor (default: 9000)
- `--password`: Contraseña para cifrado (default: chat_secret_key_2024)

### 3. Ejemplo de Uso
```bash
# Terminal 1: Servidor
python server.py --password mi_super_clave_2024

# Terminal 2: Cliente 1
python client.py --password mi_super_clave_2024

# Terminal 3: Cliente 2
python client.py --password mi_super_clave_2024
```

## 🔧 Configuración Avanzada

### Cambiar Contraseña
```bash
# Servidor con contraseña personalizada
python server.py --password "MiClaveSuperSecreta123!"

# Cliente con la misma contraseña
python client.py --password "MiClaveSuperSecreta123!"
```

### Configurar Logging
```bash
# Servidor con logs personalizados
python server.py --log-file mi_chat.log --max-bytes 10000000 --backups 5
```

## 🧪 Pruebas

### Probar Cifrado
   ```bash
python crypto_utils.py
   ```

### Ver Estructura del Cifrado
   ```bash
python mostrar_cifrado.py
```

### Probar Comunicación
1. Inicia el servidor
2. Conecta múltiples clientes
3. Envía mensajes desde diferentes clientes
4. **Observa los datos cifrados** en tiempo real
5. Verifica que aparezcan en el log del servidor

### Visualización en Tiempo Real
- **Cliente**: Muestra datos cifrados en hexadecimal
- **Servidor**: Muestra datos recibidos y descifrados
- **Estructura**: IV, Tag, HMAC, Ciphertext

## 🔒 Seguridad

### Algoritmos Utilizados
- **AES-256-GCM**: Cifrado simétrico de 256 bits con autenticación
- **HMAC-SHA256**: Verificación de integridad del payload cifrado con clave secreta
- **SHA256**: Hash de mensajes para verificación adicional de integridad (v2.0)
- **PBKDF2**: Derivación de claves con 100,000 iteraciones
- **Salt fijo**: Para desarrollo (cambiar en producción)

### Buenas Prácticas
- ✅ Usa contraseñas fuertes y únicas
- ✅ Cambia la contraseña regularmente
- ✅ No compartas la contraseña por canales inseguros
- ✅ Considera usar variables de entorno para contraseñas
- ✅ Monitorea los logs para actividad sospechosa

### Limitaciones Actuales
- ⚠️ Contraseña compartida predefinida (cambiar en producción)
- ⚠️ Salt fijo (implementar salt aleatorio en producción)
- ⚠️ No hay rotación automática de claves
- ⚠️ No hay autenticación de usuarios

## 📁 Estructura del Proyecto

```
chat/
├── server.py              # Servidor TCP asíncrono con descifrado (v2.0)
├── client.py              # Cliente TCP asíncrono con cifrado (v2.0)
├── crypto_utils.py        # Utilidades criptográficas (con SHA256)
├── mostrar_cifrado.py     # Script de demostración del cifrado
├── calcular_md5.py        # Script para calcular MD5 de archivos (v2.0)
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
├── README.txt            # Historial detallado de cambios (v2.0)
├── CONTROL_CAMBIOS.txt   # Documento de control de cambios (v2.0)
└── chat.log              # Logs del servidor (generado automáticamente)
```

## 🐛 Solución de Problemas

### Error: "No se pudo conectar"
- Verifica que el servidor esté ejecutándose
- Comprueba la IP y puerto
- Revisa el firewall

### Error: "Verificación HMAC falló"
- Asegúrate de usar la misma contraseña en cliente y servidor
- Verifica que no haya corrupción de datos en la red

### Error: "Datos cifrados demasiado cortos"
- El mensaje puede estar corrupto
- Verifica la integridad de la conexión

## 🔄 Versiones

### Versión 2.0 - Arquitectura Asíncrona (Actual)
- ✅ Migración completa a asyncio
- ✅ Servidor y cliente asíncronos
- ✅ Hash SHA256 de mensajes agregado
- ✅ Mejora significativa en escalabilidad
- ✅ Soporte para miles de conexiones simultáneas
- ✅ Mejor eficiencia de recursos

### Versión 1.0 - Versión Síncrona (Obsoleta)
- ✅ Cifrado simétrico AES-256-GCM + HMAC
- ✅ Cliente y servidor síncronos con threading
- ✅ Utilidades criptográficas completas

### Próximas Versiones
- 🔄 Autenticación de usuarios
- 🔄 Rotación automática de claves
- 🔄 Interfaz gráfica
- 🔄 Cifrado asimétrico opcional (RSA/ECDSA)

## 📚 Referencias Técnicas

- [AES-GCM Specification](https://tools.ietf.org/html/rfc5288)
- [HMAC Specification](https://tools.ietf.org/html/rfc2104)
- [PBKDF2 Specification](https://tools.ietf.org/html/rfc2898)
- [Cryptography Library](https://cryptography.io/)

## 📝 Control de Versiones

**Última actualización: 2025-11-19 (Versión 2.0)**

| Archivo           | MD5                                   | Fecha de cambio | Versión |
|-------------------|---------------------------------------|-----------------|---------|
| server.py         | `8e6483ab0156066a822851036bed0f91`    | 2025-11-19      | 2.0     |
| client.py         | `715e500ff50413e2181027b877657fbc`    | 2025-11-19      | 2.0     |
| crypto_utils.py   | `b552d4565126f25cfaeb87ff8e9bfa6a`    | 2025-11-19      | 2.0     |
| mostrar_cifrado.py| `c6ea27b39da48f363cfb2102994f33fd`    | 2025-10-22      | 1.0     |
| calcular_md5.py   | `1832f95ca60a02101473cee1e5434ba9`    | 2025-11-19      | 2.0     |
| README.md         | (verificar con calcular_md5.py)      | 2025-11-19      | 2.0     |

**Nota:** Para calcular MD5 de archivos actualizados, ejecutar: `python calcular_md5.py`

**Documentación adicional:**
- `README.txt`: Historial detallado de cambios
- `CONTROL_CAMBIOS.txt`: Documento para presentación con cliente

## 👥 Contribuciones

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

**⚠️ Advertencia de Seguridad**: Este es un proyecto educativo. Para uso en producción, implementa medidas de seguridad adicionales como autenticación de usuarios, rotación de claves, y auditoría de seguridad.