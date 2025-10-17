# 🔐 Chat TCP con Cifrado Asimétrico

Un sistema de chat cliente-servidor TCP con cifrado asimétrico robusto implementado en Python.

## 🚀 Características

### Seguridad
- **RSA-4096**: Para firmas digitales y autenticación
- **ECDH P-384**: Para intercambio seguro de claves
- **AES-256-GCM**: Cifrado simétrico de grado militar
- **HMAC-SHA256**: Verificación adicional de integridad
- **No-repudio**: Firma digital de cada mensaje
- **Autenticación**: Verificación de identidad del remitente
- **IV aleatorio**: Cada mensaje usa un vector de inicialización único

### Funcionalidades
- ✅ Comunicación TCP en tiempo real
- ✅ **Intercambio automático de claves públicas**
- ✅ **Firma digital de mensajes**
- ✅ **Verificación de identidad**
- ✅ Cifrado/descifrado transparente
- ✅ **Visualización de datos cifrados** en tiempo real
- ✅ Logging rotativo con archivos de respaldo
- ✅ Manejo robusto de errores
- ✅ Interfaz de línea de comandos configurable
- ✅ Soporte para múltiples clientes simultáneos
- ✅ **Scripts de demostración** del cifrado

## 🏗️ Arquitectura

### Protocolo de Cifrado Asimétrico
```
1. Intercambio de claves públicas:
   Cliente → Servidor: Clave pública RSA + ECDH
   Servidor → Cliente: Clave pública RSA + ECDH

2. Cálculo de secreto compartido:
   Ambos calculan: ECDH(privada_local, pública_peer)

3. Mensaje cifrado:
   [4 bytes: longitud total]
   [12 bytes: IV (nonce)]
   [16 bytes: tag de autenticación GCM]
   [32 bytes: HMAC-SHA256]
   [resto: ciphertext AES-256-GCM]

4. Firma digital:
   [4 bytes: longitud firma]
   [resto: firma RSA-4096]
```

### Flujo de Comunicación
1. **Intercambio de claves** → Claves públicas RSA + ECDH
2. **Cálculo ECDH** → Secreto compartido para AES
3. **Cliente** → Cifra mensaje con AES-256-GCM + Firma con RSA-4096
4. **Red** → Transmisión segura de datos cifrados + firma
5. **Servidor** → Verifica firma RSA + Descifra con AES-256-GCM
6. **Log** → Almacena mensaje con identidad verificada

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
python server.py --host 0.0.0.0 --port 9000 --key-size 4096
```

**Parámetros:**
- `--host`: IP de escucha (default: 0.0.0.0)
- `--port`: Puerto de escucha (default: 9000)
- `--key-size`: Tamaño de clave RSA (default: 4096)
- `--log-file`: Archivo de log (default: chat.log)
- `--max-bytes`: Tamaño máximo del log (default: 5MB)
- `--backups`: Número de archivos de respaldo (default: 3)

### 2. Conectar Cliente
```bash
python client.py
```

**Opciones del cliente:**
```bash
python client.py --host 127.0.0.1 --port 9000 --key-size 4096
```

**Parámetros:**
- `--host`: IP del servidor (default: 127.0.0.1)
- `--port`: Puerto del servidor (default: 9000)
- `--key-size`: Tamaño de clave RSA (default: 4096)

### 3. Ejemplo de Uso
```bash
# Terminal 1: Servidor
python server.py --key-size 4096

# Terminal 2: Cliente 1
python client.py --key-size 4096

# Terminal 3: Cliente 2
python client.py --key-size 4096
```

## 🔧 Configuración Avanzada

### Cambiar Tamaño de Clave RSA
```bash
# Servidor con clave RSA-2048 (más rápido)
python server.py --key-size 2048

# Cliente con la misma configuración
python client.py --key-size 2048
```

### Configurar Logging
```bash
# Servidor con logs personalizados
python server.py --log-file mi_chat.log --max-bytes 10000000 --backups 5
```

## 🧪 Pruebas

### Probar Cifrado Asimétrico
```bash
python crypto_utils_asymmetric.py
```

### Ver Estructura del Cifrado
```bash
python mostrar_cifrado_asimetrico.py
```

### Probar Comunicación
1. Inicia el servidor
2. Conecta múltiples clientes
3. Envía mensajes desde diferentes clientes
4. **Observa el intercambio de claves** en tiempo real
5. **Verifica las firmas digitales** automáticamente
6. Verifica que aparezcan en el log del servidor

### Visualización en Tiempo Real
- **Cliente**: Muestra datos cifrados y firma digital
- **Servidor**: Muestra datos recibidos, descifrados y verificación de firma
- **Estructura**: IV, Tag, HMAC, Ciphertext + Firma RSA
- **Identidad**: Hash de clave pública para identificación

## 🔒 Seguridad

### Algoritmos Utilizados
- **RSA-4096**: Cifrado asimétrico de 4096 bits con autenticación
- **ECDH P-384**: Intercambio de claves con curva elíptica de 384 bits
- **AES-256-GCM**: Cifrado simétrico de 256 bits con autenticación
- **HMAC-SHA256**: Verificación de integridad con clave secreta
- **PSS Padding**: Relleno probabilístico para firmas RSA

### Características de Seguridad
- ✅ **Confidencialidad**: AES-256-GCM
- ✅ **Integridad**: HMAC-SHA256
- ✅ **Autenticación**: RSA-4096
- ✅ **No-repudio**: Firma digital
- ✅ **Distribución de claves**: ECDH P-384
- ✅ **Detección de tampering**: Falla si el mensaje fue alterado
- ✅ **Verificación de identidad**: Cada mensaje está firmado

### Buenas Prácticas
- ✅ Usa claves RSA de al menos 2048 bits (recomendado 4096)
- ✅ Verifica la identidad de los participantes
- ✅ Monitorea los logs para actividad sospechosa
- ✅ Considera rotación periódica de claves
- ✅ Almacena claves privadas de forma segura

### Limitaciones Actuales
- ⚠️ Claves generadas en memoria (no persistentes)
- ⚠️ No hay revocación de claves
- ⚠️ No hay certificados digitales
- ⚠️ No hay autenticación de usuarios

## 📊 Comparación: Simétrico vs Asimétrico

| Característica | Simétrico | Asimétrico |
|---------------|-----------|------------|
| **Velocidad** | ⚡ Muy rápido | 🐌 Más lento |
| **Complejidad** | 🟢 Simple | 🔴 Complejo |
| **Distribución de claves** | ❌ Problemática | ✅ Segura |
| **No-repudio** | ❌ No | ✅ Sí |
| **Autenticación** | ❌ Limitada | ✅ Completa |
| **Escalabilidad** | 🟡 Limitada | 🟢 Excelente |
| **Uso recomendado** | Chat grupal | Transacciones críticas |

## 🐛 Solución de Problemas

### Error: "No se pudo conectar"
- Verifica que el servidor esté ejecutándose
- Comprueba la IP y puerto
- Revisa el firewall

### Error: "Intercambio de claves falló"
- Verifica que las claves RSA sean compatibles
- Comprueba la conectividad de red
- Revisa los logs del servidor

### Error: "Firma digital inválida"
- Verifica que las claves públicas coincidan
- Comprueba que no haya corrupción de datos
- Revisa la integridad de la conexión

### Error: "Datos cifrados demasiado cortos"
- El mensaje puede estar corrupto
- Verifica la integridad de la conexión
- Comprueba el intercambio de claves

## 📁 Estructura del Proyecto

```
chat/
├── client.py                      # Cliente TCP con cifrado asimétrico
├── server.py                      # Servidor TCP con descifrado asimétrico
├── crypto_utils_asymmetric.py     # Utilidades criptográficas asimétricas
├── mostrar_cifrado_asimetrico.py  # Script de demostración del cifrado asimétrico
├── requirements.txt               # Dependencias Python
├── README.md                      # Este archivo
└── chat.log                       # Logs del servidor (generado automáticamente)
```

## 🔄 Versiones

### Rama Actual: `feature/asymmetric-encryption`
- ✅ Cifrado asimétrico RSA-4096 + ECDH P-384 + AES-256-GCM
- ✅ Intercambio automático de claves públicas
- ✅ Firma digital y verificación
- ✅ Cliente y servidor modificados
- ✅ Utilidades criptográficas completas

### Rama Anterior: `feature/symmetric-encryption`
- ✅ Cifrado simétrico AES-256-GCM + HMAC
- ✅ Clave compartida predefinida
- ✅ Implementación más simple

## 📚 Referencias Técnicas

- [RSA Specification](https://tools.ietf.org/html/rfc3447)
- [ECDH Specification](https://tools.ietf.org/html/rfc7748)
- [AES-GCM Specification](https://tools.ietf.org/html/rfc5288)
- [HMAC Specification](https://tools.ietf.org/html/rfc2104)
- [Cryptography Library](https://cryptography.io/)

## 👥 Contribuciones

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

**⚠️ Advertencia de Seguridad**: Este es un proyecto educativo. Para uso en producción, implementa medidas de seguridad adicionales como certificados digitales, revocación de claves, y auditoría de seguridad.| README.md | 01efe997695b7ca6ff2f7c0f51ed0a66 | 2025-10-08 | NombreTeam |


## 📝 Control de Versiones

| Archivo                         | MD5                              | Fecha de cambio|
|---------------------------------|----------------------------------|----------------|
| README.md                       | 8f02923001cc1e7e42324ed253cd0fec | 2025-10-08     |
| __pycache__                     |                                  | 2025-10-08     |
| chat                            |                                  |                |
| chat.log                        | d7e83eb0c924c48db2d539af3d0b9bc4 | 2025-10-08     |
| client.py                       | 62ddf99888a2f0d20641ee4e4344f133 | 2025-10-08     |
| crypto_utils_asymmetric.py      | de411e77dfe63776add713e50189ef01 | 2025-10-08     |
| mostrar_cifrado_asimetrico.py   | 031c161ab7da05cf34d08483d75b9ec6 | 2025-10-08     |
| requirements.txt                | f075620e4fc1dfbcfd4e88038cd67c7e | 2025-10-07     |
| server.py                       | e9c0bb12f6b22477bc02270165efec1b | 2025-10-08     |
