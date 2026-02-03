#!/bin/bash
# AWS Lightsail デプロイスクリプト
set -e

LIGHTSAIL_IP="${LIGHTSAIL_IP:-your-lightsail-ip}"
REMOTE_PATH="/home/ubuntu/zoom-up-pub-app"

echo "=== AWS Lightsail デプロイ ==="
echo "日時: $(date)"
echo "デプロイ先: ubuntu@$LIGHTSAIL_IP:$REMOTE_PATH"

# 1) フロントエンドビルド
echo ""
echo "1/4 フロントエンドビルド中..."
cd frontend
npm run build
cd ..

# 2) ファイル転送
echo ""
echo "2/4 ファイル転送中..."
rsync -avz --delete \
    --exclude 'node_modules' \
    --exclude '.git' \
    --exclude '.next' \
    --exclude 'data/cache' \
    --exclude '__pycache__' \
    --exclude '.env' \
    . ubuntu@$LIGHTSAIL_IP:$REMOTE_PATH/

# 3) リモートでDockerコンテナ再ビルド＆起動
echo ""
echo "3/4 リモートでDocker再起動中..."
ssh ubuntu@$LIGHTSAIL_IP << 'EOF'
cd /home/ubuntu/zoom-up-pub-app
docker compose -f docker-compose.aws.yml down
docker compose -f docker-compose.aws.yml build --no-cache
docker compose -f docker-compose.aws.yml up -d
EOF

# 4) ヘルスチェック
echo ""
echo "4/4 ヘルスチェック中..."
sleep 10
if curl -sf "http://$LIGHTSAIL_IP:8000/api/health" > /dev/null; then
    echo "✅ API ヘルスチェック OK"
else
    echo "⚠️  API ヘルスチェック失敗"
fi

echo ""
echo "=== デプロイ完了 ==="
echo "URL: https://dx.kikagaku-zoom.com"
