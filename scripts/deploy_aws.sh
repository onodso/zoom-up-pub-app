#!/bin/bash
set -e

# Target host information
HOST="ubuntu@54.150.207.122"
KEY="~/.ssh/zoom-dx-prod.pem"
PROJECT_DIR="/home/ubuntu/zoom-up-pub-app"

echo "🚀 Starting deployment to AWS Lightsail..."

# Step 1: Push latest changes to current branch (Ensure remote has the latest code)
echo "📦 Pushing latest updates to origin..."
git push origin HEAD --force-with-lease || git push origin HEAD

# Step 2: Connect to AWS and pull/deploy
echo "🌐 Connecting to AWS Lightsail..."
ssh -i $KEY $HOST << 'EOF'
    set -e
    
    # Clone or Update Repo
    if [ ! -d "/home/ubuntu/zoom-up-pub-app" ]; then
        echo "📥 Cloning repository..."
        git clone https://github.com/onodso/zoom-up-pub-app.git /home/ubuntu/zoom-up-pub-app
        cd /home/ubuntu/zoom-up-pub-app
    else
        echo "🔄 Updating existing repository..."
        cd /home/ubuntu/zoom-up-pub-app
        git fetch --all
        git reset --hard origin/$(git rev-parse --abbrev-ref HEAD)
    fi

    # Update docker-compose.aws.yml for Vite compatibility if not already updated
    # Currently it points to NEXT_PUBLIC_API_URL which Next.js uses.
    # We will inject VITE_API_BASE into the frontend container.
    
    echo "⚙️ Creating environment file for frontend..."
    cat <<ENVFILE > frontend/.env.local
# AWS環境ではCaddyの同一オリジンへの相対パスを使用するため空にする
VITE_API_BASE=
ENVFILE

    echo "🐳 Building and starting Docker containers..."
    docker compose -f docker-compose.aws.yml build frontend
    docker compose -f docker-compose.aws.yml up -d frontend

    echo "🧹 Cleaning up old images..."
    docker image prune -f

    echo "✅ Health check..."
    docker compose -f docker-compose.aws.yml ps
EOF

echo "🎉 Deployment to AWS Lightsail completed!"
