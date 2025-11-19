# 🔐 Chat TCP Asíncrono con Cifrado Híbrido y SSL/TLS

Un sistema de chat cliente-servidor TCP **asíncrono** con cifrado híbrido (RSA + AES) y SSL/TLS de grado empresarial implementado en Python. Utiliza `asyncio` para manejo eficiente de múltiples conexiones simultáneas. Configuración mediante variables de entorno sin valores hardcodeados.

## 🚀 Características

### Seguridad
- **Cifrado Híbrido**: RSA-2048 para intercambio de claves + AES-256-GCM para mensajes
- **SSL/TLS**: Cifrado de transporte para conexiones seguras (v5.0)
- **RSA-2048**: Cifrado asimétrico para intercambio seguro de claves AES
- **AES-256-GCM**: Cifrado simétrico autenticado de grado militar para mensajes
- **HMAC-SHA256**: Verificación adicional de integridad del payload cifrado
- **SHA256 Hash**: Verificación de integridad del mensaje descifrado
- **Intercambio de claves seguro**: Sin necesidad de compartir contraseñas
- **Protección contra tampering**: Detección automática de mensajes alterados
- **IV aleatorio**: Cada mensaje usa un vector de inicialización único
- **Variables de entorno**: Sin valores hardcodeados (v5.0)

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

### Protocolo de Cifrado Híbrido

**Fase 1: Intercambio de Claves (RSA)**
1. Cliente y servidor generan pares de claves RSA-2048
2. Intercambian claves públicas RSA
3. Cliente genera clave AES aleatoria y la cifra con la clave pública del servidor
4. Servidor descifra la clave AES con su clave privada RSA

**Fase 2: Cifrado de Mensajes (AES) con Validación SHA256**
```
Mensaje cifrado:
[4 bytes: longitud total]
[32 bytes: Hash SHA256 del mensaje original]
[12 bytes: IV (nonce)]
[16 bytes: tag de autenticación GCM]
[32 bytes: HMAC-SHA256]
[resto: ciphertext AES-256-GCM]
```

### Flujo de Comunicación
1. **Conexión** → Cliente y servidor intercambian claves públicas RSA
2. **Establecimiento de clave** → Cliente cifra clave AES con RSA y la envía al servidor
3. **Cliente** → Calcula hash SHA256 del mensaje original, cifra mensaje con AES-256-GCM + HMAC
4. **Cliente** → Envía hash SHA256 + mensaje cifrado al servidor
5. **Red** → Transmisión segura de datos cifrados con hash SHA256
6. **Servidor** → Extrae hash SHA256 recibido y datos cifrados
7. **Servidor** → Verifica HMAC y descifra con AES-256-GCM
8. **Servidor** → Calcula hash SHA256 del mensaje descifrado
9. **Servidor** → **VALIDACIÓN**: Compara hash recibido con hash calculado
10. **Servidor** → Si coinciden: acepta mensaje; si no: descarta mensaje
11. **Log** → Almacena mensaje descifrado con hash SHA256 para auditoría

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
- `python-dotenv>=1.0.0`: Gestión de variables de entorno (v5.0)

## 🚀 Uso

### Configuración Inicial

1. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   # Edita .env con tus valores
   ```

2. **Generar certificados SSL (para desarrollo):**
   ```bash
   python generate_ssl_cert.py
   ```
   
   **Nota:** Para producción, usa certificados de una CA válida (Let's Encrypt, etc.)

### 1. Iniciar el Servidor
```bash
python server.py
```

**Opciones del servidor:**
```bash
python server.py --host 0.0.0.0 --port 9000 --no-ssl
```

**Parámetros:**
- `--host`: IP de escucha (default: desde .env o 0.0.0.0)
- `--port`: Puerto de escucha (default: desde .env o 9000)
- `--log-file`: Archivo de log (default: desde .env o chat.log)
- `--max-bytes`: Tamaño máximo del log (default: desde .env o 5MB)
- `--backups`: Número de archivos de respaldo (default: desde .env o 3)
- `--no-ssl`: Deshabilitar SSL/TLS (usar TCP sin cifrado de transporte)

**Nota:** La configuración se lee desde el archivo `.env`. Los argumentos de línea de comandos tienen prioridad.

### 2. Conectar Cliente
```bash
python client.py
```

**Opciones del cliente:**
```bash
python client.py --host 127.0.0.1 --port 9000 --no-ssl
```

**Parámetros:**
- `--host`: IP del servidor (default: desde .env o 127.0.0.1)
- `--port`: Puerto del servidor (default: desde .env o 9000)
- `--no-ssl`: Deshabilitar SSL/TLS

**Nota:** El cliente genera automáticamente su par de claves RSA y establece la comunicación segura con el servidor.

### 3. Ejemplo de Uso
```bash
# Terminal 1: Servidor
python server.py

# Terminal 2: Cliente 1
python client.py

# Terminal 3: Cliente 2
python client.py
```

**Nota:** Cada cliente establece su propia conexión segura con intercambio automático de claves RSA. No se requiere contraseña compartida.

## 🔧 Configuración Avanzada

### Variables de Entorno

El proyecto usa variables de entorno para configuración. Crea un archivo `.env` basado en `.env.example`:

```bash
# Servidor
SERVER_HOST=0.0.0.0
SERVER_PORT=9000
LOG_FILE=chat.log
LOG_MAX_BYTES=5000000
LOG_BACKUPS=3

# Cliente
CLIENT_HOST=127.0.0.1
CLIENT_PORT=9000

# SSL/TLS
SSL_ENABLED=true
SSL_CERT_FILE=certificates/server.crt
SSL_KEY_FILE=certificates/server.key
SSL_CA_FILE=certificates/ca.crt

# Criptografía
HMAC_SALT=tu_salt_secreto_aqui
```

**Importante:** 
- Nunca commitees el archivo `.env` al repositorio
- Cambia `HMAC_SALT` por un valor aleatorio seguro en producción
- Para producción, usa certificados SSL de una CA válida

### Configurar SSL/TLS

**Para desarrollo (self-signed):**
```bash
python generate_ssl_cert.py
```

**Para producción:**
- Usa certificados de Let's Encrypt u otra CA válida
- Coloca los certificados en el directorio `certificates/`
- Actualiza las rutas en `.env`

### Configurar Logging
```bash
# Opción 1: Desde .env
LOG_FILE=mi_chat.log
LOG_MAX_BYTES=10000000
LOG_BACKUPS=5

# Opción 2: Desde línea de comandos
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
- **RSA-2048**: Cifrado asimétrico para intercambio seguro de claves (OAEP padding con SHA256)
- **AES-256-GCM**: Cifrado simétrico de 256 bits con autenticación para mensajes
- **HMAC-SHA256**: Verificación de integridad del payload cifrado
- **SHA256**: Hash de mensajes para verificación adicional de integridad
- **Claves RSA generadas dinámicamente**: Cada conexión tiene su propio par de claves

### Ventajas del Cifrado Híbrido
- ✅ **Sin contraseñas compartidas**: Cada conexión establece su propia clave AES de forma segura
- ✅ **Escalable**: Ideal para múltiples usuarios sin compartir secretos
- ✅ **Rápido**: AES para mensajes (rápido) + RSA solo para claves (pocas veces)
- ✅ **Seguro**: Combinación de lo mejor de cifrado simétrico y asimétrico
- ✅ **Autenticación**: Cada cliente tiene su propio par de claves RSA

### Validación SHA256 (v4.0)
- ✅ **Validación obligatoria**: Cada mensaje debe incluir hash SHA256 válido
- ✅ **Protección contra alteración**: Mensajes modificados son detectados y descartados
- ✅ **Integridad garantizada**: Solo se aceptan mensajes con hash SHA256 coincidente
- ✅ **Auditoría mejorada**: Logs registran intentos de mensajes inválidos

### Buenas Prácticas
- ✅ Monitorea los logs para actividad sospechosa
- ✅ Considera implementar autenticación de usuarios adicional
- ✅ Rotación periódica de claves RSA (implementar en producción)
- ✅ Almacenamiento seguro de claves privadas (si se persisten)

### SSL/TLS (v5.0)
- ✅ **Cifrado de transporte**: SSL/TLS protege la conexión TCP
- ✅ **Certificados self-signed**: Para desarrollo y pruebas
- ✅ **Soporte para CA válida**: Listo para certificados de producción
- ✅ **Configurable**: SSL puede habilitarse/deshabilitarse desde .env
- ✅ **Doble capa de seguridad**: SSL/TLS (transporte) + Cifrado híbrido (aplicación)

### Limitaciones Actuales
- ⚠️ No hay autenticación de usuarios (solo cifrado)
- ⚠️ No hay rotación automática de claves RSA
- ⚠️ Claves RSA se generan en memoria (no se persisten)
- ⚠️ Certificados SSL autofirmados solo para desarrollo (usar CA válida en producción)
- ⚠️ Certificados self-signed requieren aceptación manual del cliente

## 📁 Estructura del Proyecto

```
chat/
├── server.py              # Servidor TCP/SSL asíncrono con cifrado híbrido (v5.0)
├── client.py              # Cliente TCP/SSL asíncrono con cifrado híbrido (v5.0)
├── crypto_utils.py        # Utilidades criptográficas híbridas (RSA + AES)
├── generate_ssl_cert.py  # Script para generar certificados SSL (v5.0)
├── mostrar_cifrado.py     # Script de demostración del cifrado
├── calcular_md5.py        # Script para calcular MD5 de archivos
├── requirements.txt       # Dependencias Python
├── .env.example           # Ejemplo de variables de entorno (v5.0)
├── .gitignore            # Archivos ignorados por git
├── README.md             # Este archivo
├── README.txt            # Historial detallado de cambios
├── CONTROL_CAMBIOS.txt   # Documento de control de cambios
├── certificates/         # Directorio para certificados SSL (v5.0)
│   ├── server.crt        # Certificado del servidor
│   ├── server.key        # Clave privada del servidor
│   └── ca.crt            # Certificado CA (self-signed)
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

### Versión 5.0 - SSL/TLS y Variables de Entorno (Actual)
- ✅ Implementación de SSL/TLS para cifrado de transporte
- ✅ Variables de entorno reemplazan valores hardcodeados
- ✅ Removido hardening (valores fijos) en favor de configuración flexible
- ✅ Script generate_ssl_cert.py para certificados SSL self-signed
- ✅ Soporte para certificados de CA válida en producción
- ✅ Configuración centralizada en archivo .env
- ✅ HMAC_SALT configurable desde variables de entorno
- ✅ Doble capa de seguridad: SSL/TLS (transporte) + Cifrado híbrido (aplicación)

### Versión 4.0 - Validación SHA256 en Intercambio
- ✅ Validación obligatoria de SHA256 en cada mensaje
- ✅ Cliente envía hash SHA256 junto con mensaje cifrado
- ✅ Servidor valida hash SHA256 antes de aceptar mensaje
- ✅ Mensajes con hash no coincidente son descartados automáticamente
- ✅ Mayor protección contra mensajes alterados o corruptos
- ✅ Logs mejorados con información de validación

### Versión 3.0 - Cifrado Híbrido
- ✅ Migración a cifrado híbrido (RSA + AES)
- ✅ Intercambio automático de claves RSA-2048
- ✅ Sin necesidad de contraseñas compartidas
- ✅ Mayor seguridad y escalabilidad
- ✅ Ideal para múltiples usuarios
- ✅ Mantiene arquitectura asíncrona de v2.0

### Versión 2.0 - Arquitectura Asíncrona
- ✅ Migración completa a asyncio
- ✅ Servidor y cliente asíncronos
- ✅ Hash SHA256 de mensajes agregado
- ✅ Mejora significativa en escalabilidad
- ✅ Soporte para miles de conexiones simultáneas
- ✅ Cifrado simétrico con contraseña compartida

### Versión 1.0 - Versión Síncrona (Obsoleta)
- ✅ Cifrado simétrico AES-256-GCM + HMAC
- ✅ Cliente y servidor síncronos con threading
- ✅ Utilidades criptográficas completas

### Próximas Versiones
- 🔄 Autenticación de usuarios
- 🔄 Rotación automática de claves RSA
- 🔄 Interfaz gráfica
- 🔄 Persistencia segura de claves

## 📚 Referencias Técnicas

- [AES-GCM Specification](https://tools.ietf.org/html/rfc5288)
- [HMAC Specification](https://tools.ietf.org/html/rfc2104)
- [PBKDF2 Specification](https://tools.ietf.org/html/rfc2898)
- [Cryptography Library](https://cryptography.io/)

## 📝 Control de Versiones

**Última actualización: 2025-11-19 (Versión 5.0)**

| Archivo           | MD5                                   | Fecha de cambio | Versión |
|-------------------|---------------------------------------|-----------------|---------|
| server.py         | `348ebfd6dbfcf67f0deb930d6a3486ab`    | 2025-11-19      | 5.0     |
| server.py         | `ae21a882e1a6bac3ed008c28331295fd`    | 2025-11-19      | 4.0     |
| server.py         | `eb818069eeb98ff97b3da10d21f58b2f`    | 2025-11-19      | 3.0     |
| client.py         | `b07f5e3d3ccda837997644139c45c44b`    | 2025-11-19      | 5.0     |
| client.py         | `27e5385e75efcf34b63e2509e6448d2a`    | 2025-11-19      | 4.0     |
| client.py         | `ef87c47acbe985866e2666b94b36fc37`    | 2025-11-19      | 3.0     |
| crypto_utils.py   | `2fe800977b7e5b67185cf7a5c145f31c`    | 2025-11-19      | 5.0     |
| crypto_utils.py   | `6c26258132d8e030857d73d651d156a1`    | 2025-11-19      | 3.0     |
| generate_ssl_cert.py | `6e5d4821aabccd97433a0011b412dbe1`    | 2025-11-19      | 5.0     |
| mostrar_cifrado.py| `c6ea27b39da48f363cfb2102994f33fd`    | 2025-10-22      | 1.0     |
| calcular_md5.py   | `1832f95ca60a02101473cee1e5434ba9`    | 2025-11-19      | 2.0     |
| README.md         | (verificar con calcular_md5.py)       | 2025-11-19      | 4.0     |

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