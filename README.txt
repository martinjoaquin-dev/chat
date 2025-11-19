================================================================================
                    HISTORIAL DE CAMBIOS - CHAT ASÍNCRONO
================================================================================

Este documento registra todos los cambios realizados en el proyecto de chat
con cifrado simétrico, incluyendo la migración a arquitectura asíncrona.

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

