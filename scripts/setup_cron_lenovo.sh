#!/bin/bash

# scripts/setup_cron_lenovo.sh
# Lenovo Tiny (WSL2) 用の定期実行設定スクリプト

LOG_DIR="/var/log/zoom-dx"
PROJECT_DIR=$(pwd)
CRON_FILE="zoom-dx-cron"

echo "⏰ Setting up Nightly Scoring Cron Job..."

# 1. ログディレクトリ作成
if [ ! -d "$LOG_DIR" ]; then
    echo "Creating log directory: $LOG_DIR"
    sudo mkdir -p $LOG_DIR
    sudo chown $(whoami):$(whoami) $LOG_DIR
fi

# 2. Cronファイル作成
# 毎日 AM 3:00 に実行
# Dockerコンテナ内で実行するため、docker execを使用
echo "Creating cron entry..."
cat > $CRON_FILE <<EOF
# Zoom City DX Nightly Scoring (Daily at 03:00 JST)
0 3 * * * cd $PROJECT_DIR && docker compose -f docker-compose.lenovo.yml exec -T api python3 scripts/nightly_scoring.py >> $LOG_DIR/nightly_scoring.log 2>&1
EOF

# 3. Crontabへの登録
if crontab -l | grep -q "Zoom City DX Nightly Scoring"; then
    echo "⚠️  Cron job already exists. Skipping."
else
    # 既存のcrontabをバックアップして追記
    crontab -l > mycron.backup 2>/dev/null
    cat $CRON_FILE >> mycron.backup
    crontab mycron.backup
    rm mycron.backup
    echo "✅ Cron job registered."
fi

rm $CRON_FILE

echo "=================================================="
echo "Current Crontab:"
crontab -l
echo "=================================================="
echo "🎉 Setup Complete. Logs will be at: $LOG_DIR/nightly_scoring.log"
