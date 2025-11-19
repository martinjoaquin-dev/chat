================================================================================
                    HISTORIAL DE CAMBIOS - CHAT ASÍNCRONO
================================================================================

Este documento registra todos los cambios realizados en el proyecto de chat,
incluyendo la migración a arquitectura asíncrona y cifrado híbrido.

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

