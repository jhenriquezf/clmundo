#!/bin/bash
# backup.sh - Script para hacer backup de la base de datos

set -e

BACKUP_DIR="/root/clmundo/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="clmundo_backup_${DATE}.sql"
CONTAINER_NAME="clmundo_db"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "======================================"
echo "💾 CLMUNDO - Database Backup"
echo "======================================"

# Crear directorio de backup si no existe
mkdir -p ${BACKUP_DIR}

# Hacer backup
echo -e "${GREEN}[INFO]${NC} Creando backup de la base de datos..."
docker exec ${CONTAINER_NAME} pg_dump -U clmundo_user clmundo_prod > ${BACKUP_DIR}/${BACKUP_FILE}

# Comprimir backup
echo -e "${GREEN}[INFO]${NC} Comprimiendo backup..."
gzip ${BACKUP_DIR}/${BACKUP_FILE}

# Eliminar backups antiguos (mantener solo los últimos 7 días)
echo -e "${GREEN}[INFO]${NC} Limpiando backups antiguos..."
find ${BACKUP_DIR} -name "clmundo_backup_*.sql.gz" -mtime +7 -delete

echo -e "${GREEN}✅ Backup completado: ${BACKUP_FILE}.gz${NC}"
echo -e "${GREEN}📁 Ubicación: ${BACKUP_DIR}/${BACKUP_FILE}.gz${NC}"

# Mostrar tamaño del backup
SIZE=$(du -h ${BACKUP_DIR}/${BACKUP_FILE}.gz | cut -f1)
echo -e "${GREEN}📊 Tamaño: ${SIZE}${NC}"
