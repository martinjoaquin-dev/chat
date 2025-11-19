# 🔐 Chat TCP Asíncrono con Cifrado Híbrido

Un sistema de chat cliente-servidor TCP **asíncrono** con cifrado híbrido (RSA + AES) de grado empresarial implementado en Python. Utiliza `asyncio` para manejo eficiente de múltiples conexiones simultáneas.

## 🚀 Características

### Seguridad
- **Cifrado Híbrido**: RSA-2048 para intercambio de claves + AES-256-GCM para mensajes
- **RSA-2048**: Cifrado asimétrico para intercambio seguro de claves AES
- **AES-256-GCM**: Cifrado simétrico autenticado de grado militar para mensajes
- **HMAC-SHA256**: Verificación adicional de integridad del payload cifrado
- **SHA256 Hash**: Verificación de integridad del mensaje descifrado
- **Intercambio de claves seguro**: Sin necesidad de compartir contraseñas
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

### Protocolo de Cifrado Híbrido

**Fase 1: Intercambio de Claves (RSA)**
1. Cliente y servidor generan pares de claves RSA-2048
2. Intercambian claves públicas RSA
3. Cliente genera clave AES aleatoria y la cifra con la clave pública del servidor
4. Servidor descifra la clave AES con su clave privada RSA

**Fase 2: Cifrado de Mensajes (AES)**
```
Mensaje cifrado:
[4 bytes: longitud total]
[12 bytes: IV (nonce)]
[16 bytes: tag de autenticación GCM]
[32 bytes: HMAC-SHA256]
[resto: ciphertext AES-256-GCM]
```

### Flujo de Comunicación
1. **Conexión** → Cliente y servidor intercambian claves públicas RSA
2. **Establecimiento de clave** → Cliente cifra clave AES con RSA y la envía al servidor
3. **Cliente** → Cifra mensaje con AES-256-GCM + HMAC, calcula hash SHA256
4. **Red** → Transmisión segura de datos cifrados
5. **Servidor** → Verifica HMAC y descifra con AES-256-GCM
6. **Servidor** → Calcula y verifica hash SHA256 del mensaje descifrado
7. **Log** → Almacena mensaje descifrado con hash SHA256 para auditoría

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
python server.py --host 0.0.0.0 --port 9000
```

**Parámetros:**
- `--host`: IP de escucha (default: 0.0.0.0)
- `--port`: Puerto de escucha (default: 9000)
- `--log-file`: Archivo de log (default: chat.log)
- `--max-bytes`: Tamaño máximo del log (default: 5MB)
- `--backups`: Número de archivos de respaldo (default: 3)

**Nota:** Ya no se requiere contraseña compartida. El sistema usa cifrado híbrido con intercambio automático de claves RSA.

### 2. Conectar Cliente
```bash
python client.py
```

**Opciones del cliente:**
```bash
python client.py --host 127.0.0.1 --port 9000
```

**Parámetros:**
- `--host`: IP del servidor (default: 127.0.0.1)
- `--port`: Puerto del servidor (default: 9000)

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

### Buenas Prácticas
- ✅ Monitorea los logs para actividad sospechosa
- ✅ Considera implementar autenticación de usuarios adicional
- ✅ Rotación periódica de claves RSA (implementar en producción)
- ✅ Almacenamiento seguro de claves privadas (si se persisten)

### Limitaciones Actuales
- ⚠️ No hay autenticación de usuarios (solo cifrado)
- ⚠️ No hay rotación automática de claves RSA
- ⚠️ Claves RSA se generan en memoria (no se persisten)

## 📁 Estructura del Proyecto

```
chat/
├── server.py              # Servidor TCP asíncrono con cifrado híbrido (v3.0)
├── client.py              # Cliente TCP asíncrono con cifrado híbrido (v3.0)
├── crypto_utils.py        # Utilidades criptográficas híbridas (RSA + AES)
├── mostrar_cifrado.py     # Script de demostración del cifrado
├── calcular_md5.py        # Script para calcular MD5 de archivos
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
├── README.txt            # Historial detallado de cambios
├── CONTROL_CAMBIOS.txt   # Documento de control de cambios
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

### Versión 3.0 - Cifrado Híbrido (Actual)
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

**Última actualización: 2025-11-19 (Versión 3.0)**

| Archivo           | MD5                                   | Fecha de cambio | Versión |
|-------------------|---------------------------------------|-----------------|---------|
| server.py         | `eb818069eeb98ff97b3da10d21f58b2f`    | 2025-11-19      | 3.0     |
| client.py         | `ef87c47acbe985866e2666b94b36fc37`    | 2025-11-19      | 3.0     |
| crypto_utils.py   | `6c26258132d8e030857d73d651d156a1`    | 2025-11-19      | 3.0     |
| mostrar_cifrado.py| `c6ea27b39da48f363cfb2102994f33fd`    | 2025-10-22      | 1.0     |
| calcular_md5.py   | `1832f95ca60a02101473cee1e5434ba9`    | 2025-11-19      | 2.0     |
| README.md         | (verificar con calcular_md5.py)       | 2025-01-XX      | 3.0     |

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