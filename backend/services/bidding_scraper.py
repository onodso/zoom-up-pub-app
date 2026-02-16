"""
Municipality IT Bidding Information Scraper
自治体のIT関連入札情報を収集し、以下を判定:
1. PBXベンダー・機種
2. Microsoft 365契約有無・ライセンス種類
3. Web会議ツール
4. グループウェア
5. 庁内ネットワーク更新時期

データソース:
- 調達ポータル (https://www.chotatuportal.jp/)
- 各自治体の入札情報ページ
"""

import httpx
# from bs4 import BeautifulSoup  # Will install later
import re
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time
from datetime import datetime

class BiddingInfoScraper:
    """入札情報スクレイパー"""

    # キーワードパターン
    KEYWORDS = {
        'pbx': [
            '電話交換機', 'PBX', '構内交換機', '電話設備',
            'ビジネスフォン', '内線電話', 'IP電話交換'
        ],
        'microsoft': [
            'Microsoft 365', 'M365', 'Office 365', 'O365',
            'Microsoft Teams', 'SharePoint', 'Exchange'
        ],
        'web_meeting': [
            'Web会議', 'ビデオ会議', 'オンライン会議',
            'Zoom', 'Teams', 'Webex', 'Google Meet'
        ],
        'groupware': [
            'グループウェア', 'サイボウズ', 'デスクネッツ',
            'J-MOTTO', 'Office 365'
        ],
        'network': [
            '庁内ネットワーク', 'LAN更新', 'ネットワーク機器',
            'スイッチ', 'ルータ', 'ファイアウォール'
        ]
    }

    # ベンダーパターン
    VENDORS = {
        'pbx': {
            'NEC': ['NEC', 'Aspire', 'UNIVERGE'],
            '富士通': ['富士通', 'FUJITSU', 'IP-PBX'],
            'Cisco': ['Cisco', 'シスコ', 'Unified'],
            '日立': ['日立', 'HITACHI'],
            'Panasonic': ['パナソニック', 'Panasonic'],
        },
        'microsoft_license': {
            'E5': ['E5', 'Enterprise E5', 'Microsoft 365 E5'],
            'E3': ['E3', 'Enterprise E3', 'Microsoft 365 E3'],
            'A5': ['A5', 'Microsoft 365 A5'],  # 教育機関向け
            'A3': ['A3', 'Microsoft 365 A3'],
        }
    }

    def __init__(self):
        self.client = httpx.Client(timeout=30.0)

    def search_chotatsu_portal(self, city_name: str, keyword: str) -> List[Dict]:
        """
        調達ポータルを検索

        Args:
            city_name: 自治体名
            keyword: 検索キーワード

        Returns:
            入札情報リスト
        """
        results = []

        try:
            # 調達ポータルの検索URL（仮）
            search_url = "https://www.chotatuportal.jp/search"
            params = {
                "keyword": f"{city_name} {keyword}",
                "year": "2020-2025"
            }

            # TODO: 実際のAPIエンドポイントに応じて実装
            # response = self.client.get(search_url, params=params)

            # ダミーデータ（テスト用）
            results.append({
                'title': f'{keyword}更新業務',
                'date': '2024-01-01',
                'amount': 50000000,
                'vendor': 'Unknown',
                'description': ''
            })

        except Exception as e:
            print(f"⚠️  Search error: {e}")

        return results

    def extract_pbx_info(self, text: str) -> Optional[Dict]:
        """
        PBX情報を抽出

        Returns:
            {
                'vendor': 'NEC',
                'model': 'UNIVERGE Aspire X',
                'extension_count': 800,
                'year': 2023
            }
        """
        result = {
            'vendor': None,
            'model': None,
            'extension_count': None,
            'year': None
        }

        # ベンダー検出
        for vendor, patterns in self.VENDORS['pbx'].items():
            for pattern in patterns:
                if pattern in text:
                    result['vendor'] = vendor
                    break
            if result['vendor']:
                break

        # 内線数抽出
        extension_match = re.search(r'内線.*?(\d{2,4})[台回線]', text)
        if extension_match:
            result['extension_count'] = int(extension_match.group(1))

        # 年度抽出
        year_match = re.search(r'(20\d{2})年', text)
        if year_match:
            result['year'] = int(year_match.group(1))

        return result if result['vendor'] else None

    def extract_microsoft_info(self, text: str) -> Optional[Dict]:
        """
        Microsoft 365情報を抽出

        Returns:
            {
                'has_contract': True,
                'license_type': 'E3',
                'user_count': 500,
                'year': 2024
            }
        """
        result = {
            'has_contract': False,
            'license_type': None,
            'user_count': None,
            'year': None
        }

        # Microsoft 365契約確認
        for keyword in self.KEYWORDS['microsoft']:
            if keyword in text:
                result['has_contract'] = True
                break

        if not result['has_contract']:
            return None

        # ライセンス種類検出
        for license_type, patterns in self.VENDORS['microsoft_license'].items():
            for pattern in patterns:
                if pattern in text:
                    result['license_type'] = license_type
                    break
            if result['license_type']:
                break

        # ユーザー数抽出
        user_match = re.search(r'(\d{2,5})[名人ユーザー]', text)
        if user_match:
            result['user_count'] = int(user_match.group(1))

        return result

    def extract_web_meeting_tool(self, text: str) -> Optional[str]:
        """Web会議ツールを検出"""
        tools = ['Zoom', 'Teams', 'Webex', 'Google Meet']

        for tool in tools:
            if tool in text or tool.lower() in text.lower():
                return tool

        return None

    def close(self):
        self.client.close()


class ITInfrastructureUpdater:
    """IT基盤情報をデータベースに保存"""

    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER", "zoom_admin"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            dbname=os.getenv("POSTGRES_DB", "zoom_dx_db")
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

        # テーブル作成
        self.create_table()

    def create_table(self):
        """it_infrastructureテーブルを作成"""
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS it_infrastructure (
                city_code VARCHAR(6) PRIMARY KEY,
                pbx_vendor VARCHAR(100),
                pbx_model VARCHAR(200),
                pbx_extension_count INT,
                pbx_update_year INT,
                microsoft_365 BOOLEAN DEFAULT FALSE,
                microsoft_license VARCHAR(10),
                microsoft_user_count INT,
                web_meeting_tool VARCHAR(50),
                groupware VARCHAR(50),
                network_update_year INT,
                data_source TEXT,
                confidence VARCHAR(20),  -- high/medium/low
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        self.conn.commit()

    def update_pbx_info(self, city_code: str, pbx_info: Dict, source: str):
        """PBX情報を更新"""
        self.cur.execute("""
            INSERT INTO it_infrastructure
                (city_code, pbx_vendor, pbx_model, pbx_extension_count, pbx_update_year, data_source, confidence)
            VALUES (%s, %s, %s, %s, %s, %s, 'medium')
            ON CONFLICT (city_code) DO UPDATE SET
                pbx_vendor = EXCLUDED.pbx_vendor,
                pbx_model = EXCLUDED.pbx_model,
                pbx_extension_count = EXCLUDED.pbx_extension_count,
                pbx_update_year = EXCLUDED.pbx_update_year,
                data_source = EXCLUDED.data_source,
                updated_at = NOW();
        """, (
            city_code,
            pbx_info.get('vendor'),
            pbx_info.get('model'),
            pbx_info.get('extension_count'),
            pbx_info.get('year'),
            source
        ))

    def update_microsoft_info(self, city_code: str, ms_info: Dict, source: str):
        """Microsoft 365情報を更新"""
        self.cur.execute("""
            INSERT INTO it_infrastructure
                (city_code, microsoft_365, microsoft_license, microsoft_user_count, data_source, confidence)
            VALUES (%s, %s, %s, %s, %s, 'high')
            ON CONFLICT (city_code) DO UPDATE SET
                microsoft_365 = EXCLUDED.microsoft_365,
                microsoft_license = EXCLUDED.microsoft_license,
                microsoft_user_count = EXCLUDED.microsoft_user_count,
                data_source = EXCLUDED.data_source,
                updated_at = NOW();
        """, (
            city_code,
            ms_info.get('has_contract'),
            ms_info.get('license_type'),
            ms_info.get('user_count'),
            source
        ))

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()


def collect_bidding_info_sample():
    """
    サンプル実行: 福岡市のPBX/Microsoft情報を収集
    """
    print("=" * 80)
    print("IT Infrastructure Data Collection - Sample Run")
    print("=" * 80)
    print()

    scraper = BiddingInfoScraper()
    updater = ITInfrastructureUpdater()

    # サンプルテキスト（実際の入札情報から抽出を想定）
    sample_pbx_text = """
    福岡市庁舎電話交換機更新業務
    NEC製 UNIVERGE Aspire X 導入
    内線800台、令和5年度更新
    契約金額: 5,000万円
    """

    sample_ms_text = """
    福岡市 Microsoft 365導入・運用支援業務
    Microsoft 365 E3ライセンス
    対象ユーザー数: 8,000名
    令和4年度契約
    """

    try:
        # PBX情報抽出
        pbx_info = scraper.extract_pbx_info(sample_pbx_text)
        if pbx_info:
            print(f"✅ PBX情報検出:")
            print(f"   ベンダー: {pbx_info['vendor']}")
            print(f"   内線数: {pbx_info['extension_count']}")
            print(f"   更新年: {pbx_info['year']}")

            updater.update_pbx_info('401307', pbx_info, 'sample_bidding_doc')

        # Microsoft情報抽出
        ms_info = scraper.extract_microsoft_info(sample_ms_text)
        if ms_info:
            print(f"\n✅ Microsoft 365情報検出:")
            print(f"   契約: {ms_info['has_contract']}")
            print(f"   ライセンス: {ms_info['license_type']}")
            print(f"   ユーザー数: {ms_info['user_count']}")

            updater.update_microsoft_info('401307', ms_info, 'sample_bidding_doc')

        updater.commit()

        print("\n" + "=" * 80)
        print("✅ Sample data saved to it_infrastructure table")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        scraper.close()
        updater.close()


if __name__ == "__main__":
    collect_bidding_info_sample()
