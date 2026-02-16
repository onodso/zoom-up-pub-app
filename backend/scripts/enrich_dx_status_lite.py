"""
DX Status Enrichment (Lite Version - Mock Data)
CSVファイルなしでモックデータを使用してdx_statusを設定
"""
import sys
import os
from pathlib import Path
import psycopg2
import json

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from backend.config import settings

def main():
    print("🚀 Starting DX Status Enrichment (Lite Mode - Mock Data)...")

    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )

    try:
        cur = conn.cursor()

        # Check if dx_status column exists
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'municipalities'
            AND column_name = 'dx_status'
        """)

        if not cur.fetchone():
            print("   ⚠️ dx_status column does not exist. Creating...")
            cur.execute("ALTER TABLE municipalities ADD COLUMN dx_status JSONB")
            conn.commit()
            print("   ✅ dx_status column created")

        # Get all municipalities
        cur.execute("SELECT city_code, city_name FROM municipalities LIMIT 100")
        cities = cur.fetchall()

        print(f"   📊 Processing {len(cities)} municipalities with mock DX status...")

        # Mock DX status data (varies by city)
        import random

        for city_code, city_name in cities:
            # Generate mock DX status
            mock_status = {
                "dept": random.choice([True, False]),  # DX専門部署あり
                "cio": random.choice(["あり", "なし"]),  # CIO任命
                "ext_cio": random.choice(["あり", "なし"]),  # 外部CIO
                "strategy": random.choice([True, False]),  # DX戦略策定済み
                "updated_at": "2026-02-13"
            }

            cur.execute("""
                UPDATE municipalities
                SET dx_status = %s
                WHERE city_code = %s
            """, (json.dumps(mock_status), city_code))

        conn.commit()
        print("✅ DX Status Enrichment Completed (Mock Data)")
        print("   💡 Note: Using randomized mock data for demonstration")

    except Exception as e:
        print(f"❌ Enrichment Failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
