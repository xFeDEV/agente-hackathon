#!/bin/bash

# Script para configurar las credenciales de Google Cloud
# Asegúrate de tener el archivo primeval-falcon-474622-h1-d5121477addc.json

echo "🔧 Configuración de Credenciales de Google Cloud"
echo "================================================"
echo ""

# Colores para mejor visualización
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Nombre del archivo de credenciales
KEY_FILE="primeval-falcon-474622-h1-d5121477addc.json"
CONFIG_DIR="config"
TARGET_PATH="$CONFIG_DIR/$KEY_FILE"

# Verificar si el directorio config existe
if [ ! -d "$CONFIG_DIR" ]; then
    echo -e "${YELLOW}⚠️  Directorio config no encontrado. Creándolo...${NC}"
    mkdir -p "$CONFIG_DIR"
    echo -e "${GREEN}✓ Directorio config creado${NC}"
fi

# Verificar si el archivo ya existe en config/
if [ -f "$TARGET_PATH" ]; then
    echo -e "${GREEN}✓ El archivo de credenciales ya está en la ubicación correcta${NC}"
    echo "  Ruta: $TARGET_PATH"
    ls -lh "$TARGET_PATH"
    exit 0
fi

# Buscar el archivo en ubicaciones comunes
echo "🔍 Buscando el archivo de credenciales..."
echo ""

POSSIBLE_LOCATIONS=(
    "$HOME/Downloads/$KEY_FILE"
    "$HOME/Descargas/$KEY_FILE"
    "$HOME/Escritorio/$KEY_FILE"
    "./$KEY_FILE"
    "../$KEY_FILE"
)

FOUND=false
for location in "${POSSIBLE_LOCATIONS[@]}"; do
    if [ -f "$location" ]; then
        echo -e "${GREEN}✓ Archivo encontrado en: $location${NC}"
        echo ""
        echo "Copiando a $TARGET_PATH..."
        cp "$location" "$TARGET_PATH"
        chmod 600 "$TARGET_PATH"  # Permisos restrictivos para seguridad
        echo -e "${GREEN}✓ Archivo copiado correctamente${NC}"
        echo ""
        FOUND=true
        break
    fi
done

if [ "$FOUND" = false ]; then
    echo -e "${RED}❌ Archivo no encontrado en ubicaciones comunes${NC}"
    echo ""
    echo "Por favor, copia manualmente el archivo con el siguiente comando:"
    echo ""
    echo -e "${YELLOW}  cp /ruta/a/$KEY_FILE $TARGET_PATH${NC}"
    echo ""
    echo "O si lo tienes en otra ubicación, ejecútalo manualmente."
    exit 1
fi

# Verificación final
echo "📋 Verificación final:"
echo "===================="
echo ""
ls -lh "$TARGET_PATH"
echo ""

# Verificar que es un JSON válido
if command -v python3 &> /dev/null; then
    if python3 -c "import json; json.load(open('$TARGET_PATH'))" 2>/dev/null; then
        echo -e "${GREEN}✓ El archivo JSON es válido${NC}"
    else
        echo -e "${RED}❌ El archivo no parece ser un JSON válido${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}✅ Configuración completada correctamente${NC}"
echo ""
echo "Próximos pasos:"
echo "1. Verifica que el archivo .env tenga las siguientes variables:"
echo "   - GOOGLE_CLOUD_PROJECT=primeval-falcon-474622-h1"
echo "   - GOOGLE_CLOUD_LOCATION=us-central1"
echo ""
echo "2. Inicia los servicios con:"
echo "   docker-compose up -d --build"
echo ""
echo "3. Verifica los logs del backend:"
echo "   docker-compose logs -f backend"
echo ""

