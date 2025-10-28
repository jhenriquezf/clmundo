# 🌍 CLMUNDO - Travel Management System

Sistema de gestión de viajes construido con Django, PostgreSQL, Celery y Redis.

## 🚀 Quick Start

### Desarrollo Local

```bash
# 1. Clonar repositorio
git clone <tu-repo>
cd clmundo

# 2. Crear archivo .env desde el ejemplo
cp .env.example .env

# 3. Iniciar servicios con Docker
docker-compose up -d

# 4. Ejecutar migraciones
docker-compose exec web python manage.py migrate

# 5. Crear superusuario
docker-compose exec web python manage.py createsuperuser

# 6. Acceder a la aplicación
# http://localhost:8000
```

### Producción en GCP

Ver guía completa de deployment: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

```bash
# 1. Configurar VM en GCP
./setup_vm.sh

# 2. Configurar variables de entorno
cp .env.prod.template .env.prod
# Editar .env.prod con valores reales

# 3. Deploy
./deploy.sh <IP_DE_LA_VM>
```

## 📦 Stack Tecnológico

- **Backend**: Django 5.2.6
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Task Queue**: Celery 5.5.3
- **Web Server**: Nginx
- **WSGI**: Gunicorn
- **Containerization**: Docker & Docker Compose

## 🛠️ Comandos Útiles

```bash
# Usando Makefile
make help              # Ver todos los comandos disponibles
make build             # Build de imagen Docker
make deploy            # Deploy completo
make logs              # Ver logs
make shell             # Django shell
make migrate           # Ejecutar migraciones
make backup            # Backup de BD

# O directamente con docker-compose
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
docker-compose -f docker-compose.prod.yml restart
```

## 📁 Estructura del Proyecto

```
clmundo/
├── clmundo/              # Configuración Django
│   ├── settings.py       # Settings desarrollo
│   ├── settings_prod.py  # Settings producción
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── travel/               # App principal
├── static/               # Archivos estáticos
├── templates/            # Templates HTML
├── nginx/               # Configuración Nginx
├── docker-compose.yml    # Docker Compose desarrollo
├── docker-compose.prod.yml  # Docker Compose producción
├── Dockerfile.prod       # Dockerfile producción
├── requirements.txt      # Dependencias Python
├── Makefile             # Comandos útiles
└── deploy.sh            # Script de deployment

```

## 🔐 Seguridad

- ✅ HTTPS/SSL con Let's Encrypt
- ✅ Variables de entorno para secretos
- ✅ Usuario no-root en contenedores
- ✅ Security headers en Nginx
- ✅ Firewall configurado (UFW)
- ✅ Fail2ban activado
- ✅ Rate limiting en Nginx

## 📊 Monitoreo

- **Health Check**: `https://clmundo.cloud8.cl/health/`
- **Celery Monitoring**: `https://clmundo.cloud8.cl/flower/`
- **Logs**: `docker-compose logs -f`

## 🔄 CI/CD

### Workflow Manual

1. Desarrollar localmente
2. Commitear cambios
3. Build imagen: `make build`
4. Push a DockerHub: `make push`
5. Deploy: `make deploy`

## 🐛 Troubleshooting

Ver sección de troubleshooting en [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

Problemas comunes:
- Permission denied con Docker → Agregar usuario a grupo docker
- 502 Bad Gateway → Verificar logs de Django y Nginx
- Migraciones fallando → Ver logs y ejecutar `--fake-initial`
- Celery no procesa → Verificar conexión a Redis

## 📝 Configuración de Entorno

### Variables Requeridas (.env.prod)

```bash
# Django
SECRET_KEY=tu-secret-key-aqui
DEBUG=False
ALLOWED_HOSTS=clmundo.cloud8.cl,www.clmundo.cloud8.cl

# Database
DATABASE_URL=postgresql://user:pass@db:5432/dbname

# Redis/Celery
CELERY_BROKER_URL=redis://:password@redis:6379/0

# APIs
GOOGLE_MAPS_API_KEY=tu-key-aqui
TWILIO_ACCOUNT_SID=tu-sid-aqui
TWILIO_AUTH_TOKEN=tu-token-aqui
```

## 🧪 Testing

```bash
# Ejecutar tests
docker-compose exec web python manage.py test

# Con coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
```

## 📚 Documentación Adicional

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Guía completa de deployment
- [Django Documentation](https://docs.djangoproject.com/)
- [Celery Documentation](https://docs.celeryproject.org/)

## 👥 Equipo

- Joaquín Cifuentes (@joaquin.cifuentes)

## 📄 Licencia

[Tu licencia aquí]

---

## 🆘 Soporte

Para problemas o preguntas:
1. Revisa el [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Verifica los logs: `make logs`
3. [Crear un issue en GitHub]

---

**Última actualización**: Octubre 2025
# clmundo
