#!/bin/bash
# AWS S3 同期スクリプト
set -e

BACKUP_DIR="${BACKUP_DIR:-/mnt/external_hdd/zoom-dx-backups}"
S3_BUCKET="${S3_BUCKET:-s3://zoom-dx-backups}"

echo "=== AWS S3 同期 ==="
echo "日時: $(date)"
echo "ローカル: $BACKUP_DIR"
echo "S3: $S3_BUCKET"

# AWS CLI確認
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI がインストールされていません"
    exit 1
fi

# 同期実行
echo "差分同期中..."
aws s3 sync "$BACKUP_DIR" "$S3_BUCKET" \
    --storage-class STANDARD_IA \
    --exclude "*" \
    --include "postgres_*.sql.gz"

echo "✅ S3同期完了"

# S3バケット内容確認
echo ""
echo "S3内のバックアップ一覧（最新5件）:"
aws s3 ls "$S3_BUCKET/" | grep "postgres_" | tail -5

echo ""
echo "=== 同期完了 ==="
