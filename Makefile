# Makefile - Comandos útiles para CLMUNDO

.PHONY: help build push deploy logs status restart shell migrate collectstatic backup clean

# Variables
DOCKER_USER := jhenriquezf
IMAGE_NAME := clmundo
TAG := latest
COMPOSE_FILE := docker-compose.prod.yml

help: ## Muestra esta ayuda
	@echo "Comandos disponibles para CLMUNDO:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build de la imagen Docker
	docker build -f Dockerfile.prod -t $(DOCKER_USER)/$(IMAGE_NAME):$(TAG) .

push: build ## Build y push al Docker Hub
	docker login
	docker push $(DOCKER_USER)/$(IMAGE_NAME):$(TAG)

deploy: push ## Deploy completo (build, push y update en servidor)
	@read -p "Ingresa la IP de la VM: " VM_IP; \
	./deploy.sh $$VM_IP

logs: ## Ver logs de todos los contenedores
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-web: ## Ver logs solo de Django
	docker-compose -f $(COMPOSE_FILE) logs -f web

logs-celery: ## Ver logs solo de Celery
	docker-compose -f $(COMPOSE_FILE) logs -f celery_worker

logs-nginx: ## Ver logs solo de Nginx
	docker-compose -f $(COMPOSE_FILE) logs -f nginx

status: ## Ver estado de los contenedores
	docker-compose -f $(COMPOSE_FILE) ps

restart: ## Reiniciar todos los contenedores
	docker-compose -f $(COMPOSE_FILE) restart

restart-web: ## Reiniciar solo Django
	docker-compose -f $(COMPOSE_FILE) restart web

restart-celery: ## Reiniciar solo Celery
	docker-compose -f $(COMPOSE_FILE) restart celery_worker

shell: ## Abrir shell de Django
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py shell

bash: ## Abrir bash en el contenedor web
	docker-compose -f $(COMPOSE_FILE) exec web bash

migrate: ## Ejecutar migraciones
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py migrate

makemigrations: ## Crear migraciones
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py makemigrations

collectstatic: ## Recolectar archivos estáticos
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py collectstatic --noinput

createsuperuser: ## Crear superusuario
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py createsuperuser

backup: ## Hacer backup de la base de datos
	./backup.sh

up: ## Iniciar todos los servicios
	docker-compose -f $(COMPOSE_FILE) up -d

down: ## Detener todos los servicios
	docker-compose -f $(COMPOSE_FILE) down

down-v: ## Detener servicios y eliminar volúmenes
	docker-compose -f $(COMPOSE_FILE) down -v

ps: ## Listar contenedores en ejecución
	docker ps

clean: ## Limpiar imágenes y contenedores no usados
	docker system prune -f

clean-all: ## Limpiar todo (incluyendo volúmenes)
	docker system prune -af --volumes

# Comandos de desarrollo local
dev-up: ## Iniciar entorno de desarrollo
	docker-compose up -d

dev-logs: ## Ver logs de desarrollo
	docker-compose logs -f

dev-down: ## Detener entorno de desarrollo
	docker-compose down

test: ## Ejecutar tests
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py test

check: ## Verificar configuración de Django
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py check

dbshell: ## Abrir shell de PostgreSQL
	docker-compose -f $(COMPOSE_FILE) exec db psql -U clmundo_user -d clmundo_prod
