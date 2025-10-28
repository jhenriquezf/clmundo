# 🚀 Guía de Deployment - CLMUNDO en GCP

## 📋 Índice
1. [Preparación del Proyecto](#preparación-del-proyecto)
2. [Setup de VM en GCP](#setup-de-vm-en-gcp)
3. [Configuración de DNS](#configuración-de-dns)
4. [Certificados SSL](#certificados-ssl)
5. [Deployment](#deployment)
6. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Preparación del Proyecto

### 1. Estructura de Archivos

Asegúrate de tener esta estructura en tu proyecto:

```
clmundo/
├── clmundo/
│   ├── __init__.py
│   ├── settings.py
│   ├── settings_prod.py    # ← NUEVO
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── travel/
├── static/
├── templates/
├── nginx/
│   └── nginx.conf          # ← NUEVO
├── Dockerfile.prod         # ← NUEVO
├── docker-compose.prod.yml # ← NUEVO
├── .env.prod              # ← CREAR (no commitear)
├── .env.prod.template     # ← NUEVO
├── requirements.txt
├── manage.py
├── deploy.sh              # ← NUEVO
├── setup_vm.sh            # ← NUEVO
└── backup.sh              # ← NUEVO
```

### 2. Archivos que Debes Crear/Actualizar

#### a) Copiar `settings_prod.py`
```bash
cp settings_prod.py clmundo/settings_prod.py
```

#### b) Crear `.env.prod` desde el template
```bash
cp .env.prod.template .env.prod
```

**Edita `.env.prod` con tus valores reales:**
```bash
# Genera una SECRET_KEY segura:
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Edita el archivo con los valores reales
nano .env.prod
```

#### c) Agregar endpoint de health check

Agrega el contenido de `health.py` a `travel/views.py` y actualiza `urls.py`:

```python
# En clmundo/urls.py
from travel.views import health_check

urlpatterns = [
    path('health/', health_check, name='health'),
    # ... resto de tus URLs
]
```

#### d) Actualizar requirements.txt

Asegúrate de tener:
```txt
# Agregar si no está
django-celery-beat==2.5.0
```

### 3. Preparar Archivos para Git

```bash
# Agregar al .gitignore
echo ".env.prod" >> .gitignore
echo "*.log" >> .gitignore
echo "staticfiles/" >> .gitignore
echo "mediafiles/" >> .gitignore
echo "logs/" >> .gitignore
```

---

## 🖥️ Setup de VM en GCP

### 1. Crear VM en GCP Console

1. Ve a **Compute Engine** > **VM Instances**
2. Click en **Create Instance**
3. Configuración recomendada:
   - **Name**: clmundo-prod
   - **Region**: us-central1 (o la más cercana a tus usuarios)
   - **Machine type**: e2-medium (2 vCPU, 4 GB RAM) - mínimo recomendado
   - **Boot disk**: Debian 11, 30 GB SSD
   - **Firewall**: Allow HTTP y HTTPS traffic

4. Click **Create**

### 2. Conectarse a la VM

```bash
# Desde tu computadora local
gcloud compute ssh joaquin.cifuentes@clmundo-prod --zone=us-central1-a
```

### 3. Ejecutar Setup Inicial

```bash
# En la VM
# Copiar el script setup_vm.sh a la VM primero
exit  # Salir de la VM

# Desde local
gcloud compute scp setup_vm.sh joaquin.cifuentes@clmundo-prod:~/ --zone=us-central1-a

# Volver a conectar
gcloud compute ssh joaquin.cifuentes@clmundo-prod --zone=us-central1-a

# Ejecutar setup
chmod +x setup_vm.sh
./setup_vm.sh

# Cerrar sesión y reconectar (para aplicar grupo docker)
exit
gcloud compute ssh joaquin.cifuentes@clmundo-prod --zone=us-central1-a
```

### 4. Verificar Instalación

```bash
docker --version
docker-compose --version
docker ps  # No debería dar error de permisos
```

---

## 🌐 Configuración de DNS

### 1. Obtener IP de la VM

```bash
gcloud compute instances describe clmundo-prod --zone=us-central1-a --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

### 2. Configurar DNS en tu Proveedor (cloud8.cl)

Crea estos registros:

| Tipo | Nombre | Valor | TTL |
|------|--------|-------|-----|
| A | clmundo | [IP_DE_TU_VM] | 300 |
| A | www.clmundo | [IP_DE_TU_VM] | 300 |

Espera 5-10 minutos para que se propague.

### 3. Verificar DNS

```bash
# Desde tu local
dig clmundo.cloud8.cl
ping clmundo.cloud8.cl
```

---

## 🔒 Certificados SSL

### 1. Obtener Certificados con Let's Encrypt

```bash
# En la VM
sudo certbot certonly --standalone \
  -d clmundo.cloud8.cl \
  -d www.clmundo.cloud8.cl \
  --email tu-email@ejemplo.com \
  --agree-tos \
  --non-interactive
```

### 2. Copiar Certificados al Proyecto

```bash
sudo mkdir -p ~/clmundo/nginx/ssl
sudo cp /etc/letsencrypt/live/clmundo.cloud8.cl/fullchain.pem ~/clmundo/nginx/ssl/
sudo cp /etc/letsencrypt/live/clmundo.cloud8.cl/privkey.pem ~/clmundo/nginx/ssl/
sudo chown -R $USER:$USER ~/clmundo/nginx/ssl
```

### 3. Configurar Renovación Automática

```bash
# Agregar al crontab
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet && cp /etc/letsencrypt/live/clmundo.cloud8.cl/*.pem ~/clmundo/nginx/ssl/ && cd ~/clmundo && docker-compose -f docker-compose.prod.yml restart nginx") | crontab -
```

---

## 🚀 Deployment

### Opción 1: Deployment Automático (Recomendado)

**Desde tu máquina local:**

```bash
# 1. Hacer ejecutable el script
chmod +x deploy.sh

# 2. Ejecutar deployment
./deploy.sh [IP_DE_LA_VM]

# Ejemplo:
./deploy.sh 34.123.45.67
```

### Opción 2: Deployment Manual

#### Paso 1: Subir archivos a la VM

```bash
# Desde tu local
gcloud compute scp docker-compose.prod.yml joaquin.cifuentes@clmundo-prod:~/clmundo/ --zone=us-central1-a
gcloud compute scp .env.prod joaquin.cifuentes@clmundo-prod:~/clmundo/ --zone=us-central1-a
gcloud compute scp -r nginx joaquin.cifuentes@clmundo-prod:~/clmundo/ --zone=us-central1-a
gcloud compute scp Dockerfile.prod joaquin.cifuentes@clmundo-prod:~/clmundo/ --zone=us-central1-a
gcloud compute scp requirements.txt joaquin.cifuentes@clmundo-prod:~/clmundo/ --zone=us-central1-a

# Subir todo el código (o hacer git clone)
gcloud compute scp -r ./clmundo ./travel ./static ./templates ./manage.py joaquin.cifuentes@clmundo-prod:~/clmundo/ --zone=us-central1-a
```

#### Paso 2: Build y Push de la imagen

```bash
# Desde tu local
docker build -f Dockerfile.prod -t jhenriquezf/clmundo:latest .
docker login
docker push jhenriquezf/clmundo:latest
```

#### Paso 3: Iniciar en la VM

```bash
# Conectar a la VM
gcloud compute ssh joaquin.cifuentes@clmundo-prod --zone=us-central1-a

# Ir al directorio
cd ~/clmundo

# Pull de la imagen
docker-compose -f docker-compose.prod.yml pull

# Iniciar servicios
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Ejecutar migraciones
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collectstatic
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Crear superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

#### Paso 4: Verificar

```bash
# Ver estado de contenedores
docker-compose -f docker-compose.prod.yml ps

# Verificar health check
curl http://localhost/health/

# Verificar en navegador
# https://clmundo.cloud8.cl
```

---

## 📊 Monitoreo y Mantenimiento

### 1. Ver Logs

```bash
# Todos los servicios
docker-compose -f docker-compose.prod.yml logs -f

# Solo Django
docker-compose -f docker-compose.prod.yml logs -f web

# Solo Celery
docker-compose -f docker-compose.prod.yml logs -f celery_worker

# Solo Nginx
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### 2. Ver Estado de Servicios

```bash
docker-compose -f docker-compose.prod.yml ps
```

### 3. Entrar a un Contenedor

```bash
# Shell de Django
docker-compose -f docker-compose.prod.yml exec web bash

# Shell de PostgreSQL
docker-compose -f docker-compose.prod.yml exec db psql -U clmundo_user -d clmundo_prod

# Django shell
docker-compose -f docker-compose.prod.yml exec web python manage.py shell
```

### 4. Monitorear Celery con Flower

Accede a: `https://clmundo.cloud8.cl/flower/`

(Usuario/contraseña configurados en nginx)

### 5. Backup de Base de Datos

```bash
# Configurar backup automático
chmod +x backup.sh

# Agregar al crontab (diario a las 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /root/clmundo/backup.sh") | crontab -

# Backup manual
./backup.sh
```

### 6. Restaurar Backup

```bash
# Descomprimir backup
gunzip clmundo_backup_YYYYMMDD_HHMMSS.sql.gz

# Restaurar
docker exec -i clmundo_db psql -U clmundo_user -d clmundo_prod < clmundo_backup_YYYYMMDD_HHMMSS.sql
```

---

## 🔧 Troubleshooting

### Problema: "Permission denied" al ejecutar Docker

```bash
# Solución
sudo usermod -aG docker $USER
# Cerrar sesión y reconectar
```

### Problema: Contenedores no inician

```bash
# Ver logs detallados
docker-compose -f docker-compose.prod.yml logs

# Verificar puertos
sudo netstat -tulpn | grep LISTEN

# Verificar recursos
df -h
free -h
docker system df
```

### Problema: Error de migraciones

```bash
# Entrar al contenedor y ejecutar
docker-compose -f docker-compose.prod.yml exec web python manage.py showmigrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --fake-initial
```

### Problema: Archivos estáticos no cargan

```bash
# Recolectar estáticos
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Verificar permisos
docker-compose -f docker-compose.prod.yml exec web ls -la /app/staticfiles

# Reiniciar nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Problema: Celery no procesa tareas

```bash
# Ver logs de Celery
docker-compose -f docker-compose.prod.yml logs celery_worker

# Verificar conexión a Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Reiniciar worker
docker-compose -f docker-compose.prod.yml restart celery_worker
```

### Problema: Error 502 Bad Gateway

```bash
# Verificar que Django esté corriendo
docker-compose -f docker-compose.prod.yml ps web

# Ver logs de Django
docker-compose -f docker-compose.prod.yml logs web

# Verificar nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml restart web nginx
```

---

## 🔄 Actualizar la Aplicación

```bash
# 1. Desde local: build y push nueva imagen
docker build -f Dockerfile.prod -t jhenriquezf/clmundo:latest .
docker push jhenriquezf/clmundo:latest

# 2. En la VM: pull y restart
cd ~/clmundo
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## 📞 Comandos Rápidos

```bash
# Start
docker-compose -f docker-compose.prod.yml up -d

# Stop
docker-compose -f docker-compose.prod.yml down

# Restart
docker-compose -f docker-compose.prod.yml restart

# Logs
docker-compose -f docker-compose.prod.yml logs -f

# Status
docker-compose -f docker-compose.prod.yml ps

# Django shell
docker-compose -f docker-compose.prod.yml exec web python manage.py shell

# Django commands
docker-compose -f docker-compose.prod.yml exec web python manage.py [comando]
```

---

## ✅ Checklist Final

- [ ] VM creada y configurada
- [ ] Docker y Docker Compose instalados
- [ ] DNS configurado y funcionando
- [ ] Certificados SSL obtenidos
- [ ] `.env.prod` configurado con valores reales
- [ ] Código subido a la VM
- [ ] Contenedores iniciados correctamente
- [ ] Migraciones ejecutadas
- [ ] Archivos estáticos recolectados
- [ ] Superuser creado
- [ ] Sitio accesible en https://clmundo.cloud8.cl
- [ ] Health check respondiendo
- [ ] Celery procesando tareas
- [ ] Flower accesible
- [ ] Backup automatizado configurado
- [ ] Renovación SSL automática configurada

---

## 🎉 ¡Listo!

Tu aplicación debería estar corriendo en: **https://clmundo.cloud8.cl**

Para soporte o dudas, revisa los logs y el troubleshooting guide.
