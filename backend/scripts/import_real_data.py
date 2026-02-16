"""
実データインポートスクリプト

以下のデータソースからDBを更新する:
1. localgov_master_full_original.csv → 自治体マスタに緯度/経度を追加
2. 市区町村毎のDX進捗状況_市区町村比較.csv → dx_progress テーブルに格納
3. 市区町村毎のDX進捗状況_行政手続のオンライン申請率.csv → dx_progress テーブルに格納

使い方:
  docker compose exec backend python scripts/import_real_data.py
  または
  cd backend && python scripts/import_real_data.py
"""

import os
import csv
import sys
import re
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# /app がPYTHONPATHに含まれている想定
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models.municipality import Municipality, Base
from models.dx_progress import DxProgress

# DB接続設定（database.py と同じ環境変数を使用）
POSTGRES_USER = os.getenv("POSTGRES_USER", "zoom_admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_secure_password_here")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "zoom_dx_db")
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# データファイルのパス（Docker内では /app/data/、ローカルでは相対パス）
DATA_DIR = os.getenv("DATA_DIR", "/app/data/manual_add")

# DX進捗CSVのカテゴリ名→DBカテゴリ名の対応表
DX_CATEGORY_MAP = {
    "CIOの任命": "cio_appointed",
    "CIO補佐官等の任命": "cio_assistant",
    "全体方針策定": "dx_strategy",
    "全庁的な体制構築": "cross_dept_team",
    "外部人材活用": "external_talent",
    "職員育成の取組": "staff_training",
    "全職員対象研修の実施": "all_staff_training",
    "AIの導入状況": "ai_deployed",
    "RPAの導入状況": "rpa_deployed",
    "テレワークの導入状況": "telework_enabled",
    "マイナンバーカードの保有状況": "mynumber_rate",
    "子育て・介護26手続のオンライン化状況 ": "childcare_online",
    "子育て・介護26手続のオンライン化状況": "childcare_online",
    "よく使う32手続のオンライン化状況": "common32_online",
}

# テキスト値→数値変換
VALUE_MAP = {
    "実施": 1.0,
    "未実施": 0.0,
    "調査無し": None,
    "": None,
}


def import_geo_data(session):
    """
    localgov_master_full_original.csv から
    緯度/経度/URLを既存の municipalities レコードに上書き。
    """
    csv_path = os.path.join(DATA_DIR, "localgov_master_full_original.csv")
    if not os.path.exists(csv_path):
        print(f"⚠️  ファイルが見つかりません: {csv_path}")
        return 0

    print(f"📍 地理データ読み込み: {csv_path}")
    updated = 0
    skipped = 0

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lgcode = row.get('lgcode', '').strip()
            if not lgcode:
                skipped += 1
                continue

            lat = _safe_float(row.get('lat'))
            lng = _safe_float(row.get('lng'))
            url = row.get('url', '').strip()

            if lat is None or lng is None:
                skipped += 1
                continue

            # 既存レコードを更新
            muni = session.query(Municipality).filter_by(code=lgcode).first()
            if muni:
                muni.latitude = lat
                muni.longitude = lng
                if url:
                    muni.official_url = url
                updated += 1
            else:
                skipped += 1

    session.commit()
    print(f"  ✅ 更新: {updated} 件 / スキップ: {skipped} 件")
    return updated


def import_dx_progress(session):
    """
    市区町村毎のDX進捗状況_市区町村比較.csv を
    横持ち→縦持ちに変換して dx_progress テーブルに格納。
    """
    csv_path = os.path.join(DATA_DIR, "市区町村毎のDX進捗状況_市区町村比較.csv")
    if not os.path.exists(csv_path):
        print(f"⚠️  ファイルが見つかりません: {csv_path}")
        return 0

    print(f"📊 DX進捗データ読み込み: {csv_path}")

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Row 0 = ヘッダー行（空, 空, 札幌市, 函館市, ...）
    header = rows[0]
    municipality_names = header[2:]  # 先頭2列はカテゴリ/サブカテゴリ

    # 自治体名→自治体コードのマッピングを構築
    all_munis = session.query(Municipality).all()
    name_to_code = {}
    for m in all_munis:
        name_to_code[m.name] = m.code
        # 「市」「区」「町」「村」の部分一致も考慮
        # 例: CSV上の「渋谷区」→ DBの「渋谷区」
        # 特別区は「東京都 渋谷区」ではなく「渋谷区」のケースも
        clean_name = m.name.replace(' ', '')
        name_to_code[clean_name] = m.code

    # 既存データをクリア（全件入れ直し）
    deleted = session.query(DxProgress).filter_by(
        source="gov_dx_dashboard"
    ).delete()
    print(f"  🗑  既存DXデータ削除: {deleted} 件")

    # 横持ち→縦持ち変換
    inserted = 0
    unmatched_names = set()

    for row in rows[1:]:
        # row[0] = 大カテゴリ（自治体DXの推進体制等 等）
        # row[1] = サブカテゴリ名（CIOの任命 等）
        sub_category = row[1].strip()
        db_category = DX_CATEGORY_MAP.get(sub_category)

        if not db_category:
            # 分母/分子行などはスキップ
            continue

        for col_idx, muni_name in enumerate(municipality_names):
            muni_name = muni_name.strip()
            if not muni_name:
                continue

            code = name_to_code.get(muni_name)
            if not code:
                unmatched_names.add(muni_name)
                continue

            raw_value = row[col_idx + 2].strip() if col_idx + 2 < len(row) else ""

            # パーセンテージ値の処理
            numeric_value = None
            if raw_value in VALUE_MAP:
                numeric_value = VALUE_MAP[raw_value]
            elif raw_value.endswith('%'):
                numeric_value = _safe_float(raw_value.rstrip('%'))

            progress = DxProgress(
                municipality_code=code,
                municipality_name=muni_name,
                category=db_category,
                value=numeric_value,
                value_text=raw_value if raw_value else None,
                source="gov_dx_dashboard",
            )
            session.add(progress)
            inserted += 1

    session.commit()
    print(f"  ✅ 挿入: {inserted} 件")

    if unmatched_names:
        print(f"  ⚠️  マッチしなかった自治体名: {len(unmatched_names)} 件")
        # 上位10件を表示
        for name in sorted(unmatched_names)[:10]:
            print(f"    - {name}")

    return inserted


def import_online_rate(session):
    """
    市区町村毎のDX進捗状況_行政手続のオンライン申請率.csv を読み込み。
    こちらは横持ちだが構造が異なる（手続ごとの申請率）。
    まずは概要だけ取得して summary として格納。
    """
    csv_path = os.path.join(DATA_DIR, "市区町村毎のDX進捗状況_行政手続のオンライン申請率.csv")
    if not os.path.exists(csv_path):
        print(f"⚠️  ファイルが見つかりません: {csv_path}")
        return 0

    print(f"📋 オンライン申請率データ: {csv_path}")
    # このCSVは53行×1744列以上の大きなデータ
    # 現段階では構造が複雑なので、段階1以降で詳細パースする
    print(f"  ℹ️  このデータは段階1で詳細パース予定（構造が複雑）")
    return 0


def _safe_float(val):
    """安全な float 変換"""
    if val is None:
        return None
    try:
        return float(str(val).strip())
    except (ValueError, TypeError):
        return None


def ensure_tables(engine):
    """新規テーブルがなければ作成（既存テーブルには影響しない）"""
    Base.metadata.create_all(engine, checkfirst=True)
    print("✅ テーブル構造確認完了")


def main():
    print("=" * 60)
    print(f"実データインポート開始: {datetime.now()}")
    print("=" * 60)

    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # テーブル確認・作成
        ensure_tables(engine)

        # 1. 地理データ（lat/lng）
        geo_count = import_geo_data(session)

        # 2. DX進捗データ
        dx_count = import_dx_progress(session)

        # 3. オンライン申請率（概要のみ）
        online_count = import_online_rate(session)

        print("=" * 60)
        print(f"完了サマリー:")
        print(f"  地理データ更新: {geo_count} 件")
        print(f"  DX進捗挿入: {dx_count} 件")
        print(f"  オンライン申請率: {online_count} 件")
        print("=" * 60)

    except Exception as e:
        session.rollback()
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    main()
