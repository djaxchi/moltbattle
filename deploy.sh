#!/bin/bash
# =============================================================================
# MOLTBATTLE PRODUCTION DEPLOYMENT SCRIPT
# =============================================================================

set -e

echo "🚀 MoltClash Production Deployment"
echo "===================================="

# Check for required files
if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production not found!"
    echo "   Copy .env.production.example to .env.production and configure it."
    exit 1
fi

if [ ! -f "firebase-service-account.json" ]; then
    echo "❌ Error: firebase-service-account.json not found!"
    echo "   Download your Firebase service account key and place it in the root directory."
    exit 1
fi

# Load production environment
export $(grep -v '^#' .env.production | xargs)

echo ""
echo "📋 Configuration:"
echo "   Domain: ${DOMAIN:-moltclash.com}"
echo "   API URL: ${API_URL:-https://api.moltclash.com}"
echo "   Frontend URL: ${FRONTEND_URL:-https://moltclash.com}"
echo ""

# Create certbot directories if they don't exist
mkdir -p certbot/conf certbot/www

# Check if SSL certificates exist
if [ ! -d "certbot/conf/live/${DOMAIN:-moltclash.com}" ]; then
    echo "⚠️  SSL certificates not found. Running initial certificate setup..."
    echo ""
    echo "First, start nginx in HTTP-only mode to get certificates:"
    echo ""
    echo "1. Temporarily modify nginx/conf.d/moltclash.conf to serve HTTP only"
    echo "2. Run: docker-compose -f docker-compose.prod.yml up -d nginx"
    echo "3. Run: ./init-letsencrypt.sh"
    echo "4. Then run this script again"
    echo ""
    
    read -p "Continue without SSL? (for initial setup only) [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🔨 Building containers..."
docker-compose -f docker-compose.prod.yml build

echo ""
echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

echo ""
echo "🔍 Checking service status..."
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Services:"
echo "   Frontend: https://${DOMAIN:-moltclash.com}"
echo "   API: https://api.${DOMAIN:-moltclash.com}"
echo "   Health: https://api.${DOMAIN:-moltclash.com}/health"
echo ""
echo "📊 View logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
