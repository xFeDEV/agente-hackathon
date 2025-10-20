#!/bin/bash

# 🚀 Script de inicio rápido para verificar y lanzar el proyecto

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🔐 Agente Hackathon - Inicio con Vertex AI              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.yml no encontrado${NC}"
    echo "   Asegúrate de ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

# 1. Verificar archivo de credenciales
echo -e "${BLUE}[1/5]${NC} Verificando archivo de credenciales..."
CREDS_FILE="config/primeval-falcon-474622-h1-d5121477addc.json"

if [ ! -f "$CREDS_FILE" ]; then
    echo -e "${RED}❌ Archivo de credenciales no encontrado${NC}"
    echo ""
    echo "Por favor, coloca el archivo en: $CREDS_FILE"
    echo "Puedes usar el script de ayuda: ./setup-credentials.sh"
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ Archivo de credenciales encontrado${NC}"
    
    # Verificar permisos
    PERMS=$(stat -c "%a" "$CREDS_FILE" 2>/dev/null || stat -f "%Lp" "$CREDS_FILE" 2>/dev/null)
    if [ "$PERMS" != "600" ]; then
        echo -e "${YELLOW}⚠️  Ajustando permisos a 600...${NC}"
        chmod 600 "$CREDS_FILE"
    fi
fi

# 2. Verificar archivo .env
echo -e "${BLUE}[2/5]${NC} Verificando archivo .env..."
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Archivo .env no encontrado${NC}"
    exit 1
fi

# Verificar variables críticas
if ! grep -q "GOOGLE_CLOUD_PROJECT" .env; then
    echo -e "${RED}❌ Variable GOOGLE_CLOUD_PROJECT no encontrada en .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Archivo .env configurado${NC}"

# 3. Detener contenedores existentes
echo -e "${BLUE}[3/5]${NC} Deteniendo contenedores existentes (si los hay)..."
docker-compose down > /dev/null 2>&1
echo -e "${GREEN}✅ Limpieza completada${NC}"

# 4. Construir e iniciar contenedores
echo -e "${BLUE}[4/5]${NC} Construyendo e iniciando contenedores..."
echo ""
if docker-compose up -d --build; then
    echo ""
    echo -e "${GREEN}✅ Contenedores iniciados correctamente${NC}"
else
    echo ""
    echo -e "${RED}❌ Error al iniciar contenedores${NC}"
    exit 1
fi

# 5. Esperar a que el backend esté listo
echo ""
echo -e "${BLUE}[5/5]${NC} Esperando a que el backend esté listo..."
sleep 5

# Ejecutar el test de verificación
echo ""
echo -e "${YELLOW}Ejecutando verificación de Vertex AI...${NC}"
echo ""
docker-compose exec -T backend python /app/test_vertex_ai.py

# Verificar el resultado
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ¡Sistema iniciado y verificado correctamente!        ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "📍 Servicios disponibles:"
    echo "   • Backend API:  http://localhost:8000"
    echo "   • API Docs:     http://localhost:8000/docs"
    echo "   • n8n:          http://localhost:5678"
    echo "   • PostgreSQL:   localhost:5432"
    echo ""
    echo "📋 Comandos útiles:"
    echo "   • Ver logs:           docker-compose logs -f"
    echo "   • Ver logs backend:   docker-compose logs -f backend"
    echo "   • Detener:            docker-compose down"
    echo "   • Reiniciar:          docker-compose restart"
    echo ""
else
    echo ""
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⚠️  Sistema iniciado pero hay problemas de config       ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Los contenedores están corriendo, pero la verificación de Vertex AI falló."
    echo "Revisa los mensajes anteriores para más detalles."
    echo ""
    echo "Consulta VERTEX_AI_SETUP.md para instrucciones completas."
    echo ""
    echo "Para ver logs en tiempo real:"
    echo "  docker-compose logs -f backend"
    echo ""
fi

