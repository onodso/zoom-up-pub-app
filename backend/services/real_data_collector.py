"""
Real Data Collector - NO DUMMY DATA
実データのみを収集する。ダミーデータは一切使用しない。

収集可能な実データソース:
1. 総務省 地方公共団体情報システム機構（J-LIS）
2. 各自治体の公式サイト（市長名、組織図）
3. 国土地理院（正確な緯度経度）
4. 総務省統計（財政状況）
5. Googleニュース検索（DX関連ニュース）
"""

import httpx
import re
import json
from typing import Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time


class RealDataCollector:
    """実データ収集エンジン - ダミーデータ禁止"""

    def __init__(self):
        self.client = httpx.Client(timeout=30.0, follow_redirects=True)
        self.conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER", "zoom_admin"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            dbname=os.getenv("POSTGRES_DB", "zoom_dx_db")
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

    def scrape_mayor_from_official_site(self, city_code: str, official_url: str) -> Optional[str]:
        """
        自治体公式サイトから市長名を実際にスクレイピング

        Returns:
            市長名（実データ）または None
        """
        if not official_url:
            return None

        try:
            # 市長挨拶・市長室ページを探す
            mayor_keywords = ['市長', '町長', '村長', '区長', '首長']
            page_patterns = [
                '/mayor/',
                '/shicho/',
                '/message/',
                '/greeting/',
                '/profile/',
            ]

            # メインページを取得
            response = self.client.get(official_url)
            if response.status_code != 200:
                print(f"⚠️  {official_url}: HTTP {response.status_code}")
                return None

            html = response.text

            # 市長ページのリンクを探す
            mayor_page_url = None
            for pattern in page_patterns:
                if pattern in html.lower():
                    # リンクを抽出（簡易版）
                    match = re.search(rf'href=["\']([^"\']*{pattern}[^"\']*)["\']', html, re.IGNORECASE)
                    if match:
                        link = match.group(1)
                        if link.startswith('http'):
                            mayor_page_url = link
                        else:
                            mayor_page_url = official_url.rstrip('/') + '/' + link.lstrip('/')
                        break

            if not mayor_page_url:
                # メインページから直接市長名を探す
                return self._extract_mayor_name_from_html(html)

            # 市長ページを取得
            response = self.client.get(mayor_page_url)
            if response.status_code == 200:
                return self._extract_mayor_name_from_html(response.text)

            return None

        except Exception as e:
            print(f"❌ Scraping error for {official_url}: {e}")
            return None

    def _extract_mayor_name_from_html(self, html: str) -> Optional[str]:
        """
        HTMLから市長名を抽出

        パターン:
        - "市長 山田太郎"
        - "市長：田中花子"
        - "○○市長 鈴木一郎"
        """
        patterns = [
            r'市長[：:\s]+([^\s<>]{2,5})',
            r'町長[：:\s]+([^\s<>]{2,5})',
            r'村長[：:\s]+([^\s<>]{2,5})',
            r'区長[：:\s]+([^\s<>]{2,5})',
        ]

        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                name = match.group(1)
                # 「様」「さん」などを除去
                name = re.sub(r'[様さん殿氏]$', '', name)
                # 漢字のみ（2-4文字）であることを確認
                if re.match(r'^[一-龯]{2,4}$', name):
                    return name

        return None

    def search_dx_news(self, city_name: str, keyword: str) -> list:
        """
        Google検索で実際のDX関連ニュースを収集

        Args:
            city_name: 自治体名
            keyword: 検索キーワード（例: "DX推進", "Zoom導入"）

        Returns:
            ニュース記事リスト（実データ）
        """
        try:
            # Google Custom Search API使用（または通常のGoogle検索）
            query = f"{city_name} {keyword}"

            # シンプルなGoogle検索（APIキーがない場合の代替）
            search_url = "https://www.google.com/search"
            params = {
                'q': query,
                'num': 10,
                'hl': 'ja'
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = self.client.get(search_url, params=params, headers=headers)

            if response.status_code == 200:
                # 実際のニュースタイトルを抽出
                titles = re.findall(r'<h3[^>]*>([^<]+)</h3>', response.text)
                return titles[:5]  # 上位5件

            return []

        except Exception as e:
            print(f"❌ News search error: {e}")
            return []

    def get_fiscal_data_from_soumu(self, city_code: str) -> Optional[Dict]:
        """
        総務省の公開データから財政情報を取得（実データ）

        データソース: 総務省「地方財政状況調査」
        """
        try:
            # 総務省の公開データポータル
            # 実際のURLは総務省のデータカタログから取得

            # 現時点では財政力指数は既にDBにあるので、それを利用
            self.cur.execute("""
                SELECT fiscal_index
                FROM municipalities
                WHERE city_code = %s AND fiscal_index IS NOT NULL;
            """, (city_code,))

            result = self.cur.fetchone()
            if result:
                return {'fiscal_index': result['fiscal_index']}

            return None

        except Exception as e:
            print(f"❌ Fiscal data error: {e}")
            return None

    def validate_and_save_mayor(self, city_code: str, mayor_name: str, source_url: str):
        """
        市長名をバリデーションして保存（実データのみ）

        バリデーション:
        - 漢字のみ（2-4文字）
        - ソースURLが記録されている
        """
        if not mayor_name:
            return False

        # バリデーション
        if not re.match(r'^[一-龯]{2,4}$', mayor_name):
            print(f"⚠️  Invalid mayor name format: {mayor_name}")
            return False

        # データベースに保存
        self.cur.execute("""
            UPDATE municipalities
            SET mayor_name = %s,
                mayor_speech_url = %s,
                updated_at = NOW()
            WHERE city_code = %s
            RETURNING city_name;
        """, (mayor_name, source_url, city_code))

        result = self.cur.fetchone()
        if result:
            print(f"✅ {result['city_name']}: 市長名を更新 → {mayor_name} (Source: {source_url})")
            self.conn.commit()
            return True

        return False

    def collect_real_data_for_municipality(self, city_code: str):
        """
        1つの自治体の実データを収集

        収集項目:
        1. 市長名（公式サイトからスクレイピング）
        2. DX関連ニュース（Google検索）
        3. 財政情報（総務省データ）
        """
        # 自治体情報取得
        self.cur.execute("""
            SELECT city_code, city_name, official_url, mayor_name
            FROM municipalities
            WHERE city_code = %s;
        """, (city_code,))

        muni = self.cur.fetchone()
        if not muni:
            print(f"❌ Municipality {city_code} not found")
            return

        print(f"\n{'='*80}")
        print(f"Collecting REAL data for: {muni['city_name']} ({city_code})")
        print(f"{'='*80}")

        # 1. 市長名収集（既に市長名がある場合はスキップ）
        if not muni['mayor_name'] and muni['official_url']:
            print(f"\n🔍 Scraping mayor name from {muni['official_url']}...")
            mayor_name = self.scrape_mayor_from_official_site(city_code, muni['official_url'])

            if mayor_name:
                self.validate_and_save_mayor(city_code, mayor_name, muni['official_url'])
            else:
                print(f"⚠️  Could not extract mayor name")

        # 2. DXニュース検索
        print(f"\n📰 Searching DX news...")
        news = self.search_dx_news(muni['city_name'], 'DX推進')
        if news:
            print(f"✅ Found {len(news)} news articles:")
            for idx, title in enumerate(news[:3], 1):
                print(f"   {idx}. {title[:60]}...")

        # 3. 財政データ
        print(f"\n💰 Checking fiscal data...")
        fiscal = self.get_fiscal_data_from_soumu(city_code)
        if fiscal:
            print(f"✅ Fiscal index: {fiscal['fiscal_index']}")

        print(f"\n{'='*80}\n")

        # Rate limiting
        time.sleep(2)

    def close(self):
        self.cur.close()
        self.conn.close()
        self.client.close()


def collect_real_data_batch(city_codes: list):
    """
    複数自治体の実データを一括収集

    Args:
        city_codes: 自治体コードのリスト
    """
    print("=" * 80)
    print("REAL DATA COLLECTION - NO DUMMY DATA")
    print("=" * 80)
    print(f"\nTarget: {len(city_codes)} municipalities")
    print()

    collector = RealDataCollector()

    try:
        for city_code in city_codes:
            collector.collect_real_data_for_municipality(city_code)

    finally:
        collector.close()


if __name__ == "__main__":
    # パイロット17自治体の実データを収集
    pilot_cities = [
        '401307',  # 福岡市
        '401005',  # 北九州市
        '402141',  # 宗像市
    ]

    print("🚀 Starting REAL data collection...")
    print("⚠️  NO DUMMY DATA - Only collecting actual information from public sources")
    print()

    collect_real_data_batch(pilot_cities)

    print("\n✅ Real data collection complete")
    print("📊 Check database for updated information")
