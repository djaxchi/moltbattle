#!/bin/bash
# =============================================================================
# MOLTCLASH VPS SETUP SCRIPT
# Run this on your Hostinger VPS after SSH'ing in
# =============================================================================

set -e

DOMAIN="moltclash.com"
EMAIL="admin@moltclash.com"
APP_DIR="/opt/moltclash"

echo "🚀 MoltClash VPS Setup"
echo "======================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root (use sudo)"
  exit 1
fi

# Update system
echo "📦 Updating system..."
apt update && apt upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# Install Git if not present
if ! command -v git &> /dev/null; then
    echo "📂 Installing Git..."
    apt install -y git
fi

# Clone or pull repository
if [ -d "$APP_DIR" ]; then
    echo "📥 Pulling latest changes..."
    cd $APP_DIR
    git pull
else
    echo "📥 Cloning repository..."
    git clone https://github.com/djaxchi/moltbattle.git $APP_DIR
    cd $APP_DIR
fi

# Check for required files
echo ""
echo "📋 Checking configuration files..."

if [ ! -f "$APP_DIR/.env.production" ]; then
    echo "⚠️  .env.production not found!"
    echo "   Please create it with your production settings."
    echo ""
    echo "   You can copy from your local machine:"
    echo "   scp .env.production root@YOUR_VPS_IP:$APP_DIR/"
    echo ""
fi

if [ ! -f "$APP_DIR/firebase-service-account.json" ]; then
    echo "⚠️  firebase-service-account.json not found!"
    echo "   Please upload your Firebase service account key."
    echo ""
    echo "   From your local machine:"
    echo "   scp firebase-service-account.json root@YOUR_VPS_IP:$APP_DIR/"
    echo ""
fi

# Create certbot directories
mkdir -p $APP_DIR/certbot/conf $APP_DIR/certbot/www

echo ""
echo "✅ VPS Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Upload .env.production and firebase-service-account.json if not done"
echo "2. Configure DNS to point $DOMAIN to this server"
echo "3. Run: cd $APP_DIR && ./init-letsencrypt.sh"
echo "4. Run: ./deploy.sh"
echo ""
echo "📍 Your app will be available at:"
echo "   Frontend: https://$DOMAIN"
echo "   API: https://api.$DOMAIN"
