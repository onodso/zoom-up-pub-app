#!/usr/bin/env python3
"""
Hubファイルからのデータ移行スクリプト
"""
import os
import sys
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import pandas as pd
    import psycopg2
    from psycopg2.extras import execute_batch
except ImportError:
    print("❌ 必要なパッケージがインストールされていません")
    print("   pip install pandas psycopg2-binary")
    sys.exit(1)

# データベース接続設定
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', 5432),
    'user': os.getenv('POSTGRES_USER', 'zoom_admin'),
    'password': os.getenv('POSTGRES_PASSWORD', 'changeme'),
    'database': os.getenv('POSTGRES_DB', 'zoom_dx_db')
}

# Hubファイルパス
HUB_DATA_DIR = Path(os.getenv('HUB_DATA_DIR', '/Users/sonodera/hub_files'))

# 地方区分マッピング
REGION_MAP = {
    '北海道': '北海道',
    '青森県': '東北', '岩手県': '東北', '宮城県': '東北',
    '秋田県': '東北', '山形県': '東北', '福島県': '東北',
    '茨城県': '関東', '栃木県': '関東', '群馬県': '関東',
    '埼玉県': '関東', '千葉県': '関東', '東京都': '関東', '神奈川県': '関東',
    '新潟県': '中部', '富山県': '中部', '石川県': '中部', '福井県': '中部',
    '山梨県': '中部', '長野県': '中部', '岐阜県': '中部',
    '静岡県': '中部', '愛知県': '中部',
    '三重県': '近畿', '滋賀県': '近畿', '京都府': '近畿',
    '大阪府': '近畿', '兵庫県': '近畿', '奈良県': '近畿', '和歌山県': '近畿',
    '鳥取県': '中国', '島根県': '中国', '岡山県': '中国',
    '広島県': '中国', '山口県': '中国',
    '徳島県': '四国', '香川県': '四国', '愛媛県': '四国', '高知県': '四国',
    '福岡県': '九州', '佐賀県': '九州', '長崎県': '九州', '熊本県': '九州',
    '大分県': '九州', '宮崎県': '九州', '鹿児島県': '九州', '沖縄県': '九州',
}


def migrate_localgov_master():
    """自治体マスタデータ移行"""
    logger.info("=== 自治体マスタデータ移行開始 ===")
    
    csv_path = HUB_DATA_DIR / 'localgov_master_full.csv'
    if not csv_path.exists():
        logger.warning(f"ファイルが見つかりません: {csv_path}")
        return 0
    
    df = pd.read_csv(csv_path)
    logger.info(f"読み込み: {len(df)}件")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    insert_sql = """
        INSERT INTO municipalities (
            code, prefecture, name, population, households, region,
            official_url, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (code) DO UPDATE SET
            population = EXCLUDED.population,
            households = EXCLUDED.households,
            updated_at = NOW()
    """
    
    data = []
    for _, row in df.iterrows():
        prefecture = row.get('都道府県名', row.get('prefecture', ''))
        data.append((
            str(row.get('団体コード', row.get('code', ''))),
            prefecture,
            row.get('市区町村名', row.get('name', '')),
            int(row.get('人口', row.get('population', 0)) or 0),
            int(row.get('世帯数', row.get('households', 0)) or 0),
            REGION_MAP.get(prefecture, '不明'),
            row.get('official_url', None)
        ))
    
    execute_batch(cur, insert_sql, data, page_size=1000)
    conn.commit()
    
    logger.info(f"✅ {len(data)}件の自治体データを移行しました")
    
    cur.close()
    conn.close()
    return len(data)


def migrate_dx_progress():
    """DX進捗データ移行"""
    logger.info("=== DX進捗データ移行開始 ===")
    
    csv_path = HUB_DATA_DIR / '市区町村毎のDX進捗状況_市区町村比較.csv'
    if not csv_path.exists():
        logger.warning(f"ファイルが見つかりません: {csv_path}")
        return 0
    
    df = pd.read_csv(csv_path)
    logger.info(f"読み込み: {len(df)}件")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # スコアテーブルへ挿入
    insert_sql = """
        INSERT INTO scores (
            municipality_id, score_dx_maturity, score_online_procedures,
            calculated_at, metadata
        )
        SELECT 
            m.id, %s, %s, NOW(), %s::jsonb
        FROM municipalities m
        WHERE m.code = %s
        ON CONFLICT DO NOTHING
    """
    
    data = []
    for _, row in df.iterrows():
        import json
        metadata = json.dumps({
            'source': 'DX進捗状況調査',
            'fiscal_year': 2024
        })
        data.append((
            float(row.get('DX成熟度', 0) or 0),
            float(row.get('オンライン申請率', 0) or 0),
            metadata,
            str(row.get('団体コード', ''))
        ))
    
    execute_batch(cur, insert_sql, data, page_size=1000)
    conn.commit()
    
    logger.info(f"✅ {len(data)}件のDX進捗データを移行しました")
    
    cur.close()
    conn.close()
    return len(data)


def main():
    """メイン処理"""
    logger.info("=" * 60)
    logger.info("Hubファイル移行スクリプト")
    logger.info("=" * 60)
    
    if not HUB_DATA_DIR.exists():
        logger.error(f"❌ Hubファイルディレクトリが見つかりません: {HUB_DATA_DIR}")
        logger.info("   環境変数 HUB_DATA_DIR を設定してください")
        sys.exit(1)
    
    try:
        count1 = migrate_localgov_master()
        count2 = migrate_dx_progress()
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("🎉 移行完了")
        logger.info(f"   自治体マスタ: {count1}件")
        logger.info(f"   DX進捗: {count2}件")
        logger.info("=" * 60)
        
    except psycopg2.OperationalError as e:
        logger.error(f"❌ データベース接続エラー: {e}")
        logger.info("   Docker が起動しているか確認してください")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ エラー発生: {e}")
        raise


if __name__ == '__main__':
    main()
