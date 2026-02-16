"""
Collect News for Top Municipalities
人口上位の自治体を対象に、DX・Zoom・カスハラ関連のニュースを収集するスクリプト

API制限（1日100回無料を想定）を考慮し、
まずは Top 10 自治体 × 3カテゴリ = 30クエリ で実行する。
"""

import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from google_search_collector import GoogleNewsCollector, NewsDataUpdater

# APIレートリミット対策
# 無料枠: 1,500リクエスト/日
# 別アプリ使用: 50-150回/日（平均100回）
# 本アプリ目標: 1,020回/日 (340自治体 × 3カテゴリ)
# 合計: 1,120-1,170回/日 (無料枠の75%程度)
# 全2,406自治体を8日間で完了
BATCH_SIZE = 340
SLEEP_BETWEEN_QUERIES = 1.0

def get_next_batch_municipalities(limit: int):
    """
    ニュース収集対象の自治体を取得（ローテーション）
    
    1. 人口上位500自治体を対象とする
    2. その中で、ニュース最終収集日時(collected_at)が古い順、
       または未収集(NULL)の自治体を優先して取得する
    """
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        user=os.getenv("POSTGRES_USER", "zoom_admin"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
        dbname=os.getenv("POSTGRES_DB", "zoom_dx_db")
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # 複雑なクエリになるため、CTEを使用
        cur.execute("""
            WITH top_500 AS (
                SELECT city_code, city_name, prefecture, population
                FROM municipalities
                WHERE population IS NOT NULL
                ORDER BY population DESC
                LIMIT 500
            ),
            latest_collection AS (
                SELECT city_code, MAX(collected_at) as last_collected
                FROM municipality_news
                GROUP BY city_code
            )
            SELECT 
                t.city_code, 
                t.city_name, 
                t.prefecture, 
                t.population,
                l.last_collected
            FROM top_500 t
            LEFT JOIN latest_collection l ON t.city_code = l.city_code
            ORDER BY l.last_collected ASC NULLS FIRST
            LIMIT %s;
        """, (limit,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def main():
    print(f"🚀 Starting Daily News Collection (Batch Size: {BATCH_SIZE})")
    print("=" * 60)
    
    # APIキー確認
    if not os.getenv("GOOGLE_API_KEY") or not os.getenv("GOOGLE_CSE_ID"):
        print("❌ Error: GOOGLE_API_KEY and GOOGLE_CSE_ID must be set.")
        return

    try:
        municipalities = get_next_batch_municipalities(BATCH_SIZE)
        print(f"📋 Target Municipalities: {len(municipalities)}")
        for m in municipalities:
            last_date = m.get('last_collected')
            status = f"Last processed: {last_date}" if last_date else "Never processed"
            print(f"   - {m['city_name']} ({m['prefecture']}): {status}")
        print("-" * 60)
        
        collector = GoogleNewsCollector()
        updater = NewsDataUpdater()
        
        total_queries = 0
        total_saved = 0
        
        for i, muni in enumerate(municipalities, 1):
            city_code = muni['city_code']
            city_name = muni['city_name']
            
            print(f"\n[{i}/{len(municipalities)}] Processing: {city_name}")
            
            try:
                # 1. DX News
                print("   🔍 DX News...", end="", flush=True)
                dx_news = collector.search_dx_news(city_name)
                saved_dx = updater.save_news(city_code, 'dx', dx_news)
                print(f" Found {len(dx_news)}, Saved {saved_dx}")
                time.sleep(SLEEP_BETWEEN_QUERIES)
                total_queries += 1 # search_dx_news内で複数クエリ投げている場合は修正が必要だが、一旦簡易カウント
                
                # 2. Zoom News
                print("   🔍 Zoom News...", end="", flush=True)
                zoom_news = collector.search_zoom_deployments(city_name)
                saved_zoom = updater.save_news(city_code, 'zoom', zoom_news)
                print(f" Found {len(zoom_news)}, Saved {saved_zoom}")
                time.sleep(SLEEP_BETWEEN_QUERIES)
                total_queries += 1
                
                # 3. Kasuhara News
                print("   🔍 Kasuhara News...", end="", flush=True)
                kasuhara_news = collector.search_kasuhara_news(city_name)
                saved_kasuhara = updater.save_news(city_code, 'kasuhara', kasuhara_news)
                print(f" Found {len(kasuhara_news)}, Saved {saved_kasuhara}")
                time.sleep(SLEEP_BETWEEN_QUERIES)
                total_queries += 1
                
                total_saved += (saved_dx + saved_zoom + saved_kasuhara)
                
            except Exception as e:
                print(f"\n❌ Error processing {city_name}: {e}")
                # エラーが出ても続行
        
        print("\n" + "=" * 60)
        print("✅ Collection Complete!")
        print(f"   Total Municipalities: {len(municipalities)}")
        print(f"   Total Saved Articles: {total_saved}")
        print(f"   Est. Queries Used:    ~{total_queries} (plus internal multi-queries)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
