# scripts/deploy.sh
#!/bin/bash

echo "🚀 Iniciando deployment de ClMundo..."

# Detener servicios
docker-compose down

# Construir nuevas imágenes
docker-compose build

# Ejecutar migraciones
docker-compose run --rm web python manage.py migrate

# Crear datos demo si es primera vez
docker-compose run --rm web python manage.py populate_demo_data

# Iniciar servicios
docker-compose up -d

echo "✅ Deployment completado!"
echo "📱 Aplicación disponible en: http://localhost:8000"
echo "🔧 Admin disponible en: http://localhost:8000/admin"
echo "⚙️ Operaciones disponible en: http://localhost:8000/operations"