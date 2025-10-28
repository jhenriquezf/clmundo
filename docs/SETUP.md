# docs/SETUP.md
# Guía de Instalación - ClMundo

## Requisitos Previos
- Python 3.11+
- Docker y Docker Compose
- PostgreSQL (para producción)
- Redis (para cache y Celery)

## Instalación Local

### 1. Clonar y configurar entorno
```bash
git clone <repo-url>
cd clmundo
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 3. Configurar base de datos
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Poblar datos demo
```bash
python manage.py populate_demo_data
python manage.py create_staff_user --username=operador --email=ops@clmundo.com --password=ops123
```

### 5. Ejecutar servidor
```bash
python manage.py runserver
```

## Instalación con Docker

### 1. Usar Docker Compose
```bash
docker-compose up --build
```

### 2. Configurar base de datos (primera vez)
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py populate_demo_data
```

## Usuarios Demo

Después de ejecutar `populate_demo_data`:

**Cliente:**
- Usuario: ana.silva
- Email: ana.silva@email.com
- (Sin contraseña - usar magic link)

**Operador:**
- Usuario: operador  
- Email: ops@clmundo.com
- Contraseña: ops123

## URLs Importantes

- **Aplicación cliente:** http://localhost:8000/
- **Dashboard operaciones:** http://localhost:8000/operations/
- **Admin Django:** http://localhost:8000/admin/
- **API:** http://localhost:8000/api/

## Características Implementadas

### Para Clientes:
✅ Landing page con opciones de login
✅ Timeline del día con actividades
✅ Detalles de cada servicio/tour
✅ Sistema de vouchers con QR
✅ Reporte de incidencias
✅ Notificaciones en tiempo real
✅ Soporte offline básico

### Para Operadores:
✅ Dashboard Kanban con estados
✅ Gestión de arribos del día
✅ Seguimiento de servicios en curso
✅ Manejo de incidencias
✅ Métricas en tiempo real
✅ Actualización de estados

### Integraciones Futuras:
🔄 Google Maps API (direcciones reales)
🔄 Twilio (SMS/WhatsApp)
🔄 Sistema de pagos
🔄 Push notifications
🔄 Tracking GPS en tiempo real
🔄 Sistema de calificaciones