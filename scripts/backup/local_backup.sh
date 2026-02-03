#!/bin/bash
# ローカルバックアップスクリプト
set -e

BACKUP_DIR="${BACKUP_DIR:-/mnt/external_hdd/zoom-dx-backups}"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

echo "=== Zoom DX ローカルバックアップ ==="
echo "日時: $(date)"
echo "保存先: $BACKUP_DIR"

# ディレクトリ確認
mkdir -p "$BACKUP_DIR"

# PostgreSQL フルバックアップ
echo "PostgreSQL バックアップ中..."
docker exec zoom-dx-postgres pg_dump \
    -U "${POSTGRES_USER:-zoom_admin}" \
    "${POSTGRES_DB:-zoom_dx_db}" \
    | gzip > "$BACKUP_DIR/postgres_$DATE.sql.gz"

BACKUP_SIZE=$(ls -lh "$BACKUP_DIR/postgres_$DATE.sql.gz" | awk '{print $5}')
echo "✅ バックアップ完了: postgres_$DATE.sql.gz ($BACKUP_SIZE)"

# 世代管理
echo "古いバックアップを削除中（${RETENTION_DAYS}日以上前）..."
DELETED_COUNT=$(find "$BACKUP_DIR" -name "postgres_*.sql.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
echo "  削除ファイル数: $DELETED_COUNT"

# 現在のバックアップ一覧
echo ""
echo "現在のバックアップ一覧:"
ls -lh "$BACKUP_DIR"/postgres_*.sql.gz 2>/dev/null | tail -5 || echo "  (なし)"

echo ""
echo "=== バックアップ完了 ==="
