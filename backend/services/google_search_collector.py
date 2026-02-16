"""
Google Custom Search API Integration
自治体のDX関連ニュース、Zoom導入事例などを実データとして収集

必要な環境変数:
- GOOGLE_API_KEY: Google Cloud ConsoleのAPIキー
- GOOGLE_CSE_ID: Programmable Search EngineのID
"""

import httpx
import os
from typing import List, Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime


class GoogleNewsCollector:
    """Google Custom Search APIでニュース収集"""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.cse_id = os.getenv("GOOGLE_CSE_ID")

        if not self.api_key or not self.cse_id:
            raise ValueError(
                "Missing credentials. Set GOOGLE_API_KEY and GOOGLE_CSE_ID in .env"
            )

        self.api_url = "https://www.googleapis.com/customsearch/v1"
        self.client = httpx.Client(timeout=30.0)

    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        Google Custom Searchで検索

        Args:
            query: 検索クエリ（例: "福岡市 DX推進"）
            num_results: 取得件数（最大10）

        Returns:
            検索結果リスト [
                {
                    'title': 'ニュースタイトル',
                    'link': 'https://...',
                    'snippet': '要約',
                    'date': '2024-01-15'
                },
                ...
            ]
        """
        try:
            params = {
                'key': self.api_key,
                'cx': self.cse_id,
                'q': query,
                'num': min(num_results, 10),
                'lr': 'lang_ja',  # 日本語のみ
                'dateRestrict': 'y1',  # 過去1年以内
            }

            response = self.client.get(self.api_url, params=params)
            response.raise_for_status()

            data = response.json()

            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': item.get('displayLink', ''),
                    'date': self._extract_date(item)
                })

            return results

        except httpx.HTTPStatusError as e:
            print(f"❌ API Error: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

    def _extract_date(self, item: Dict) -> Optional[str]:
        """検索結果から日付を抽出"""
        # Google検索結果のメタデータから日付を取得
        if 'pagemap' in item and 'metatags' in item['pagemap']:
            metatags = item['pagemap']['metatags'][0]
            for date_field in ['article:published_time', 'datePublished', 'date']:
                if date_field in metatags:
                    return metatags[date_field][:10]  # YYYY-MM-DD形式

        return None

    def search_dx_news(self, city_name: str) -> List[Dict]:
        """DX関連ニュースを検索"""
        queries = [
            f"{city_name} DX推進",
            f"{city_name} デジタル化",
            f"{city_name} スマートシティ",
        ]

        all_results = []
        for query in queries:
            results = self.search(query, num_results=5)
            all_results.extend(results)

        # 重複削除
        unique_results = {r['link']: r for r in all_results}.values()
        return list(unique_results)

    def search_zoom_deployments(self, city_name: str) -> List[Dict]:
        """Zoom導入事例を検索"""
        query = f"{city_name} Zoom 導入"
        return self.search(query, num_results=10)

    def search_kasuhara_news(self, city_name: str) -> List[Dict]:
        """カスハラ関連ニュースを検索"""
        query = f"{city_name} カスハラ OR クレーム OR 苦情"
        return self.search(query, num_results=5)

    def close(self):
        self.client.close()


class NewsDataUpdater:
    """検索結果をデータベースに保存"""

    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER", "zoom_admin"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            dbname=os.getenv("POSTGRES_DB", "zoom_dx_db")
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        self.create_table()

    def create_table(self):
        """ニューステーブル作成"""
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS municipality_news (
                id SERIAL PRIMARY KEY,
                city_code VARCHAR(6),
                category VARCHAR(50),  -- dx, zoom, kasuhara
                title TEXT,
                url TEXT UNIQUE,
                snippet TEXT,
                source VARCHAR(200),
                published_date DATE,
                collected_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY (city_code) REFERENCES municipalities(city_code)
            );

            CREATE INDEX IF NOT EXISTS idx_news_city_category
            ON municipality_news(city_code, category);
        """)
        self.conn.commit()

    def save_news(self, city_code: str, category: str, news_list: List[Dict]):
        """ニュースを保存"""
        saved_count = 0

        for news in news_list:
            try:
                self.cur.execute("""
                    INSERT INTO municipality_news
                        (city_code, category, title, url, snippet, source, published_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING;
                """, (
                    city_code,
                    category,
                    news['title'],
                    news['link'],
                    news['snippet'],
                    news['source'],
                    news['date']
                ))

                if self.cur.rowcount > 0:
                    saved_count += 1

            except Exception as e:
                print(f"⚠️  Failed to save: {e}")

        self.conn.commit()
        return saved_count

    def get_news_summary(self, city_code: str) -> Dict:
        """自治体のニュースサマリーを取得"""
        self.cur.execute("""
            SELECT category, COUNT(*) as count
            FROM municipality_news
            WHERE city_code = %s
            GROUP BY category;
        """, (city_code,))

        summary = {row['category']: row['count'] for row in self.cur.fetchall()}
        return summary

    def close(self):
        self.cur.close()
        self.conn.close()


def collect_news_for_city(city_code: str, city_name: str):
    """
    1つの自治体のニュースを収集

    Args:
        city_code: 自治体コード
        city_name: 自治体名
    """
    print(f"\n{'='*80}")
    print(f"Collecting news for: {city_name} ({city_code})")
    print(f"{'='*80}")

    collector = GoogleNewsCollector()
    updater = NewsDataUpdater()

    try:
        # 1. DX関連ニュース
        print(f"\n🔍 Searching DX news...")
        dx_news = collector.search_dx_news(city_name)
        saved = updater.save_news(city_code, 'dx', dx_news)
        print(f"✅ Found {len(dx_news)} articles, saved {saved} new ones")

        if dx_news[:3]:
            print(f"\n📰 Top 3 DX news:")
            for idx, news in enumerate(dx_news[:3], 1):
                print(f"   {idx}. {news['title'][:60]}...")
                print(f"      {news['link']}")

        # 2. Zoom導入事例
        print(f"\n🔍 Searching Zoom deployments...")
        zoom_news = collector.search_zoom_deployments(city_name)
        saved = updater.save_news(city_code, 'zoom', zoom_news)
        print(f"✅ Found {len(zoom_news)} articles, saved {saved} new ones")

        # 3. カスハラニュース
        print(f"\n🔍 Searching kasuhara news...")
        kasuhara_news = collector.search_kasuhara_news(city_name)
        saved = updater.save_news(city_code, 'kasuhara', kasuhara_news)
        print(f"✅ Found {len(kasuhara_news)} articles, saved {saved} new ones")

        # サマリー表示
        summary = updater.get_news_summary(city_code)
        print(f"\n📊 Total news in database:")
        print(f"   DX: {summary.get('dx', 0)}")
        print(f"   Zoom: {summary.get('zoom', 0)}")
        print(f"   Kasuhara: {summary.get('kasuhara', 0)}")

        print(f"\n{'='*80}\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        collector.close()
        updater.close()


if __name__ == "__main__":
    # テスト: 福岡市のニュース収集
    print("🚀 Google Custom Search API - News Collection Test")
    print("=" * 80)

    # 認証情報チェック
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")

    if not api_key or not cse_id:
        print("❌ Missing credentials!")
        print("\nPlease add to .env:")
        print("  GOOGLE_API_KEY=your_api_key")
        print("  GOOGLE_CSE_ID=your_search_engine_id")
        print("\nGet credentials from:")
        print("  API Key: https://console.cloud.google.com/apis/credentials")
        print("  CSE ID:  https://programmablesearchengine.google.com/")
    else:
        print(f"✅ API Key: {api_key[:10]}...")
        print(f"✅ CSE ID:  {cse_id[:20]}...")
        print()

        # 福岡市でテスト
        collect_news_for_city('401307', '福岡市')
