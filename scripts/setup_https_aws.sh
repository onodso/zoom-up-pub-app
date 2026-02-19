#!/bin/bash
set -e

HOST="ubuntu@54.150.207.122"
KEY="~/.ssh/zoom-dx-prod.pem"

echo "🚀 Setting up Caddy for automatic HTTPS via nip.io..."

ssh -i $KEY $HOST << 'EOF'
    set -e
    cd /home/ubuntu/zoom-up-pub-app

    echo "⚙️ Creating Caddyfile..."
    cat <<CADDYFILE > Caddyfile
54-150-207-122.nip.io {
    reverse_proxy /api/* 100.107.246.40:8000
    reverse_proxy frontend:3000
}
CADDYFILE

    echo "⚙️ Updating docker-compose.aws.yml for Caddy..."
    cat <<COMPOSE > docker-compose.aws.yml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: zoom-dx-frontend
    expose:
      - "3000"
    environment:
      - NODE_ENV=production
      # ブラウザからは同一オリジンの相対パスでアクセスし、Caddyがリバースプロキシする
      - VITE_API_BASE=
    restart: unless-stopped

  caddy:
    image: caddy:2-alpine
    container_name: zoom-dx-caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - frontend

volumes:
  caddy_data:
  caddy_config:
COMPOSE

    echo "🐳 Restarting containers with Caddy..."
    docker compose -f docker-compose.aws.yml down
    docker compose -f docker-compose.aws.yml up -d

    echo "✅ Setup injected. Caddy is requesting an SSL certificate for 54-150-207-122.nip.io..."
EOF

echo "🎉 Done! It may take a minute for Let's Encrypt to issue the certificate."
