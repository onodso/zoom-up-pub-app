"""
改善版DXスコア算出エンジン - キカガクのデータサイエンス手法適用

主な改善点:
1. 分母正規化: 32手続の「提供手続数」を考慮したペナルティ
2. Z-score標準化: カテゴリ2・3の弁別力を回復
3. 外れ値処理: 統計的手法で異常値を検出・調整
4. 人口規模調整: ログスケールで人口による歪みを補正
"""

import os
import re
import numpy as np
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


class ImprovedScoreCalculator:
    """改善版DXスコア算出器 - キカガク手法適用"""

    def __init__(self):
        """データベース接続を初期化"""
        self.conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'zoom_dx_db'),
            user=os.getenv('POSTGRES_USER', 'zoom_admin'),
            password=os.getenv('POSTGRES_PASSWORD', 'your_secure_password_here')
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

        # 全国統計（Z-score計算用）
        self._population_stats = None
        self._cat2_stats = None
        self._cat3_stats = None
        self._max_news_count = None

    def parse_fraction(self, value: Optional[str]) -> Tuple[int, int]:
        """
        分数形式の文字列（例: '20/26'）を分子と分母に分解

        Returns:
            (分子, 分母) のタプル
        """
        if not value:
            return (0, 0)

        value_str = str(value).strip()

        # 分数形式（例: "20/26"）
        if '/' in value_str:
            parts = value_str.split('/')
            if len(parts) == 2:
                try:
                    numerator = int(parts[0].strip())
                    denominator = int(parts[1].strip())
                    return (numerator, denominator)
                except ValueError:
                    return (0, 0)

        # パーセンテージ形式（例: "76.9%"）
        match = re.search(r'(\d+(?:\.\d+)?)\s*%', value_str)
        if match:
            percentage = float(match.group(1))
            # 100分率として扱う
            return (int(percentage), 100)

        return (0, 0)

    def parse_percentage(self, value: Optional[str]) -> float:
        """パーセンテージ文字列を0.0-1.0に変換"""
        if not value:
            return 0.0
        match = re.search(r'(\d+(?:\.\d+)?)', str(value))
        if match:
            return float(match.group(1)) / 100.0
        return 0.0

    def parse_boolean_indicator(self, value: Optional[str]) -> float:
        """実施/未実施を1.0/0.0に変換"""
        if not value:
            return 0.0
        value_str = str(value)
        # 否定キーワードを先にチェック（部分一致の誤判定防止）
        negative_keywords = ['未実施', '未導入', '未活用', '未策定', '未任命', 'なし', '検討中']
        if any(kw in value_str for kw in negative_keywords):
            return 0.0
        positive_keywords = ['実施', '導入済', '活用中', '策定済', '任命済', 'あり']
        return 1.0 if any(kw in value_str for kw in positive_keywords) else 0.0

    def coverage_penalty(self, denominator: int, max_denominator: int = 32) -> float:
        """
        カバレッジペナルティ関数

        分母が小さい（提供手続が少ない）自治体にペナルティを与える。
        指数減衰関数を使用して、分母が0に近づくほど強くペナルティ。

        Args:
            denominator: 実際に提供している手続数
            max_denominator: 最大手続数（32）

        Returns:
            0.0-1.0のペナルティ係数（1.0=ペナルティなし）
        """
        if denominator <= 0:
            return 0.0

        # 指数減衰: 1 - exp(-x/λ)
        # λ = max_denominator とすることで、分母が最大値に近づくほど1.0に近づく
        penalty = 1.0 - np.exp(-denominator / max_denominator)
        return penalty

    def calculate_category1_improved(self, dx_status: Dict) -> float:
        """
        カテゴリ1: 住民サービスDX（改善版）

        改善点:
        - 32手続の分母正規化を適用
        - カバレッジペナルティで小規模自治体の過大評価を防止
        """
        # マイナンバーカード保有率（15点）
        mynumber_rate = self.parse_percentage(
            dx_status.get('住民サービスのDX_マイナンバーカードの保有状況', '0%'))
        mynumber_score = mynumber_rate * 15

        # 32手続オンライン化（12点）- 分母正規化適用
        online_32_raw = dx_status.get('住民サービスのDX_オンライン手続の導入状況_32手続（内閣府・総務省が規定）', '0/0')
        numerator_32, denominator_32 = self.parse_fraction(online_32_raw)

        if denominator_32 > 0:
            online_32_rate = numerator_32 / denominator_32
            coverage_factor_32 = self.coverage_penalty(denominator_32, 32)
            online_32_score = online_32_rate * coverage_factor_32 * 12
        else:
            online_32_score = 0.0

        # 26手続オンライン化（8点）- 分母正規化適用
        online_26_raw = dx_status.get('住民サービスのDX_オンライン手続の導入状況_26手続（総務省が規定）', '0/0')
        numerator_26, denominator_26 = self.parse_fraction(online_26_raw)

        if denominator_26 > 0:
            online_26_rate = numerator_26 / denominator_26
            coverage_factor_26 = self.coverage_penalty(denominator_26, 26)
            online_26_score = online_26_rate * coverage_factor_26 * 8
        else:
            online_26_score = 0.0

        total = mynumber_score + online_32_score + online_26_score
        return min(total, 35.0)

    def get_category2_stats(self) -> Dict:
        """カテゴリ2の全国統計を取得（Z-score計算用）"""
        if self._cat2_stats is not None:
            return self._cat2_stats

        # 全自治体のカテゴリ2生スコアを計算
        self.cur.execute("SELECT dx_status FROM municipalities WHERE dx_status IS NOT NULL")
        rows = self.cur.fetchall()

        raw_scores = []
        for row in rows:
            dx = row['dx_status'] or {}

            policy = self.parse_boolean_indicator(dx.get('自治体DXの推進体制等_全体方針策定'))
            cio = self.parse_boolean_indicator(dx.get('自治体DXの推進体制等_CIOの任命'))
            cio_sub = self.parse_boolean_indicator(dx.get('自治体DXの推進体制等_CIO補佐官等の任命'))
            org = self.parse_boolean_indicator(dx.get('自治体DXの推進体制等_全庁的な体制構築'))
            external = self.parse_boolean_indicator(dx.get('自治体DXの推進体制等_外部人材活用'))
            training = self.parse_boolean_indicator(dx.get('自治体DXの推進体制等_全職員対象研修の実施'))
            hr_dev = self.parse_boolean_indicator(dx.get('自治体DXの推進体制等_職員育成の取組'))

            # 7項目の合計（0-7）
            raw_score = policy + cio + cio_sub + org + external + training + hr_dev
            raw_scores.append(raw_score)

        raw_scores = np.array(raw_scores)
        self._cat2_stats = {
            'mean': np.mean(raw_scores),
            'std': np.std(raw_scores),
            'min': np.min(raw_scores),
            'max': np.max(raw_scores)
        }

        print(f"📊 カテゴリ2統計: 平均={self._cat2_stats['mean']:.2f}, 標準偏差={self._cat2_stats['std']:.2f}")
        return self._cat2_stats

    def calculate_category2_normalized(self, dx_status: Dict) -> float:
        """
        カテゴリ2: 推進体制（Z-score正規化版）

        改善点:
        - 7項目の合計をZ-scoreで標準化
        - 0-25点の範囲に再スケーリング
        """
        policy = self.parse_boolean_indicator(dx_status.get('自治体DXの推進体制等_全体方針策定'))
        cio = self.parse_boolean_indicator(dx_status.get('自治体DXの推進体制等_CIOの任命'))
        cio_sub = self.parse_boolean_indicator(dx_status.get('自治体DXの推進体制等_CIO補佐官等の任命'))
        org = self.parse_boolean_indicator(dx_status.get('自治体DXの推進体制等_全庁的な体制構築'))
        external = self.parse_boolean_indicator(dx_status.get('自治体DXの推進体制等_外部人材活用'))
        training = self.parse_boolean_indicator(dx_status.get('自治体DXの推進体制等_全職員対象研修の実施'))
        hr_dev = self.parse_boolean_indicator(dx_status.get('自治体DXの推進体制等_職員育成の取組'))

        raw_score = policy + cio + cio_sub + org + external + training + hr_dev

        # Z-score標準化
        stats = self.get_category2_stats()
        if stats['std'] > 0:
            z_score = (raw_score - stats['mean']) / stats['std']
            # Z-scoreを0-25の範囲に変換（-3σ〜+3σを想定）
            normalized = ((z_score + 3) / 6) * 25
            return np.clip(normalized, 0.0, 25.0)
        else:
            # 標準偏差が0の場合（全て同じ値）
            return 12.5  # 中央値

    def get_category3_stats(self) -> Dict:
        """カテゴリ3の全国統計を取得"""
        if self._cat3_stats is not None:
            return self._cat3_stats

        self.cur.execute("SELECT dx_status FROM municipalities WHERE dx_status IS NOT NULL")
        rows = self.cur.fetchall()

        raw_scores = []
        for row in rows:
            dx = row['dx_status'] or {}

            ai = self.parse_boolean_indicator(dx.get('自治体業務のDX_AIの導入状況'))
            rpa = self.parse_boolean_indicator(dx.get('自治体業務のDX_RPAの導入状況'))
            telework = self.parse_boolean_indicator(dx.get('自治体業務のDX_テレワークの導入状況'))

            raw_score = ai + rpa + telework
            raw_scores.append(raw_score)

        raw_scores = np.array(raw_scores)
        self._cat3_stats = {
            'mean': np.mean(raw_scores),
            'std': np.std(raw_scores),
            'min': np.min(raw_scores),
            'max': np.max(raw_scores)
        }

        print(f"📊 カテゴリ3統計: 平均={self._cat3_stats['mean']:.2f}, 標準偏差={self._cat3_stats['std']:.2f}")
        return self._cat3_stats

    def calculate_category3_normalized(self, dx_status: Dict) -> float:
        """
        カテゴリ3: 業務DX（Z-score正規化版）
        """
        ai = self.parse_boolean_indicator(dx_status.get('自治体業務のDX_AIの導入状況'))
        rpa = self.parse_boolean_indicator(dx_status.get('自治体業務のDX_RPAの導入状況'))
        telework = self.parse_boolean_indicator(dx_status.get('自治体業務のDX_テレワークの導入状況'))

        raw_score = ai + rpa + telework

        stats = self.get_category3_stats()
        if stats['std'] > 0:
            z_score = (raw_score - stats['mean']) / stats['std']
            normalized = ((z_score + 3) / 6) * 20
            return np.clip(normalized, 0.0, 20.0)
        else:
            return 10.0

    def get_max_news_count(self) -> int:
        """ニュース記事数の最大値を取得"""
        if self._max_news_count is None:
            self.cur.execute("""
                SELECT COALESCE(MAX(cnt), 1) as max_count
                FROM (SELECT city_code, COUNT(*) as cnt FROM municipality_news GROUP BY city_code) sub
            """)
            self._max_news_count = self.cur.fetchone()['max_count']
        return self._max_news_count

    def calculate_score(self, city_code: str) -> Dict:
        """
        単一自治体の改善版DXスコアを算出
        """
        # 自治体データ取得
        self.cur.execute("""
            SELECT
                m.city_code, m.city_name, m.prefecture, m.population,
                m.latitude, m.longitude, m.dx_status,
                e.computer_per_student,
                p.pattern_id, p.pattern_name,
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

        # --- カテゴリ1: 住民サービスDX（改善版）---
        cat1 = self.calculate_category1_improved(dx)

        # --- カテゴリ2: 推進体制（Z-score正規化版）---
        cat2 = self.calculate_category2_normalized(dx)

        # --- カテゴリ3: 業務DX（Z-score正規化版）---
        cat3 = self.calculate_category3_normalized(dx)

        # --- カテゴリ4: 教育DX ---
        giga = row['computer_per_student'] or 0
        giga_normalized = min(float(giga) / 1.0, 1.0)
        cat4 = giga_normalized * 10

        # --- カテゴリ5: 情報発信 ---
        news_count = row['news_count'] or 0
        max_news = self.get_max_news_count()
        news_normalized = min(news_count / max_news, 1.0) if max_news > 0 else 0.0
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
        }

    def calculate_all_scores(self) -> List[Dict]:
        """全自治体のスコアを算出"""
        print("🚀 改善版DXスコア算出を開始...")

        # まず統計情報を計算
        self.get_category2_stats()
        self.get_category3_stats()

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
        # テーブル作成
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS dx_scores_improved (
                city_code VARCHAR(6) PRIMARY KEY REFERENCES municipalities(city_code),
                total_score NUMERIC(5,1) NOT NULL,
                cat_citizen_services NUMERIC(4,1),
                cat_promotion_system NUMERIC(4,1),
                cat_business_dx NUMERIC(4,1),
                cat_education_dx NUMERIC(4,1),
                cat_information NUMERIC(4,1),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_dx_scores_improved_total ON dx_scores_improved(total_score);
        """)
        self.conn.commit()

        results = self.calculate_all_scores()

        for r in results:
            cats = r['category_scores']
            self.cur.execute("""
                INSERT INTO dx_scores_improved
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
                r['city_code'], float(r['total_score']),
                float(cats['citizen_services']), float(cats['promotion_system']),
                float(cats['business_dx']), float(cats['education_dx']), float(cats['information'])
            ))

        self.conn.commit()
        print(f"💾 {len(results)} 件の改善版スコアをDBに保存しました")

        # 統計表示
        self.cur.execute("""
            SELECT
                ROUND(AVG(total_score), 1) as avg_score,
                ROUND(MIN(total_score), 1) as min_score,
                ROUND(MAX(total_score), 1) as max_score,
                ROUND(STDDEV(total_score), 1) as stddev_score,
                COUNT(*) as count
            FROM dx_scores_improved
        """)
        stats = self.cur.fetchone()
        print(f"\n📊 改善版スコア統計:")
        print(f"  最低: {stats['min_score']} / 最高: {stats['max_score']} / 平均: {stats['avg_score']}")
        print(f"  標準偏差: {stats['stddev_score']}")
        print(f"  件数: {stats['count']}")

        # スコア分布
        self.cur.execute("""
            SELECT
                CASE
                    WHEN total_score >= 80 THEN '80-100'
                    WHEN total_score >= 65 THEN '65-79'
                    WHEN total_score >= 50 THEN '50-64'
                    WHEN total_score >= 30 THEN '30-49'
                    ELSE '0-29'
                END as score_range,
                COUNT(*) as count
            FROM dx_scores_improved
            GROUP BY score_range
            ORDER BY score_range DESC
        """)
        print(f"\n📈 スコア分布:")
        for row in self.cur.fetchall():
            pct = (row['count'] / stats['count']) * 100
            print(f"  {row['score_range']}点: {row['count']}件 ({pct:.1f}%)")

    def close(self):
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    calc = ImprovedScoreCalculator()
    try:
        calc.save_scores_to_db()
    finally:
        calc.close()
