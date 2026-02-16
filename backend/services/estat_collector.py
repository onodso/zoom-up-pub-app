"""
e-Stat API Integration for Municipality Data Collection
総務省統計LOD（e-Stat）から自治体データを取得

取得データ:
1. 人口・世帯数（実データ）
2. 職員数（正規・非正規）
3. 財政力指数
4. 高齢化率
5. 人口減少率
"""

import httpx
import os
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import time

class EStatCollector:
    """e-Stat API Data Collector"""

    def __init__(self, app_id: str = None):
        self.app_id = app_id or os.getenv("ESTAT_APP_ID")
        if not self.app_id:
            raise ValueError("ESTAT_APP_ID is required")

        self.base_url = "https://api.e-stat.go.jp/rest/3.0/app/json"
        self.client = httpx.Client(timeout=30.0)

    def get_stats_list(self, survey_code: str = None) -> Dict:
        """統計リストを取得"""
        params = {
            "appId": self.app_id,
            "lang": "J",
            "surveyYears": "2020-2025"
        }
        if survey_code:
            params["surveyCode"] = survey_code

        response = self.client.get(f"{self.base_url}/getStatsList", params=params)
        response.raise_for_status()
        return response.json()

    def get_population_data(self, city_code: str) -> Optional[Dict]:
        """
        人口データを取得
        統計表ID: 0003448237 (令和2年国勢調査)
        """
        try:
            params = {
                "appId": self.app_id,
                "lang": "J",
                "statsDataId": "0003448237",  # 国勢調査（人口・世帯）
                "cdArea": city_code,  # 市区町村コード
            }

            response = self.client.get(f"{self.base_url}/getStatsData", params=params)

            if response.status_code != 200:
                print(f"⚠️  {city_code}: HTTP {response.status_code}")
                return None

            data = response.json()

            # データ解析
            result = {
                "population": None,
                "households": None,
                "elderly_ratio": None,
            }

            # TODO: e-StatレスポンスのJSONパース実装
            # （実際のデータ構造に応じて調整）

            return result

        except Exception as e:
            print(f"❌ Error fetching {city_code}: {e}")
            return None

    def get_staff_count(self, city_code: str) -> Optional[int]:
        """
        職員数を取得
        統計表ID: 地方公務員給与実態調査
        """
        try:
            # TODO: 職員数データの取得実装
            return None
        except Exception as e:
            print(f"❌ Error fetching staff for {city_code}: {e}")
            return None

    def close(self):
        """クライアントを閉じる"""
        self.client.close()


class EStatDataUpdater:
    """データベース更新処理"""

    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER", "zoom_admin"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            dbname=os.getenv("POSTGRES_DB", "zoom_dx_db")
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

    def get_all_municipalities(self) -> List[Dict]:
        """全自治体を取得"""
        self.cur.execute("""
            SELECT city_code, city_name, prefecture
            FROM municipalities
            ORDER BY city_code;
        """)
        return self.cur.fetchall()

    def update_population(self, city_code: str, population: int, households: int):
        """人口データを更新"""
        self.cur.execute("""
            UPDATE municipalities
            SET population = %s,
                households = %s,
                updated_at = NOW()
            WHERE city_code = %s;
        """, (population, households, city_code))

    def update_elderly_ratio(self, city_code: str, ratio: float):
        """高齢化率を更新"""
        self.cur.execute("""
            UPDATE municipalities
            SET elderly_ratio = %s,
                updated_at = NOW()
            WHERE city_code = %s;
        """, (ratio, city_code))

    def commit(self):
        """コミット"""
        self.conn.commit()

    def close(self):
        """接続を閉じる"""
        self.cur.close()
        self.conn.close()


def collect_estat_data_batch(limit: int = 100):
    """
    e-Statデータを一括取得

    Args:
        limit: 取得する自治体数（デフォルト100）
    """
    print("=" * 80)
    print("e-Stat API Data Collection - Batch Update")
    print("=" * 80)

    collector = EStatCollector()
    updater = EStatDataUpdater()

    try:
        municipalities = updater.get_all_municipalities()[:limit]

        print(f"\n📊 Processing {len(municipalities)} municipalities...")
        print()

        success_count = 0
        fail_count = 0

        for idx, muni in enumerate(municipalities, 1):
            city_code = muni['city_code']
            city_name = muni['city_name']

            print(f"[{idx}/{len(municipalities)}] {city_name} ({city_code})...", end=" ")

            # 人口データ取得
            pop_data = collector.get_population_data(city_code)

            if pop_data and pop_data.get('population'):
                updater.update_population(
                    city_code,
                    pop_data['population'],
                    pop_data['households']
                )

                if pop_data.get('elderly_ratio'):
                    updater.update_elderly_ratio(
                        city_code,
                        pop_data['elderly_ratio']
                    )

                print(f"✅ Pop: {pop_data['population']:,}")
                success_count += 1
            else:
                print("⚠️  No data")
                fail_count += 1

            # Rate limiting (e-Stat APIは1秒間に10リクエストまで)
            time.sleep(0.15)

            # 100件ごとにコミット
            if idx % 100 == 0:
                updater.commit()
                print(f"\n💾 Committed {idx} records\n")

        # 最終コミット
        updater.commit()

        print()
        print("=" * 80)
        print(f"✅ Success: {success_count}")
        print(f"⚠️  Failed:  {fail_count}")
        print(f"📊 Total:   {len(municipalities)}")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        collector.close()
        updater.close()


if __name__ == "__main__":
    # Test with 10 municipalities first
    collect_estat_data_batch(limit=10)
