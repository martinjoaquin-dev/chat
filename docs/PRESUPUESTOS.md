# ANÁLISIS DE PRESUPUESTOS
## Sistema de Chat Seguro con Firma Digital

**Versión:** 6.0  
**Fecha:** 2025-11-19  
**Período de Análisis:** Anual

---

## 1. RESUMEN EJECUTIVO DE COSTOS

### Costo Total Estimado Anual
**Desarrollo y Mantenimiento:** $0 - $15,000 USD  
**Infraestructura (AWS):** $600 - $1,200 USD/año  
**Servicios Adicionales:** $0 - $500 USD/año  
**Total Estimado:** $600 - $16,700 USD/año

---

## 2. COSTOS DE DESARROLLO

### Fase de Desarrollo Inicial
| Concepto | Horas | Costo/Hora | Total |
|----------|-------|------------|-------|
| Desarrollo Backend | 80 | $50-100 | $4,000 - $8,000 |
| Desarrollo Frontend (futuro) | 40 | $50-100 | $2,000 - $4,000 |
| Pruebas y QA | 20 | $40-80 | $800 - $1,600 |
| Documentación | 15 | $40-60 | $600 - $900 |
| **Subtotal Desarrollo** | **155** | - | **$7,400 - $14,500** |

**Nota:** Si el desarrollo es interno, estos costos pueden ser $0.

---

## 3. COSTOS DE INFRAESTRUCTURA

### Opción 1: AWS EC2

#### Instancia Recomendada: t3.medium
| Concepto | Especificación | Costo Mensual | Costo Anual |
|----------|----------------|---------------|--------------|
| Instancia EC2 | 2 vCPU, 4 GB RAM | $30-35 | $360-420 |
| Almacenamiento EBS | 20 GB SSD | $2-3 | $24-36 |
| Transferencia de Datos | 100 GB/mes | $9-10 | $108-120 |
| Elastic IP | 1 IP estática | $3.65 | $43.80 |
| **Subtotal AWS** | - | **$44-51** | **$535-620** |

#### Instancia Mínima: t3.small
| Concepto | Especificación | Costo Mensual | Costo Anual |
|----------|----------------|---------------|--------------|
| Instancia EC2 | 2 vCPU, 2 GB RAM | $15-18 | $180-216 |
| Almacenamiento EBS | 10 GB SSD | $1-2 | $12-24 |
| Transferencia de Datos | 50 GB/mes | $4-5 | $48-60 |
| Elastic IP | 1 IP estática | $3.65 | $43.80 |
| **Subtotal AWS Mínimo** | - | **$23-28** | **$283-344** |

### Opción 2: Máquina Virtual On-Premise
| Concepto | Costo Inicial | Costo Anual |
|----------|---------------|--------------|
| Servidor Físico | $500-1,500 | $0 |
| Licencia OS (si aplica) | $0-200 | $0-200 |
| Mantenimiento | $0 | $100-300 |
| Electricidad | $0 | $120-240 |
| **Subtotal VM** | **$500-1,700** | **$220-740** |

### Opción 3: Servicios Cloud Alternativos
- **DigitalOcean Droplet:** $12-24/mes ($144-288/año)
- **Linode:** $12-24/mes ($144-288/año)
- **Azure VM:** Similar a AWS
- **Google Cloud:** Similar a AWS

---

## 4. COSTOS DE CERTIFICADOS Y SEGURIDAD

### Certificados SSL/TLS
| Opción | Costo Inicial | Costo Anual | Notas |
|--------|---------------|-------------|-------|
| Let's Encrypt | $0 | $0 | Gratis, renovación automática |
| Comodo SSL | $50-100 | $50-100 | Certificado básico |
| DigiCert | $200-500 | $200-500 | Certificado empresarial |
| **Recomendado** | **$0** | **$0** | **Let's Encrypt** |

### Servicios de Seguridad Adicionales
- **Monitoreo de seguridad:** $0-50/mes (opcional)
- **Backup automático:** Incluido en AWS o $5-10/mes
- **Firewall/WAF:** $0-20/mes (opcional)

---

## 5. COSTOS DE SERVICIOS ADICIONALES

### Google Drive API (Opcional)
| Concepto | Costo |
|----------|------|
| Google Workspace Basic | $6/usuario/mes |
| Almacenamiento adicional | $0.02/GB/mes |
| API Calls | Gratis (límites generosos) |

### Servicios de Correo (Opcional)
| Servicio | Costo Mensual | Costo Anual |
|----------|---------------|-------------|
| SendGrid (Free Tier) | $0 | $0 |
| SendGrid (Paid) | $15-80 | $180-960 |
| Amazon SES | $0.10/1000 emails | Variable |
| Mailgun | $35+ | $420+ |

### VPN (Opcional)
| Opción | Costo Mensual | Costo Anual |
|--------|---------------|-------------|
| OpenVPN (self-hosted) | $0 | $0 |
| AWS VPN | $36-72 | $432-864 |
| Servicio VPN comercial | $5-15 | $60-180 |

---

## 6. COSTOS DE MANTENIMIENTO

### Mantenimiento Anual
| Concepto | Horas/Mes | Costo/Hora | Costo Anual |
|----------|-----------|------------|-------------|
| Monitoreo y soporte | 4 | $40-60 | $1,920-2,880 |
| Actualizaciones de seguridad | 2 | $50-80 | $1,200-1,920 |
| Backup y recuperación | 1 | $40-60 | $480-720 |
| **Subtotal Mantenimiento** | **7** | - | **$3,600-5,520** |

**Nota:** Si el mantenimiento es interno, estos costos pueden reducirse significativamente.

---

## 7. COMPARACIÓN DE ESCENARIOS

### Escenario 1: Mínimo (Desarrollo Interno, Let's Encrypt)
- **Desarrollo:** $0
- **Infraestructura AWS (t3.small):** $283-344/año
- **Certificados:** $0
- **Mantenimiento interno:** $0-1,000/año
- **Total:** $283-1,344/año

### Escenario 2: Estándar (Desarrollo Interno, AWS t3.medium)
- **Desarrollo:** $0
- **Infraestructura AWS:** $535-620/año
- **Certificados:** $0 (Let's Encrypt)
- **Mantenimiento:** $1,000-2,000/año
- **Total:** $1,535-2,620/año

### Escenario 3: Empresarial (Desarrollo Externo, AWS, Certificados Comerciales)
- **Desarrollo:** $7,400-14,500 (una vez)
- **Infraestructura AWS:** $535-620/año
- **Certificados:** $200-500/año
- **Mantenimiento:** $3,600-5,520/año
- **Servicios adicionales:** $500-1,000/año
- **Total primer año:** $12,235-22,140
- **Total años siguientes:** $4,835-7,640/año

---

## 8. RECOMENDACIONES

### Para Desarrollo/Pruebas
- **Infraestructura:** AWS t3.small o DigitalOcean ($12/mes)
- **Certificados:** Let's Encrypt (gratis)
- **Costo estimado:** $144-420/año

### Para Producción Pequeña-Mediana
- **Infraestructura:** AWS t3.medium ($44-51/mes)
- **Certificados:** Let's Encrypt (gratis)
- **Backup:** Incluido en AWS
- **Costo estimado:** $535-620/año + mantenimiento

### Para Producción Empresarial
- **Infraestructura:** AWS t3.large o superior
- **Certificados:** DigiCert o similar ($200-500/año)
- **Monitoreo:** Servicio profesional
- **Costo estimado:** $1,000-3,000/año + mantenimiento

---

## 9. AHORROS POTENCIALES

### Optimizaciones de Costo
1. **Reserved Instances AWS:** 30-40% descuento
2. **Spot Instances:** 50-90% descuento (para desarrollo)
3. **Let's Encrypt:** Ahorro de $50-500/año vs certificados comerciales
4. **Mantenimiento interno:** Ahorro de $3,600-5,520/año

### ROI Estimado
- **Reducción de riesgos de seguridad:** Invaluable
- **Automatización de procesos:** Ahorro de tiempo
- **Cumplimiento normativo:** Evita multas/penalizaciones

---

## 10. NOTAS IMPORTANTES

1. **Los costos de desarrollo** asumen desarrollo interno. Si se contrata externamente, agregar $7,400-14,500 iniciales.

2. **Los costos de AWS** pueden variar según región y uso real.

3. **Let's Encrypt** es completamente gratuito y adecuado para la mayoría de casos.

4. **Mantenimiento** puede ser mínimo si se automatiza correctamente.

5. **Servicios adicionales** (Drive, Email, VPN) son opcionales.

---

## 11. ACTUALIZACIÓN DE PRESUPUESTOS

Este documento debe actualizarse:
- Cada 6 meses
- Cuando cambien los requisitos
- Al migrar a nueva infraestructura
- Al agregar nuevos servicios

---

**Última Actualización:** 2025-11-19  
**Próxima Revisión:** 2026-05-19

