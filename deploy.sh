#!/bin/bash
# deploy.sh - Script de deployment para GCP

set -e  # Exit on error

echo "======================================"
echo "🚀 CLMUNDO - Deployment Script"
echo "======================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
DOCKER_USERNAME="jhenriquezf"
IMAGE_NAME="clmundo"
TAG="latest"
FULL_IMAGE="${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}"

# Función para imprimir en colores
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    print_error "Este script debe ejecutarse desde el directorio raíz del proyecto Django"
    exit 1
fi

# Verificar que existe .env.prod
if [ ! -f ".env.prod" ]; then
    print_error "Archivo .env.prod no encontrado"
    print_info "Copia .env.prod.template a .env.prod y configura las variables"
    exit 1
fi

print_info "1. Verificando requisitos..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado"
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado"
    exit 1
fi

print_info "2. Construyendo imagen Docker..."
docker build -f Dockerfile.prod -t ${FULL_IMAGE} .

print_info "3. Ejecutando tests..."
# Descomentar si tienes tests configurados
# docker run --rm ${FULL_IMAGE} python manage.py test

print_info "4. Subiendo imagen a DockerHub..."
docker login -u ${DOCKER_USERNAME}
docker push ${FULL_IMAGE}

print_info "5. Conectando a GCP VM..."
GCP_USER="joaquin.cifuentes"
GCP_VM_IP="${1:-IP_DE_TU_VM}"  # Pasar IP como primer argumento

if [ "$GCP_VM_IP" == "IP_DE_TU_VM" ]; then
    print_error "Debes proporcionar la IP de la VM como argumento"
    print_info "Uso: ./deploy.sh <IP_DE_LA_VM>"
    exit 1
fi

print_info "Desplegando en ${GCP_VM_IP}..."

# Copiar archivos necesarios a la VM
scp docker-compose.prod.yml ${GCP_USER}@${GCP_VM_IP}:~/clmundo/
scp .env.prod ${GCP_USER}@${GCP_VM_IP}:~/clmundo/
scp -r nginx ${GCP_USER}@${GCP_VM_IP}:~/clmundo/

# Ejecutar comandos en la VM
ssh ${GCP_USER}@${GCP_VM_IP} << 'ENDSSH'
cd ~/clmundo

echo "Pulling latest image..."
docker-compose -f docker-compose.prod.yml pull

echo "Stopping old containers..."
docker-compose -f docker-compose.prod.yml down

echo "Starting new containers..."
docker-compose -f docker-compose.prod.yml up -d

echo "Running migrations..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate

echo "Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

echo "Creating superuser if needed..."
# docker-compose -f docker-compose.prod.yml exec -T web python manage.py createsuperuser --noinput || true

echo "Deployment completed!"
docker-compose -f docker-compose.prod.yml ps
ENDSSH

print_info "✅ Deployment completado exitosamente!"
print_info "Aplicación disponible en: https://clmundo.cloud8.cl"
print_info ""
print_info "Comandos útiles:"
print_info "  - Ver logs: ssh ${GCP_USER}@${GCP_VM_IP} 'cd ~/clmundo && docker-compose -f docker-compose.prod.yml logs -f'"
print_info "  - Ver estado: ssh ${GCP_USER}@${GCP_VM_IP} 'cd ~/clmundo && docker-compose -f docker-compose.prod.yml ps'"
print_info "  - Reiniciar: ssh ${GCP_USER}@${GCP_VM_IP} 'cd ~/clmundo && docker-compose -f docker-compose.prod.yml restart'"
