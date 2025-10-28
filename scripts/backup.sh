# scripts/backup.sh
#!/bin/bash

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "📦 Creando backup de base de datos..."
docker-compose exec db pg_dump -U postgres clmundo > $BACKUP_DIR/database.sql

echo "💾 Backup completado en: $BACKUP_DIR"