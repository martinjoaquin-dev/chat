# 🔐 Sistema de Chat Seguro con Firma Digital

**Versión 6.0** | **Fecha: 2025-11-19**

---

## 🚀 Inicio Rápido

### Ejecutar con Interfaz Gráfica (Recomendado)

```bash
python app.py
```

Esto abrirá una ventana gráfica donde puedes:
- ✅ Iniciar el servidor de chat
- ✅ Conectar clientes de chat
- ✅ Gestionar archivos y firmas digitales

### Ejecutar desde Línea de Comandos

```bash
# Servidor de chat
python core/server.py

# Cliente de chat
python core/client.py

# Servidor de archivos
python core/file_server.py
```

---

## 📁 Estructura del Proyecto

```
chat/
├── app.py                    # Punto de entrada principal (GUI)
├── core/                     # Código principal del sistema
│   ├── server.py             # Servidor de chat
│   ├── client.py             # Cliente de chat
│   ├── file_server.py        # Servidor de archivos
│   ├── crypto_utils.py       # Utilidades criptográficas
│   └── digital_signature.py  # Módulo de firma digital
├── gui/                      # Interfaz gráfica
│   ├── main_window.py        # Ventana principal
│   ├── chat_window.py        # Ventana de chat
│   └── files_window.py       # Ventana de archivos
├── scripts/                  # Scripts auxiliares
│   ├── generate_ssl_cert.py  # Generar certificados SSL
│   ├── calcular_md5.py        # Calcular MD5
│   └── ...
├── docs/                     # Documentación completa
│   ├── README.md             # Documentación técnica
│   ├── GUIA_USO.md          # Guía paso a paso
│   └── ...
├── config/                   # Configuración
│   └── .env.example          # Plantilla de variables
└── requirements.txt          # Dependencias
```

---

## 📚 Documentación

Toda la documentación está en la carpeta `docs/`:

- **[README.md](docs/README.md)** - Documentación técnica completa
- **[GUIA_USO.md](docs/GUIA_USO.md)** - Guía paso a paso para usuarios
- **[RESUMEN_EJECUTIVO.md](docs/RESUMEN_EJECUTIVO.md)** - Resumen ejecutivo
- **[PROJECT_CHARTER.md](docs/PROJECT_CHARTER.md)** - Carta del proyecto
- **[PRESUPUESTOS.md](docs/PRESUPUESTOS.md)** - Análisis de presupuestos
- **[CONTROL_CAMBIOS.txt](docs/CONTROL_CAMBIOS.txt)** - Control de versiones

---

## ⚙️ Configuración

1. **Copia el archivo de configuración:**
   ```bash
   cp config/.env.example .env
   ```

2. **Edita `.env` con tus valores**

3. **Genera certificados SSL (si usas SSL):**
   ```bash
   python scripts/generate_ssl_cert.py
   ```

4. **Genera claves de firma (si usas firma digital):**
   ```bash
   python -c "from core.digital_signature import generate_signing_key_pair; generate_signing_key_pair()"
   ```

---

## 🎯 Características

- ✅ **Chat seguro** con cifrado híbrido (RSA + AES)
- ✅ **Firma digital** de documentos (TXT, PDF, ZIP)
- ✅ **Interfaz gráfica** intuitiva
- ✅ **SSL/TLS** para transporte seguro
- ✅ **Validación SHA256** de mensajes
- ✅ **Arquitectura asíncrona** escalable

---

## 📦 Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt
```

---

## 🆘 Soporte

- Revisa la [Guía de Uso](docs/GUIA_USO.md) para instrucciones detalladas
- Consulta la [Documentación Técnica](docs/README.md) para desarrolladores
- Revisa el [Control de Cambios](docs/CONTROL_CAMBIOS.txt) para el historial

---

**¿Primera vez usando el sistema?** → Lee [GUIA_USO.md](docs/GUIA_USO.md)  
**¿Eres desarrollador?** → Lee [docs/README.md](docs/README.md)

