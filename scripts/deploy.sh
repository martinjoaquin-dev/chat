#!/bin/bash
# Script de despliegue para AWS EC2 o VM
# Uso: ./deploy.sh

set -e

echo "=========================================="
echo "SCRIPT DE DESPLIEGUE - Servidor de Archivos"
echo "=========================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "core/file_server.py" ]; then
    echo -e "${RED}Error: No se encuentra core/file_server.py${NC}"
    echo "Ejecuta este script desde la raíz del proyecto"
    exit 1
fi

# 1. Verificar Python
echo -e "${YELLOW}[1/8] Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 no está instalado${NC}"
    echo "Instala con: sudo apt install python3 python3-pip"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓${NC} $PYTHON_VERSION"

# 2. Instalar dependencias
echo -e "${YELLOW}[2/8] Instalando dependencias...${NC}"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --user
    echo -e "${GREEN}✓${NC} Dependencias instaladas"
else
    echo -e "${RED}No se encuentra requirements.txt${NC}"
    exit 1
fi

# 3. Verificar .env
echo -e "${YELLOW}[3/8] Verificando configuración...${NC}"
if [ ! -f ".env" ]; then
    if [ -f "config/.env.example" ]; then
        echo -e "${YELLOW}Creando .env desde ejemplo...${NC}"
        cp config/.env.example .env
        echo -e "${YELLOW}⚠ IMPORTANTE: Edita .env con tus valores${NC}"
    else
        echo -e "${RED}No se encuentra .env ni config/.env.example${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} Archivo .env encontrado"
fi

# 4. Verificar claves de firma
echo -e "${YELLOW}[4/8] Verificando claves de firma...${NC}"
if [ ! -f "signing_keys/signing_private_key.pem" ]; then
    echo -e "${YELLOW}Generando claves de firma...${NC}"
    python3 -c "from core.digital_signature import generate_signing_key_pair; generate_signing_key_pair()"
    echo -e "${GREEN}✓${NC} Claves generadas"
else
    echo -e "${GREEN}✓${NC} Claves de firma encontradas"
fi

# 5. Crear directorios necesarios
echo -e "${YELLOW}[5/8] Creando directorios...${NC}"
mkdir -p uploads signatures logs certificates signing_keys
echo -e "${GREEN}✓${NC} Directorios creados"

# 6. Verificar certificados SSL (opcional)
echo -e "${YELLOW}[6/8] Verificando certificados SSL...${NC}"
if [ ! -f "certificates/server.crt" ]; then
    echo -e "${YELLOW}Generando certificados SSL self-signed...${NC}"
    python3 scripts/generate_ssl_cert.py
    echo -e "${GREEN}✓${NC} Certificados generados"
else
    echo -e "${GREEN}✓${NC} Certificados SSL encontrados"
fi

# 7. Probar que el servidor puede iniciar
echo -e "${YELLOW}[7/8] Probando servidor...${NC}"
timeout 3 python3 core/file_server.py > /dev/null 2>&1 || true
echo -e "${GREEN}✓${NC} Servidor puede iniciar"

# 8. Crear servicio systemd (opcional)
echo -e "${YELLOW}[8/8] ¿Crear servicio systemd? (s/n)${NC}"
read -r response
if [[ "$response" =~ ^([sS][iI][sS]|[sS])$ ]]; then
    CURRENT_DIR=$(pwd)
    CURRENT_USER=$(whoami)
    
    SERVICE_FILE="/etc/systemd/system/file-server.service"
    
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Servidor de Archivos y Firma Digital
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 $CURRENT_DIR/core/file_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable file-server
    echo -e "${GREEN}✓${NC} Servicio systemd creado"
    echo -e "${YELLOW}Para iniciar: sudo systemctl start file-server${NC}"
    echo -e "${YELLOW}Para ver logs: sudo journalctl -u file-server -f${NC}"
else
    echo -e "${YELLOW}Servicio systemd no creado${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}DESPLIEGUE COMPLETADO${NC}"
echo "=========================================="
echo ""
echo "Para iniciar el servidor manualmente:"
echo "  python3 core/file_server.py"
echo ""
echo "Para iniciar como servicio:"
echo "  sudo systemctl start file-server"
echo ""
echo "Verificar estado:"
echo "  curl http://localhost:8080/health"
echo ""

