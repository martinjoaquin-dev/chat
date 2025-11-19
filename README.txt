================================================================================
                    HISTORIAL DE CAMBIOS - CHAT ASÍNCRONO
================================================================================

Este documento registra todos los cambios realizados en el proyecto de chat,
incluyendo la migración a arquitectura asíncrona, cifrado híbrido, validación
SHA256, y la implementación de SSL/TLS con variables de entorno.

================================================================================
VERSIÓN 5.0 - SSL/TLS y Variables de Entorno
Fecha: 2025-11-19
================================================================================

DESCRIPCIÓN GENERAL:
Se implementó SSL/TLS para cifrado de transporte y se removió el hardening
(valores hardcodeados) en favor de variables de entorno. El sistema ahora
usa configuración flexible desde archivo .env, permitiendo mayor adaptabilidad
y mejores prácticas de seguridad.

CAMBIOS PRINCIPALES:

1. IMPLEMENTACIÓN DE SSL/TLS
   - Agregado: Soporte para SSL/TLS en conexiones TCP
   - Agregado: Script generate_ssl_cert.py para certificados self-signed
   - Agregado: Soporte para certificados de CA válida en producción
   - Modificado: server.py y client.py ahora soportan SSL/TLS
   - Mejoras:
     * Cifrado de transporte adicional (SSL/TLS)
     * Doble capa de seguridad: SSL/TLS + Cifrado híbrido
     * Configurable desde variables de entorno
     * Puede deshabilitarse con --no-ssl

2. VARIABLES DE ENTORNO
   - Removido: Valores hardcodeados (hardening)
   - Agregado: python-dotenv para gestión de variables de entorno
   - Agregado: Archivo .env.example como plantilla
   - Agregado: .gitignore para proteger archivo .env
   - Modificado: crypto_utils.py usa HMAC_SALT desde .env
   - Modificado: server.py lee configuración desde .env
   - Modificado: client.py lee configuración desde .env
   - Mejoras:
     * Configuración centralizada en .env
     * Sin valores hardcodeados
     * Fácil adaptación a diferentes entornos
     * Mejores prácticas de seguridad

3. ARCHIVOS NUEVOS
   - generate_ssl_cert.py: Script para generar certificados SSL self-signed
   - .env.example: Plantilla de variables de entorno
   - .gitignore: Protección de archivos sensibles

BENEFICIOS DE SSL/TLS Y VARIABLES DE ENTORNO:

1. Seguridad:
   - Cifrado de transporte adicional con SSL/TLS
   - Doble capa: SSL/TLS (transporte) + Cifrado híbrido (aplicación)
   - Sin valores hardcodeados que puedan comprometerse
   - Configuración flexible y segura

2. Flexibilidad:
   - Fácil adaptación a diferentes entornos (desarrollo, producción)
   - Configuración sin modificar código
   - Soporte para certificados de CA válida
   - SSL puede habilitarse/deshabilitarse según necesidad

3. Mejores Prácticas:
   - Variables de entorno para configuración sensible
   - .env no se commitea al repositorio
   - Separación de configuración y código
   - Preparado para despliegue en producción

SEGURIDAD MEJORADA:

- SSL/TLS: Cifrado de transporte adicional
- Variables de entorno: Sin valores hardcodeados
- HMAC_SALT configurable: Mayor flexibilidad y seguridad
- Certificados: Soporte para self-signed (desarrollo) y CA válida (producción)

MD5 DE ARCHIVOS - VERSIÓN 5.0 (2025-11-19):

| Archivo | MD5 | Fecha de cambio |
|---------|-----|-----------------|
| server.py | `348ebfd6dbfcf67f0deb930d6a3486ab` | 2025-11-19 |
| client.py | `b07f5e3d3ccda837997644139c45c44b` | 2025-11-19 |
| crypto_utils.py | `2fe800977b7e5b67185cf7a5c145f31c` | 2025-11-19 |
| generate_ssl_cert.py | `6e5d4821aabccd97433a0011b412dbe1` | 2025-11-19 |
| requirements.txt | (verificar con calcular_md5.py) | 2025-11-19 |
| mostrar_cifrado.py | `c6ea27b39da48f363cfb2102994f33fd` | 2025-10-22 |
| calcular_md5.py | `1832f95ca60a02101473cee1e5434ba9` | 2025-11-19 |

================================================================================
VERSIÓN 4.0 - Validación SHA256 en Intercambio de Mensajes
Fecha: 2025-11-19
================================================================================

DESCRIPCIÓN GENERAL:
Se implementó validación obligatoria de SHA256 en el intercambio de mensajes.
Cada mensaje enviado por el cliente debe incluir su hash SHA256, y el servidor
valida que el hash recibido coincida con el hash calculado del mensaje
descifrado. Los mensajes con hash no coincidente son descartados automáticamente.

CAMBIOS PRINCIPALES:

1. CLIENT.PY - Envío de Hash SHA256
   - Modificado: send_message() ahora calcula hash SHA256 antes de cifrar
   - Agregado: Hash SHA256 (32 bytes) se envía junto con el mensaje cifrado
   - Estructura: [longitud] + [32 bytes: hash SHA256] + [payload cifrado]
   - Mejoras:
     * Hash calculado del mensaje original (antes de cifrar)
     * Hash incluido en cada transmisión
     * Mayor protección contra alteración de mensajes

2. SERVER.PY - Validación SHA256 Obligatoria
   - Modificado: handle_client() ahora extrae y valida hash SHA256
   - Agregado: Comparación de hash recibido vs hash calculado
   - Agregado: Descarte automático de mensajes con hash no coincidente
   - Mejoras:
     * Validación obligatoria antes de aceptar mensaje
     * Mensajes inválidos son descartados y registrados en logs
     * Protección contra mensajes alterados o corruptos
     * Logs mejorados con información de validación

3. PROTOCOLO DE MENSAJES
   - Estructura actualizada:
     [4 bytes: longitud total]
     [32 bytes: Hash SHA256 del mensaje original]
     [12 bytes: IV]
     [16 bytes: Tag GCM]
     [32 bytes: HMAC-SHA256]
     [resto: ciphertext AES-256-GCM]

BENEFICIOS DE LA VALIDACIÓN SHA256:

1. Seguridad:
   - Detección automática de mensajes alterados en tránsito
   - Protección contra corrupción de datos
   - Validación obligatoria en cada mensaje
   - Mayor confianza en la integridad de los datos

2. Auditoría:
   - Logs registran intentos de mensajes inválidos
   - Trazabilidad de mensajes rechazados
   - Información detallada de validaciones fallidas
   - Mejor monitoreo de seguridad

3. Robustez:
   - Sistema más resistente a ataques de manipulación
   - Descarte automático de mensajes comprometidos
   - Prevención de procesamiento de datos corruptos
   - Mayor confiabilidad del sistema

SEGURIDAD MEJORADA:

- Validación SHA256 obligatoria: Cada mensaje debe pasar validación
- Protección contra alteración: Mensajes modificados son detectados
- Integridad garantizada: Solo mensajes válidos son procesados
- Logs de seguridad: Intentos de mensajes inválidos son registrados

MD5 DE ARCHIVOS - VERSIÓN 4.0 (2025-11-19):

| Archivo | MD5 | Fecha de cambio |
|---------|-----|-----------------|
| server.py | `ae21a882e1a6bac3ed008c28331295fd` | 2025-11-19 |
| client.py | `27e5385e75efcf34b63e2509e6448d2a` | 2025-11-19 |
| crypto_utils.py | `6c26258132d8e030857d73d651d156a1` | 2025-11-19 |
| mostrar_cifrado.py | `c6ea27b39da48f363cfb2102994f33fd` | 2025-10-22 |
| calcular_md5.py | `1832f95ca60a02101473cee1e5434ba9` | 2025-11-19 |

================================================================================
VERSIÓN 3.0 - Migración a Cifrado Híbrido (RSA + AES)
Fecha: 2025-11-19
================================================================================

DESCRIPCIÓN GENERAL:
Se migró completamente el proyecto de cifrado simétrico a cifrado híbrido,
combinando lo mejor de cifrado asimétrico (RSA) y simétrico (AES). Esta
versión elimina la necesidad de compartir contraseñas y proporciona mayor
seguridad y escalabilidad para múltiples usuarios.

CAMBIOS PRINCIPALES:

1. CRYPTO_UTILS.PY - Implementación de Cifrado Híbrido
   - Nueva clase: HybridCrypto para manejar cifrado híbrido
   - RSA-2048: Generación automática de pares de claves para cada conexión
   - Intercambio seguro de claves: Clave AES cifrada con RSA
   - AES-256-GCM: Mantiene cifrado rápido para mensajes
   - Clase legacy: SymmetricCrypto mantenida para compatibilidad (deprecated)
   - Mejoras:
     * Sin necesidad de contraseñas compartidas
     * Cada conexión tiene su propio par de claves RSA
     * Intercambio automático de claves públicas
     * Mayor seguridad para entornos multi-usuario

2. SERVER.PY - Soporte para Cifrado Híbrido
   - Eliminado: Parámetro --password (ya no necesario)
   - Agregado: Función exchange_keys() para intercambio RSA
   - Modificado: handle_client() ahora genera HybridCrypto por conexión
   - Mejoras:
     * Cada cliente tiene su propia instancia de cifrado
     * Intercambio automático de claves al conectar
     * Mayor seguridad sin compartir secretos
     * Escalable para múltiples usuarios independientes

3. CLIENT.PY - Soporte para Cifrado Híbrido
   - Eliminado: Parámetro --password (ya no necesario)
   - Agregado: Función exchange_keys() para intercambio RSA
   - Modificado: main_client() genera HybridCrypto y establece conexión segura
   - Mejoras:
     * Generación automática de par de claves RSA
     * Intercambio seguro de claves con servidor
     * Sin necesidad de configurar contraseñas
     * Listo para múltiples clientes simultáneos

BENEFICIOS DEL CIFRADO HÍBRIDO:

1. Seguridad:
   - Sin contraseñas compartidas: Cada conexión establece su propia clave AES
   - RSA-2048: Cifrado asimétrico robusto para intercambio de claves
   - AES-256-GCM: Cifrado simétrico rápido para mensajes
   - Mejor protección contra ataques de man-in-the-middle

2. Escalabilidad:
   - Ideal para múltiples usuarios sin compartir secretos
   - Cada cliente tiene su propio par de claves RSA
   - No hay límite de usuarios por contraseña compartida
   - Preparado para crecimiento empresarial

3. Mantenibilidad:
   - Sin gestión de contraseñas compartidas
   - Intercambio automático de claves
   - Código más seguro por defecto
   - Compatible con estándares de seguridad modernos

SEGURIDAD MEJORADA:

- Cifrado Híbrido: RSA-2048 para claves + AES-256-GCM para mensajes
- Intercambio seguro: Claves AES cifradas con RSA antes de transmitirse
- Sin contraseñas compartidas: Elimina vector de ataque común
- SHA256 Hash: Se mantiene para verificación de integridad
- HMAC-SHA256: Se mantiene para verificación del payload cifrado

MD5 DE ARCHIVOS - VERSIÓN 3.0 (2025-11-19):

| Archivo | MD5 | Fecha de cambio |
|---------|-----|-----------------|
| server.py | `eb818069eeb98ff97b3da10d21f58b2f` | 2025-11-19 |
| client.py | `ef87c47acbe985866e2666b94b36fc37` | 2025-11-19 |
| crypto_utils.py | `6c26258132d8e030857d73d651d156a1` | 2025-11-19 |
| mostrar_cifrado.py | `c6ea27b39da48f363cfb2102994f33fd` | 2025-10-22 |
| calcular_md5.py | `1832f95ca60a02101473cee1e5434ba9` | 2025-11-19 |

================================================================================
VERSIÓN 2.0 - Migración a Arquitectura Asíncrona
Fecha: 2025-11-19
================================================================================

DESCRIPCIÓN GENERAL:
Se migró completamente el proyecto de un modelo síncrono multi-hilo a una
arquitectura asíncrona utilizando asyncio de Python. Esto mejora significativamente
la escalabilidad y eficiencia del servidor al manejar múltiples clientes.

CAMBIOS PRINCIPALES:

1. SERVER.PY - Conversión a Asíncrono
   - Eliminado: threading.Thread, queue.Queue, socket bloqueante
   - Agregado: asyncio.start_server, StreamReader/StreamWriter
   - Mejoras:
     * Manejo eficiente de múltiples clientes sin crear threads
     * Lectura asíncrona con readexactly() para garantizar datos completos
     * Cierre limpio de conexiones con wait_closed()
     * Registro de hash SHA256 de mensajes en logs

2. CLIENT.PY - Conversión a Asíncrono
   - Eliminado: socket bloqueante, sys.stdin bloqueante
   - Agregado: asyncio.open_connection, loop.run_in_executor para entrada
   - Mejoras:
     * Comunicación no bloqueante con el servidor
     * Lectura asíncrona de entrada del usuario
     * Mejor manejo de desconexiones

3. CRYPTO_UTILS.PY - Agregado SHA256 Hash
   - Nueva función: hash_message() para calcular SHA256 de mensajes
   - Propósito: Verificación adicional de integridad de mensajes
   - Uso: Los mensajes ahora incluyen hash SHA256 en los logs del servidor

4. NUEVOS ARCHIVOS:
   - calcular_md5.py: Script para calcular MD5 de archivos .py del proyecto

BENEFICIOS DE LA ARQUITECTURA ASÍNCRONA:

1. Escalabilidad:
   - Puede manejar miles de conexiones simultáneas sin crear threads
   - Uso eficiente de memoria (cada conexión usa menos recursos)
   - Mejor rendimiento bajo carga alta

2. Eficiencia:
   - Sin overhead de cambio de contexto entre threads
   - Operaciones I/O no bloqueantes
   - Mejor uso de CPU

3. Mantenibilidad:
   - Código más limpio y fácil de entender
   - Manejo de errores más robusto
   - Mejor integración con otras librerías asíncronas

SEGURIDAD MEJORADA:

- SHA256 Hash: Cada mensaje ahora tiene un hash SHA256 calculado y registrado
  en los logs, permitiendo verificación de integridad adicional
- Mismo nivel de cifrado: AES-256-GCM + HMAC-SHA256 se mantiene
- Logs mejorados: Incluyen hash SHA256 para auditoría

MD5 DE ARCHIVOS - VERSIÓN 2.0 (2025-11-19):

| Archivo | MD5 | Fecha de cambio |
|---------|-----|-----------------|
| server.py | `8e6483ab0156066a822851036bed0f91` | 2025-11-19 |
| client.py | `715e500ff50413e2181027b877657fbc` | 2025-11-19 |
| crypto_utils.py | `b552d4565126f25cfaeb87ff8e9bfa6a` | 2025-11-19 |
| mostrar_cifrado.py | `c6ea27b39da48f363cfb2102994f33fd` | 2025-10-22 |
| calcular_md5.py | `1832f95ca60a02101473cee1e5434ba9` | 2025-11-19 |

================================================================================
VERSIÓN 1.0 - Versión Síncrona Inicial
Fecha: 2025-10-08
================================================================================

DESCRIPCIÓN:
Primera versión del chat con cifrado simétrico usando arquitectura síncrona
multi-hilo.

CARACTERÍSTICAS:
- Servidor TCP síncrono con threading
- Cifrado AES-256-GCM + HMAC-SHA256
- Soporte para múltiples clientes simultáneos
- Logging rotativo

MD5 DE ARCHIVOS - VERSIÓN 1.0 (2025-10-08):

| Archivo | MD5 | Fecha de cambio |
|---------|-----|-----------------|
| server.py | `e9c0bb12f6b22477bc02270165efec1b` | 2025-10-08 |
| client.py | `62ddf99888a2f0d20641ee4e4344f133` | 2025-10-08 |
| crypto_utils.py | (versión anterior sin SHA256) | 2025-10-08 |

================================================================================
NOTAS IMPORTANTES:
================================================================================

- Para calcular MD5 de archivos actualizados, ejecutar: python calcular_md5.py
- Todos los cambios deben documentarse en este archivo
- El MD5 debe actualizarse cada vez que se modifica un archivo .py
- Mantener historial completo de versiones para auditoría

================================================================================

