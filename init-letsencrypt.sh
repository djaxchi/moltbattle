#!/bin/bash
# =============================================================================
# LET'S ENCRYPT SSL CERTIFICATE INITIALIZATION
# =============================================================================
# Run this script once to obtain initial SSL certificates for moltclash.com
# =============================================================================

set -e

DOMAIN=${DOMAIN:-moltclash.com}
EMAIL=${EMAIL:-admin@moltclash.com}

echo "🔐 Let's Encrypt SSL Certificate Setup"
echo "======================================="
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Create required directories
mkdir -p certbot/conf certbot/www

# Check if certificates already exist
if [ -d "certbot/conf/live/$DOMAIN" ]; then
    echo "⚠️  Certificates already exist for $DOMAIN"
    read -p "Do you want to renew them? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo "📋 Step 1: Creating temporary nginx config for certificate validation..."

# Create temporary HTTP-only nginx config
cat > nginx/conf.d/temp-certbot.conf << EOF
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN api.$DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'Waiting for SSL setup...';
        add_header Content-Type text/plain;
    }
}
EOF

echo "📋 Step 2: Starting nginx for certificate validation..."
docker-compose -f docker-compose.prod.yml up -d nginx

echo "⏳ Waiting for nginx to start..."
sleep 5

echo "📋 Step 3: Obtaining SSL certificates..."
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN \
    -d api.$DOMAIN

echo "📋 Step 4: Removing temporary config..."
rm -f nginx/conf.d/temp-certbot.conf

echo "📋 Step 5: Restarting nginx with full config..."
docker-compose -f docker-compose.prod.yml restart nginx

echo ""
echo "✅ SSL certificates obtained successfully!"
echo ""
echo "Certificate location: certbot/conf/live/$DOMAIN/"
echo ""
echo "Next steps:"
echo "1. Run: ./deploy.sh"
echo ""
