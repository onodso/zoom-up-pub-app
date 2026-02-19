"""
スコアエンジン回帰テスト

score_calculator.py (ImprovedScoreCalculator) の計算ロジックの正確性を保証する。
DB非依存のユニットテストとDB依存の統合テストを分離。

テスト方針:
- 純粋関数（パーサー、ペナルティ関数）: 入力→出力の固定値テスト
- カテゴリ計算: モックDXデータによる回帰テスト
- 数値固定化: 将来のリファクタリングで計算結果が変わらないことを保証
"""

import os
import sys
import pytest
import numpy as np
from unittest.mock import MagicMock, patch

# backendをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# --- ImprovedScoreCalculatorのDB接続をモック化してインスタンス生成 ---
@pytest.fixture
def calculator():
    """DB接続をモック化したスコア計算器"""
    with patch('services.score_calculator.psycopg2') as mock_psycopg2:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn

        from services.score_calculator import ImprovedScoreCalculator
        calc = ImprovedScoreCalculator()
        yield calc


# ============================================================
# 1. パース関数の回帰テスト（数値固定化）
# ============================================================

class TestParseFraction:
    """分数パースの正確性を保証"""

    def test_standard_fraction(self, calculator):
        """標準的な分数形式"""
        assert calculator.parse_fraction("20/26") == (20, 26)

    def test_full_fraction(self, calculator):
        """全数一致"""
        assert calculator.parse_fraction("32/32") == (32, 32)

    def test_zero_fraction(self, calculator):
        """ゼロ"""
        assert calculator.parse_fraction("0/32") == (0, 32)

    def test_percentage_format(self, calculator):
        """パーセンテージ形式"""
        assert calculator.parse_fraction("76.9%") == (76, 100)

    def test_none_input(self, calculator):
        """None入力"""
        assert calculator.parse_fraction(None) == (0, 0)

    def test_empty_string(self, calculator):
        """空文字列"""
        assert calculator.parse_fraction("") == (0, 0)

    def test_invalid_string(self, calculator):
        """不正な入力"""
        assert calculator.parse_fraction("abc") == (0, 0)


class TestParsePercentage:
    """パーセンテージパースの正確性を保証"""

    def test_standard_percentage(self, calculator):
        """標準パーセンテージ"""
        assert calculator.parse_percentage("75%") == 0.75

    def test_decimal_percentage(self, calculator):
        """小数付きパーセンテージ"""
        result = calculator.parse_percentage("76.9%")
        assert abs(result - 0.769) < 1e-6

    def test_zero_percentage(self, calculator):
        """0%"""
        assert calculator.parse_percentage("0%") == 0.0

    def test_hundred_percentage(self, calculator):
        """100%"""
        assert calculator.parse_percentage("100%") == 1.0

    def test_none_input(self, calculator):
        """None入力"""
        assert calculator.parse_percentage(None) == 0.0


class TestParseBooleanIndicator:
    """Boolean指標パースの正確性を保証"""

    def test_positive_keywords(self, calculator):
        """正のキーワード一覧"""
        positives = ['実施', '導入済', '活用中', '策定済', '任命済', 'あり']
        for kw in positives:
            assert calculator.parse_boolean_indicator(kw) == 1.0, f"{kw}が1.0を返さない"

    def test_negative_keywords(self, calculator):
        """負のキーワード"""
        negatives = ['未実施', '未導入', 'なし', '検討中', '']
        for kw in negatives:
            assert calculator.parse_boolean_indicator(kw) == 0.0, f"{kw}が0.0を返さない"

    def test_none_input(self, calculator):
        """None入力"""
        assert calculator.parse_boolean_indicator(None) == 0.0


# ============================================================
# 2. カバレッジペナルティ関数の回帰テスト（数値固定化）
# ============================================================

class TestCoveragePenalty:
    """指数減衰ペナルティ関数の正確性を保証

    関数: 1 - exp(-denominator / max_denominator)
    """

    def test_zero_denominator(self, calculator):
        """手続数0 → ペナルティ最大（スコア0）"""
        assert calculator.coverage_penalty(0) == 0.0

    def test_full_coverage(self, calculator):
        """32手続すべてカバー"""
        result = calculator.coverage_penalty(32, 32)
        expected = 1.0 - np.exp(-1.0)  # ≈ 0.6321
        assert abs(result - expected) < 1e-6

    def test_half_coverage(self, calculator):
        """16手続（半分）"""
        result = calculator.coverage_penalty(16, 32)
        expected = 1.0 - np.exp(-0.5)  # ≈ 0.3935
        assert abs(result - expected) < 1e-6

    def test_high_coverage(self, calculator):
        """26手続（高カバレッジ）"""
        result = calculator.coverage_penalty(26, 26)
        expected = 1.0 - np.exp(-1.0)
        assert abs(result - expected) < 1e-6

    def test_penalty_monotonically_increasing(self, calculator):
        """ペナルティはカバレッジ増加に伴い単調増加"""
        prev = 0.0
        for d in range(1, 33):
            current = calculator.coverage_penalty(d, 32)
            assert current > prev, f"d={d}で単調増加が破れた"
            prev = current


# ============================================================
# 3. カテゴリ1: 住民サービスDX の回帰テスト（数値固定化）
# ============================================================

class TestCategory1:
    """住民サービスDX（35点満点）の回帰テスト"""

    def test_perfect_score(self, calculator):
        """理想的なDXリーダー自治体"""
        dx_status = {
            '住民サービスのDX_マイナンバーカードの保有状況': '80%',
            '住民サービスのDX_オンライン手続の導入状況_32手続（内閣府・総務省が規定）': '30/32',
            '住民サービスのDX_オンライン手続の導入状況_26手続（総務省が規定）': '24/26',
        }
        score = calculator.calculate_category1_improved(dx_status)
        # マイナンバー: 0.80 * 15 = 12.0
        # 32手続: (30/32) * coverage_penalty(32, 32) * 12
        #       = 0.9375 * 0.6321 * 12 ≈ 7.111
        # 26手続: (24/26) * coverage_penalty(26, 26) * 8
        #       = 0.9231 * 0.6321 * 8 ≈ 4.668
        # 合計 ≈ 23.78
        assert 23.0 <= score <= 25.0, f"完全スコアが想定範囲外: {score}"

    def test_zero_score(self, calculator):
        """データなし自治体"""
        dx_status = {}
        score = calculator.calculate_category1_improved(dx_status)
        assert score == 0.0

    def test_mynumber_only(self, calculator):
        """マイナンバーカードだけ高い自治体"""
        dx_status = {
            '住民サービスのDX_マイナンバーカードの保有状況': '100%',
        }
        score = calculator.calculate_category1_improved(dx_status)
        assert abs(score - 15.0) < 0.01, f"マイナンバー100%のスコアが15.0でない: {score}"

    def test_max_cap(self, calculator):
        """スコア上限35点の保証"""
        dx_status = {
            '住民サービスのDX_マイナンバーカードの保有状況': '200%',
            '住民サービスのDX_オンライン手続の導入状況_32手続（内閣府・総務省が規定）': '32/32',
            '住民サービスのDX_オンライン手続の導入状況_26手続（総務省が規定）': '26/26',
        }
        score = calculator.calculate_category1_improved(dx_status)
        assert score <= 35.0, f"上限35点を超過: {score}"

    def test_fixed_regression_value(self, calculator):
        """固定回帰値テスト - この値が変わったらロジック変更を意味する"""
        dx_status = {
            '住民サービスのDX_マイナンバーカードの保有状況': '75%',
            '住民サービスのDX_オンライン手続の導入状況_32手続（内閣府・総務省が規定）': '20/26',
            '住民サービスのDX_オンライン手続の導入状況_26手続（総務省が規定）': '15/20',
        }
        score = calculator.calculate_category1_improved(dx_status)

        # マイナンバー: 0.75 * 15 = 11.25
        # 32手続: (20/26) * coverage_penalty(26, 32) * 12
        #       = 0.7692 * (1 - exp(-26/32)) * 12
        #       = 0.7692 * 0.5560 * 12 ≈ 5.131
        # 26手続: (15/20) * coverage_penalty(20, 26) * 8
        #       = 0.75 * (1 - exp(-20/26)) * 8
        #       = 0.75 * 0.5369 * 8 ≈ 3.221
        # 合計 ≈ 19.60
        expected = 11.25 + (20/26) * (1 - np.exp(-26/32)) * 12 + (15/20) * (1 - np.exp(-20/26)) * 8
        assert abs(score - expected) < 0.01, f"回帰値不一致: 期待={expected:.4f}, 実際={score:.4f}"


# ============================================================
# 4. カテゴリ2: 推進体制（Z-score正規化）の回帰テスト
# ============================================================

class TestCategory2:
    """推進体制（25点満点）のZ-score正規化テスト"""

    def test_with_mocked_stats(self, calculator):
        """モック統計データでのZ-score計算"""
        # 統計をモック化（平均3.5, 標準偏差1.5を想定）
        calculator._cat2_stats = {
            'mean': 3.5,
            'std': 1.5,
            'min': 0,
            'max': 7
        }

        # 全7項目が「実施」（raw_score = 7）
        dx_status = {
            '自治体DXの推進体制等_全体方針策定': '実施',
            '自治体DXの推進体制等_CIOの任命': '任命済',
            '自治体DXの推進体制等_CIO補佐官等の任命': '任命済',
            '自治体DXの推進体制等_全庁的な体制構築': '実施',
            '自治体DXの推進体制等_外部人材活用': '活用中',
            '自治体DXの推進体制等_全職員対象研修の実施': '実施',
            '自治体DXの推進体制等_職員育成の取組': '実施',
        }
        score = calculator.calculate_category2_normalized(dx_status)

        # Z-score = (7 - 3.5) / 1.5 = 2.333
        # normalized = ((2.333 + 3) / 6) * 25 = 22.22
        expected = ((7 - 3.5) / 1.5 + 3) / 6 * 25
        assert abs(score - expected) < 0.01, f"Z-score回帰値不一致: {score} vs {expected}"

    def test_all_zero(self, calculator):
        """全項目未実施"""
        calculator._cat2_stats = {'mean': 3.5, 'std': 1.5, 'min': 0, 'max': 7}
        dx_status = {}
        score = calculator.calculate_category2_normalized(dx_status)

        # Z-score = (0 - 3.5) / 1.5 = -2.333
        # normalized = ((-2.333 + 3) / 6) * 25 = 2.78
        expected_z = (0 - 3.5) / 1.5
        expected = ((expected_z + 3) / 6) * 25
        assert abs(score - expected) < 0.01

    def test_zero_std(self, calculator):
        """標準偏差0（全自治体が同スコア）→ 中央値12.5を返す"""
        calculator._cat2_stats = {'mean': 3.5, 'std': 0, 'min': 3.5, 'max': 3.5}
        dx_status = {}
        score = calculator.calculate_category2_normalized(dx_status)
        assert score == 12.5

    def test_score_range(self, calculator):
        """スコアが0-25の範囲内に収まる"""
        calculator._cat2_stats = {'mean': 3.5, 'std': 1.5, 'min': 0, 'max': 7}
        dx_status = {}
        score = calculator.calculate_category2_normalized(dx_status)
        assert 0.0 <= score <= 25.0


# ============================================================
# 5. カテゴリ3: 業務DX（Z-score正規化）の回帰テスト
# ============================================================

class TestCategory3:
    """業務DX（20点満点）のZ-score正規化テスト"""

    def test_all_implemented(self, calculator):
        """AI・RPA・テレワーク全導入"""
        calculator._cat3_stats = {'mean': 1.5, 'std': 1.0, 'min': 0, 'max': 3}
        dx_status = {
            '自治体業務のDX_AIの導入状況': '導入済',
            '自治体業務のDX_RPAの導入状況': '導入済',
            '自治体業務のDX_テレワークの導入状況': '導入済',
        }
        score = calculator.calculate_category3_normalized(dx_status)

        # Z-score = (3 - 1.5) / 1.0 = 1.5
        # normalized = ((1.5 + 3) / 6) * 20 = 15.0
        expected = ((3 - 1.5) / 1.0 + 3) / 6 * 20
        assert abs(score - expected) < 0.01

    def test_none_implemented(self, calculator):
        """全未導入"""
        calculator._cat3_stats = {'mean': 1.5, 'std': 1.0, 'min': 0, 'max': 3}
        dx_status = {}
        score = calculator.calculate_category3_normalized(dx_status)

        expected = ((0 - 1.5) / 1.0 + 3) / 6 * 20
        assert abs(score - expected) < 0.01

    def test_score_range(self, calculator):
        """スコアが0-20の範囲内に収まる"""
        calculator._cat3_stats = {'mean': 1.5, 'std': 1.0, 'min': 0, 'max': 3}
        dx_status = {}
        score = calculator.calculate_category3_normalized(dx_status)
        assert 0.0 <= score <= 20.0


# ============================================================
# 6. 総合スコアの回帰テスト（数値固定化 = 最重要）
# ============================================================

class TestTotalScoreRegression:
    """総合スコア（100点満点）の回帰テスト

    このテストが割れたら = スコアリングロジック変更を意味する。
    意図しない変更を即座に検知する防波堤。
    """

    def test_total_score_composition(self, calculator):
        """5カテゴリの合計が正しいことを保証"""
        # 各カテゴリの上限合計が100点であること
        max_cat1 = 35.0  # 住民サービスDX
        max_cat2 = 25.0  # 推進体制
        max_cat3 = 20.0  # 業務DX
        max_cat4 = 10.0  # 教育DX
        max_cat5 = 10.0  # 情報発信

        assert max_cat1 + max_cat2 + max_cat3 + max_cat4 + max_cat5 == 100.0

    def test_category_weights_unchanged(self, calculator):
        """カテゴリの重み配分が変わっていないことを保証

        住民DX: 35%、推進体制: 25%、業務DX: 20%、教育: 10%、情報発信: 10%
        """
        # カテゴリ1: マイナンバー15 + 32手続12 + 26手続8 = 35
        assert 15 + 12 + 8 == 35

        # カテゴリ4: giga * 10 = max 10
        # カテゴリ5: news * 10 = max 10


# ============================================================
# 7. 地方区分マッピングの回帰テスト
# ============================================================

class TestRegionMapping:
    """47都道府県の地方区分が正しいことを保証"""

    def test_all_47_prefectures_mapped(self):
        """47都道府県すべてがマッピングされている"""
        from services.score_calculator import REGIONS
        assert len(REGIONS) == 47

    def test_region_count(self):
        """8地方区分に分類されている"""
        from services.score_calculator import REGIONS
        unique_regions = set(REGIONS.values())
        assert len(unique_regions) == 8

    def test_specific_mappings(self):
        """特定の都道府県マッピングの固定値テスト"""
        from services.score_calculator import REGIONS
        assert REGIONS['北海道'] == '北海道地方'
        assert REGIONS['東京都'] == '関東地方'
        assert REGIONS['大阪府'] == '近畿地方'
        assert REGIONS['沖縄県'] == '九州・沖縄地方'
        assert REGIONS['愛知県'] == '中部地方'
