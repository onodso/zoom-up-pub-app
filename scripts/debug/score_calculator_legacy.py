"""
総合DXスコア算出エンジン

自治体のDXデータ（15指標）、GIGAスクールデータ、ニュース記事数を
総合的に評価し、0-100の総合DXスコアを算出します。

スコア算出式:
  カテゴリ1: 住民サービスDX (35%)
  カテゴリ2: 推進体制 (25%)
  カテゴリ3: 業務DX (20%)
  カテゴリ4: 教育DX (10%)
  カテゴリ5: 情報発信 (10%)
"""

import os
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, List, Tuple


# 8地方区分の定義
REGIONS = {
    '北海道': '北海道地方',
    '青森県': '東北地方', '岩手県': '東北地方', '宮城県': '東北地方',
    '秋田県': '東北地方', '山形県': '東北地方', '福島県': '東北地方',
    '茨城県': '関東地方', '栃木県': '関東地方', '群馬県': '関東地方',
    '埼玉県': '関東地方', '千葉県': '関東地方', '東京都': '関東地方',
    '神奈川県': '関東地方',
    '新潟県': '中部地方', '富山県': '中部地方', '石川県': '中部地方',
    '福井県': '中部地方', '山梨県': '中部地方', '長野県': '中部地方',
    '岐阜県': '中部地方', '静岡県': '中部地方', '愛知県': '中部地方',
    '三重県': '近畿地方', '滋賀県': '近畿地方', '京都府': '近畿地方',
    '大阪府': '近畿地方', '兵庫県': '近畿地方', '奈良県': '近畿地方',
    '和歌山県': '近畿地方',
    '鳥取県': '中国地方', '島根県': '中国地方', '岡山県': '中国地方',
    '広島県': '中国地方', '山口県': '中国地方',
    '徳島県': '四国地方', '香川県': '四国地方', '愛媛県': '四国地方',
    '高知県': '四国地方',
    '福岡県': '九州・沖縄地方', '佐賀県': '九州・沖縄地方',
    '長崎県': '九州・沖縄地方', '熊本県': '九州・沖縄地方',
    '大分県': '九州・沖縄地方', '宮崎県': '九州・沖縄地方',
    '鹿児島県': '九州・沖縄地方', '沖縄県': '九州・沖縄地方',
}


class ScoreCalculator:
    """総合DXスコア算出器"""

    def __init__(self):
        """データベース接続を初期化"""
        self.conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'zoom_dx_db'),
            user=os.getenv('POSTGRES_USER', 'zoom_admin'),
            password=os.getenv('POSTGRES_PASSWORD', 'zoom_pass')
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        # ニュース記事数の最大値（正規化用）
        self._max_news_count = None

    def parse_percentage(self, value: Optional[str]) -> float:
        """パーセンテージ文字列を0.0-1.0に変換"""
        if not value:
            return 0.0
        match = re.search(r'(\d+)', str(value))
        if match:
            return float(match.group(1)) / 100.0
        return 0.0

    def parse_boolean_indicator(self, value: Optional[str]) -> float:
        """実施/未実施を1.0/0.0に変換（導入済み/活用中なども対応）"""
        if not value:
            return 0.0
        positive_keywords = ['実施', '導入済', '活用中', '策定済', '任命済', 'あり']
        return 1.0 if any(kw in str(value) for kw in positive_keywords) else 0.0

    def get_max_news_count(self) -> int:
        """ニュース記事数の最大値を取得（キャッシュ付き）"""
        if self._max_news_count is None:
            self.cur.execute("""
                SELECT COALESCE(MAX(cnt), 1) as max_count
                FROM (SELECT city_code, COUNT(*) as cnt FROM municipality_news GROUP BY city_code) sub
            """)
            self._max_news_count = self.cur.fetchone()['max_count']
        return self._max_news_count

    def calculate_score(self, city_code: str) -> Dict:
        """
        単一自治体の総合DXスコアを算出

        Returns:
            {
                'total_score': float (0-100),
                'category_scores': { カテゴリ名: スコア },
                'indicators': { 指標名: 値 }
            }
        """
        # 自治体データ取得
        self.cur.execute("""
            SELECT
                m.city_code, m.city_name, m.prefecture, m.population,
                m.latitude, m.longitude, m.dx_status,
                e.computer_per_student,
                p.pattern_id, p.pattern_name, p.mynumber_rate, p.online_proc_rate,
                (SELECT COUNT(*) FROM municipality_news n WHERE n.city_code = m.city_code) as news_count
            FROM municipalities m
            LEFT JOIN education_info e ON m.city_code = e.city_code
            LEFT JOIN municipality_patterns p ON m.city_code = p.city_code
            WHERE m.city_code = %s
        """, (city_code,))

        row = self.cur.fetchone()
        if not row:
            return None

        dx = row['dx_status'] or {}

        # --- カテゴリ1: 住民サービスDX (35%) ---
        mynumber = self.parse_percentage(
            dx.get('住民サービスのDX_マイナンバーカードの保有状況', '0%'))
        online_32 = self.parse_percentage(
            dx.get('住民サービスのDX_よく使う32手続のオンライン化状況', '0%'))
        online_26 = self.parse_percentage(
            dx.get('住民サービスのDX_子育て・介護26手続のオンライン化状況', '0%'))

        cat1 = (mynumber * 15 + online_32 * 12 + online_26 * 8)

        # --- カテゴリ2: 推進体制 (25%) ---
        policy = self.parse_boolean_indicator(
            dx.get('自治体DXの推進体制等_全体方針策定'))
        cio = self.parse_boolean_indicator(
            dx.get('自治体DXの推進体制等_CIOの任命'))
        cio_sub = self.parse_boolean_indicator(
            dx.get('自治体DXの推進体制等_CIO補佐官等の任命'))
        org = self.parse_boolean_indicator(
            dx.get('自治体DXの推進体制等_全庁的な体制構築'))
        external = self.parse_boolean_indicator(
            dx.get('自治体DXの推進体制等_外部人材活用'))
        training = self.parse_boolean_indicator(
            dx.get('自治体DXの推進体制等_全職員対象研修の実施'))
        hr_dev = self.parse_boolean_indicator(
            dx.get('自治体DXの推進体制等_職員育成の取組'))

        cat2 = (policy * 6 + cio * 5 + cio_sub * 4 + org * 4
                + external * 3 + training * 1.5 + hr_dev * 1.5)

        # --- カテゴリ3: 業務DX (20%) ---
        ai = self.parse_boolean_indicator(
            dx.get('自治体業務のDX_AIの導入状況'))
        rpa = self.parse_boolean_indicator(
            dx.get('自治体業務のDX_RPAの導入状況'))
        telework = self.parse_boolean_indicator(
            dx.get('自治体業務のDX_テレワークの導入状況'))

        cat3 = (ai * 8 + rpa * 6 + telework * 6)

        # --- カテゴリ4: 教育DX (10%) ---
        giga = row['computer_per_student'] or 0
        # GIGA端末整備率を0-10に正規化（1.0台/人 = 満点）
        giga_normalized = min(float(giga) / 1.0, 1.0)
        cat4 = giga_normalized * 10

        # --- カテゴリ5: 情報発信 (10%) ---
        news_count = row['news_count'] or 0
        max_news = self.get_max_news_count()
        news_normalized = min(news_count / max_news, 1.0)
        cat5 = news_normalized * 10

        # --- 総合スコア ---
        total = cat1 + cat2 + cat3 + cat4 + cat5
        total = min(round(total, 1), 100.0)

        return {
            'city_code': row['city_code'],
            'city_name': row['city_name'],
            'prefecture': row['prefecture'],
            'region': REGIONS.get(row['prefecture'], '不明'),
            'population': row['population'],
            'latitude': float(row['latitude']) if row['latitude'] else None,
            'longitude': float(row['longitude']) if row['longitude'] else None,
            'total_score': total,
            'category_scores': {
                'citizen_services': round(cat1, 1),
                'promotion_system': round(cat2, 1),
                'business_dx': round(cat3, 1),
                'education_dx': round(cat4, 1),
                'information': round(cat5, 1),
            },
            'pattern_id': row['pattern_id'],
            'pattern_name': row['pattern_name'],
            'giga_rate': float(giga) if giga else None,
            'news_count': news_count,
            'indicators': {
                'mynumber_rate': mynumber,
                'online_32_rate': online_32,
                'online_26_rate': online_26,
                'policy': policy,
                'cio': cio,
                'cio_sub': cio_sub,
                'org_structure': org,
                'external_talent': external,
                'training': training,
                'hr_development': hr_dev,
                'ai_adoption': ai,
                'rpa_adoption': rpa,
                'telework': telework,
            }
        }

    def calculate_all_scores(self) -> List[Dict]:
        """全自治体のスコアを算出"""
        print("🚀 全自治体の総合DXスコア算出を開始...")

        self.cur.execute("SELECT city_code FROM municipalities ORDER BY city_code")
        city_codes = [r['city_code'] for r in self.cur.fetchall()]

        results = []
        for i, code in enumerate(city_codes, 1):
            result = self.calculate_score(code)
            if result:
                results.append(result)
            if i % 200 == 0:
                print(f"  進捗: {i}/{len(city_codes)} ({i*100//len(city_codes)}%)")

        print(f"✅ 完了: {len(results)} 自治体のスコア算出")
        return results

    def save_scores_to_db(self):
        """全自治体のスコアをDBに保存"""
        # dx_scoresテーブルがなければ作成
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS dx_scores (
                city_code VARCHAR(6) PRIMARY KEY REFERENCES municipalities(city_code),
                total_score NUMERIC(5,1) NOT NULL,
                cat_citizen_services NUMERIC(4,1),
                cat_promotion_system NUMERIC(4,1),
                cat_business_dx NUMERIC(4,1),
                cat_education_dx NUMERIC(4,1),
                cat_information NUMERIC(4,1),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_dx_scores_total ON dx_scores(total_score);
        """)
        self.conn.commit()

        results = self.calculate_all_scores()

        for r in results:
            cats = r['category_scores']
            self.cur.execute("""
                INSERT INTO dx_scores
                (city_code, total_score, cat_citizen_services, cat_promotion_system,
                 cat_business_dx, cat_education_dx, cat_information, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (city_code) DO UPDATE SET
                    total_score = EXCLUDED.total_score,
                    cat_citizen_services = EXCLUDED.cat_citizen_services,
                    cat_promotion_system = EXCLUDED.cat_promotion_system,
                    cat_business_dx = EXCLUDED.cat_business_dx,
                    cat_education_dx = EXCLUDED.cat_education_dx,
                    cat_information = EXCLUDED.cat_information,
                    updated_at = NOW();
            """, (
                r['city_code'], r['total_score'],
                cats['citizen_services'], cats['promotion_system'],
                cats['business_dx'], cats['education_dx'], cats['information']
            ))

        self.conn.commit()
        print(f"💾 {len(results)} 件のスコアをDBに保存しました")

        # 統計表示
        self.cur.execute("""
            SELECT
                ROUND(AVG(total_score), 1) as avg_score,
                ROUND(MIN(total_score), 1) as min_score,
                ROUND(MAX(total_score), 1) as max_score,
                COUNT(*) as count
            FROM dx_scores
        """)
        stats = self.cur.fetchone()
        print(f"\n📊 スコア統計:")
        print(f"  最低: {stats['min_score']} / 最高: {stats['max_score']} / 平均: {stats['avg_score']}")
        print(f"  件数: {stats['count']}")

    def close(self):
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    calc = ScoreCalculator()
    try:
        calc.save_scores_to_db()
    finally:
        calc.close()
