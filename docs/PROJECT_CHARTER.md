# PROJECT CHARTER
## Sistema de Chat Seguro con Firma Digital

**Proyecto:** Sistema de Comunicación Segura y Firma Digital  
**Versión:** 6.0  
**Fecha de Inicio:** 2025-10-08  
**Fecha de Última Actualización:** 2025-11-19  
**Estado:** En Desarrollo Activo

---

## 1. INFORMACIÓN DEL PROYECTO

### Nombre del Proyecto
Sistema de Chat Seguro con Cifrado Híbrido y Firma Digital

### Descripción
Sistema completo de comunicación segura cliente-servidor con capacidades de firma digital para documentos, diseñado para entornos empresariales que requieren seguridad de grado militar.

### Objetivo del Proyecto
Desarrollar e implementar un sistema de comunicación segura con:
- Cifrado híbrido (RSA + AES)
- Validación de integridad (SHA256)
- Firma digital de documentos
- Infraestructura escalable en la nube

---

## 2. JUSTIFICACIÓN DEL PROYECTO

### Necesidad del Negocio
- Requerimiento de comunicación segura entre usuarios
- Necesidad de firmar documentos digitalmente
- Cumplimiento de estándares de seguridad
- Escalabilidad para crecimiento empresarial

### Beneficios Esperados
- Seguridad de grado empresarial
- Autenticidad e integridad de documentos
- Escalabilidad y flexibilidad
- Reducción de riesgos de seguridad

---

## 3. ALCANCE DEL PROYECTO

### Entregables Principales

#### Fase 1: Comunicación Segura (Completado)
- ✅ Sistema de chat con cifrado híbrido
- ✅ Validación SHA256
- ✅ SSL/TLS

#### Fase 2: Firma Digital (En Desarrollo)
- ✅ Módulo de firma digital
- ✅ Servidor de archivos
- ⏳ Integración con Drive
- ⏳ Notificaciones por correo

#### Fase 3: Infraestructura (Pendiente)
- ⏳ Despliegue en AWS
- ⏳ Configuración de VPN
- ⏳ Monitoreo y logging avanzado

### Criterios de Aceptación
- Sistema funcional con cifrado híbrido
- Firma digital operativa para TXT, PDF, ZIP
- Documentación completa
- Pruebas de seguridad exitosas

---

## 4. STAKEHOLDERS

### Equipo de Desarrollo
- Desarrollador Principal
- Revisor de Seguridad
- Administrador de Sistemas

### Usuarios Finales
- Personal técnico (ingenieros, desarrolladores)
- Personal no técnico (administrativo, gerencial)

### Patrocinadores
- Cliente/Organización
- Departamento de TI

---

## 5. RIESGOS Y MITIGACIÓN

### Riesgos Identificados

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Vulnerabilidades de seguridad | Media | Alto | Auditorías regulares, actualizaciones |
| Problemas de escalabilidad | Baja | Medio | Arquitectura asíncrona, pruebas de carga |
| Complejidad de despliegue | Media | Medio | Documentación detallada, scripts automatizados |
| Dependencias externas | Baja | Bajo | Uso de librerías estables, versiones fijas |

---

## 6. RECURSOS REQUERIDOS

### Recursos Humanos
- 1 Desarrollador Full-Stack
- 1 Especialista en Seguridad (part-time)
- 1 Administrador de Sistemas (part-time)

### Recursos Técnicos
- Servidor AWS EC2 o VM equivalente
- Certificados SSL (Let's Encrypt o comercial)
- Almacenamiento para archivos y logs
- Acceso a servicios de correo (opcional)

### Recursos de Software
- Python 3.7+
- Librerías criptográficas
- Servidor web asíncrono
- Herramientas de desarrollo

---

## 7. CRONOGRAMA

### Hitos Principales

| Hito | Fecha Objetivo | Estado |
|------|----------------|--------|
| Versión 1.0 - Sistema básico | 2025-10-08 | ✅ Completado |
| Versión 3.0 - Cifrado híbrido | 2025-11-19 | ✅ Completado |
| Versión 5.0 - SSL/TLS | 2025-11-19 | ✅ Completado |
| Versión 6.0 - Firma digital | 2025-11-19 | ✅ Completado |
| Despliegue en AWS | Pendiente | ⏳ Pendiente |
| Integración Drive/Email | Pendiente | ⏳ Pendiente |

---

## 8. PRESUPUESTO

Ver documento `PRESUPUESTOS.md` para detalles completos.

**Resumen:**
- Desarrollo: Incluido en recursos internos
- Infraestructura AWS: ~$50-100/mes
- Certificados SSL: Gratis (Let's Encrypt) o $50-200/año
- Servicios adicionales: Variables según uso

---

## 9. GESTIÓN DE CAMBIOS

### Proceso de Control de Cambios
1. Solicitud de cambio documentada
2. Evaluación de impacto
3. Aprobación por stakeholders
4. Implementación y pruebas
5. Actualización de documentación

### Documentación de Cambios
- `CONTROL_CAMBIOS.txt`: Control detallado
- `README.txt`: Historial de versiones
- MD5 de archivos para verificación

---

## 10. CRITERIOS DE ÉXITO

### Métricas de Éxito
- ✅ Sistema funcional con todas las características
- ✅ Documentación completa y clara
- ✅ Pruebas de seguridad exitosas
- ✅ Despliegue exitoso en infraestructura objetivo
- ✅ Satisfacción de usuarios

### Criterios de Finalización
- Todas las fases completadas
- Documentación entregada
- Sistema en producción estable
- Capacitación de usuarios realizada

---

## 11. APROBACIONES

**Patrocinador del Proyecto:** _________________  
**Gerente de Proyecto:** _________________  
**Líder Técnico:** _________________  

**Fecha de Aprobación:** _________________

---

## 12. DOCUMENTOS RELACIONADOS

- `RESUMEN_EJECUTIVO.md`: Resumen ejecutivo
- `PRESUPUESTOS.md`: Análisis de costos
- `README.md`: Documentación técnica
- `CONTROL_CAMBIOS.txt`: Control de versiones
- `README.txt`: Historial detallado

---

**Última Actualización:** 2025-11-19  
**Versión del Documento:** 1.0

