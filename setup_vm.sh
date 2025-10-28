#!/bin/bash
# setup_vm.sh - Setup inicial de la VM en GCP

set -e

echo "======================================"
echo "🔧 CLMUNDO - VM Setup Script"
echo "======================================"

# Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt-get update
sudo apt-get upgrade -y

# Instalar Docker
echo "🐳 Instalando Docker..."
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up stable repository
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Instalar Docker Compose
echo "🔨 Instalando Docker Compose..."
DOCKER_COMPOSE_VERSION="2.20.0"
sudo curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Agregar usuario al grupo docker
echo "👤 Configurando permisos de usuario..."
sudo usermod -aG docker $USER

# Instalar utilidades adicionales
echo "🛠️  Instalando utilidades adicionales..."
sudo apt-get install -y \
    git \
    htop \
    nano \
    vim \
    curl \
    wget \
    certbot \
    python3-certbot-nginx

# Configurar firewall
echo "🔥 Configurando firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Crear directorios del proyecto
echo "📁 Creando estructura de directorios..."
mkdir -p ~/clmundo
mkdir -p ~/clmundo/nginx/ssl
mkdir -p ~/clmundo/backups
mkdir -p ~/clmundo/logs

# Configurar swap (opcional, útil para VMs pequeñas)
echo "💾 Configurando swap..."
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Instalar fail2ban para seguridad
echo "🔒 Instalando fail2ban..."
sudo apt-get install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Configurar SSH más seguro
echo "🔐 Mejorando configuración SSH..."
sudo sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Verificar instalaciones
echo ""
echo "✅ Verificando instalaciones..."
docker --version
docker-compose --version
python3 --version

echo ""
echo "======================================"
echo "✅ Setup completado exitosamente!"
echo "======================================"
echo ""
echo "📝 Próximos pasos:"
echo "1. Cierra sesión y vuelve a conectar para aplicar permisos de Docker"
echo "2. Configura tu dominio clmundo.cloud8.cl para apuntar a esta IP"
echo "3. Obtén certificados SSL con: sudo certbot certonly --standalone -d clmundo.cloud8.cl -d www.clmundo.cloud8.cl"
echo "4. Copia los archivos del proyecto a ~/clmundo/"
echo "5. Configura el archivo .env.prod"
echo "6. Ejecuta: cd ~/clmundo && docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "🔑 Información importante:"
echo "- IP de esta VM: $(curl -s ifconfig.me)"
echo "- Directorio del proyecto: ~/clmundo"
echo ""
