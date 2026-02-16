"""
Sales Pattern Matcher
自治体のIT基盤情報からZoom製品の最適な提案パターンを判定

7つのパターン:
1. ZP + AI Concierge (窓口DX)
2. ZP + AIC (働き方改革)
3. ZP + AIC + ZRA (カスハラ対策)
4. ZM + ZR + ZRA (教育DX)
5. All-in (完全DX)
6. ZM + AIC (会議効率化)
7. ZCC + ZP + ZVA (奈良市モデル)
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Dict, Optional


class SalesPatternMatcher:
    """セールスパターンマッチングエンジン"""

    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER", "zoom_admin"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            dbname=os.getenv("POSTGRES_DB", "zoom_dx_db")
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

    def get_municipality_data(self, city_code: str) -> Optional[Dict]:
        """自治体の全データを取得"""
        # 基本情報
        self.cur.execute("""
            SELECT m.*,
                   i.pbx_vendor,
                   i.pbx_extension_count,
                   i.microsoft_365,
                   i.microsoft_license,
                   i.web_meeting_tool
            FROM municipalities m
            LEFT JOIN it_infrastructure i ON m.city_code = i.city_code
            WHERE m.city_code = %s;
        """, (city_code,))

        return self.cur.fetchone()

    def determine_pattern(self, city_code: str) -> List[Dict]:
        """
        最適なセールスパターンを判定

        Returns:
            [
                {
                    'pattern': 'Pattern 2: ZP + AIC',
                    'priority': 'high',
                    'confidence': 0.85,
                    'reason': 'NEC PBX更新時期 + テレワーク推進中',
                    'products': ['Zoom Phone', 'AI Companion'],
                    'strategy': 'Blue Ocean - 電話インフラを握る'
                },
                ...
            ]
        """
        data = self.get_municipality_data(city_code)
        if not data:
            return []

        patterns = []

        # Pattern 2: ZP + AIC (働き方改革)
        pattern2_score = self._score_pattern2(data)
        if pattern2_score > 0.5:
            patterns.append({
                'pattern': 'Pattern 2: ZP + AIC (働き方改革)',
                'priority': 'high' if pattern2_score > 0.75 else 'medium',
                'confidence': pattern2_score,
                'reason': self._explain_pattern2(data),
                'products': ['Zoom Phone', 'AI Companion'],
                'strategy': self._get_microsoft_strategy(data),
                'use_cases': ['PBXリプレイス', '内線通話の自動要約', 'テレワーク推進']
            })

        # Pattern 1: ZP + AI Concierge (窓口DX)
        pattern1_score = self._score_pattern1(data)
        if pattern1_score > 0.4:
            patterns.append({
                'pattern': 'Pattern 1: ZP + AI Concierge (窓口DX)',
                'priority': 'medium',
                'confidence': pattern1_score,
                'reason': '窓口業務の効率化ニーズ推定',
                'products': ['Zoom Phone', 'AI Concierge'],
                'strategy': 'シンプル版コールセンター構築',
                'use_cases': ['電話自動対応', '意図ベースルーティング', '市民サービス向上']
            })

        # Pattern 6: ZM + AIC (会議効率化)
        pattern6_score = self._score_pattern6(data)
        if pattern6_score > 0.6:
            patterns.append({
                'pattern': 'Pattern 6: ZM + AIC (会議効率化)',
                'priority': 'medium',
                'confidence': pattern6_score,
                'reason': self._explain_pattern6(data),
                'products': ['Zoom Meetings', 'AI Companion'],
                'strategy': 'Web会議の効率化・議事録自動作成',
                'use_cases': ['会議録音', '自動文字起こし', '簡易議事録作成']
            })

        # Pattern 5: All-in (完全DX)
        if data['population'] and data['population'] > 500000:  # 大規模自治体
            patterns.append({
                'pattern': 'Pattern 5: All-in (完全DX)',
                'priority': 'low',
                'confidence': 0.3,
                'reason': '大規模自治体向け長期戦略',
                'products': ['Zoom Workplace (統合)'],
                'strategy': '庁内ネットワーク刷新時に提案',
                'use_cases': ['オムニチャネル分析', '会話資産化', 'デジタルツイン']
            })

        # 優先度順にソート
        patterns.sort(key=lambda x: (
            {'high': 3, 'medium': 2, 'low': 1}[x['priority']],
            x['confidence']
        ), reverse=True)

        return patterns

    def _score_pattern2(self, data: Dict) -> float:
        """Pattern 2スコアリング（PBX + 働き方改革）"""
        score = 0.0

        # PBX情報があれば高得点
        if data.get('pbx_vendor'):
            score += 0.5

            # 内線数が多いほど高得点
            ext_count = data.get('pbx_extension_count', 0)
            if ext_count > 500:
                score += 0.2
            elif ext_count > 100:
                score += 0.1

        # 人口規模（大きいほど職員数も多い）
        population = data.get('population', 0)
        if population > 500000:
            score += 0.2
        elif population > 100000:
            score += 0.1

        return min(score, 1.0)

    def _score_pattern1(self, data: Dict) -> float:
        """Pattern 1スコアリング（窓口DX）"""
        score = 0.3  # ベーススコア（全自治体に一定のニーズあり）

        # 大規模自治体ほど窓口負荷が高い
        population = data.get('population', 0)
        if population > 500000:
            score += 0.3
        elif population > 200000:
            score += 0.2

        return min(score, 1.0)

    def _score_pattern6(self, data: Dict) -> float:
        """Pattern 6スコアリング（会議効率化）"""
        score = 0.0

        # Teamsを使っている場合は高得点（競合置き換え）
        web_tool = data.get('web_meeting_tool', '')
        if web_tool and 'Teams' in web_tool:
            score += 0.5

        # Microsoft 365契約ありなら追加点
        if data.get('microsoft_365'):
            score += 0.3

        return min(score, 1.0)

    def _explain_pattern2(self, data: Dict) -> str:
        """Pattern 2の理由説明"""
        reasons = []

        if data.get('pbx_vendor'):
            vendor = data['pbx_vendor']
            ext_count = data.get('pbx_extension_count', 0)
            reasons.append(f"{vendor}製PBX（内線{ext_count}台）リプレイス対象")

        population = data.get('population', 0)
        if population > 100000:
            estimated_staff = int(population / 100)  # 推定職員数
            reasons.append(f"推定職員数{estimated_staff}名規模")

        if data.get('microsoft_365'):
            reasons.append("テレワーク基盤あり（Microsoft 365）")

        return "、".join(reasons) if reasons else "職員の働き方改革ニーズ"

    def _explain_pattern6(self, data: Dict) -> str:
        """Pattern 6の理由説明"""
        web_tool = data.get('web_meeting_tool', '')
        if web_tool and 'Teams' in web_tool:
            return f"現在{web_tool}使用中 → Zoom移行で会議効率化"
        elif data.get('microsoft_365'):
            return "Microsoft 365契約あり → Web会議の質向上提案"
        return "Web会議ツール導入・改善ニーズ"

    def _get_microsoft_strategy(self, data: Dict) -> str:
        """Microsoft対抗戦略を判定"""
        license_type = data.get('microsoft_license', '')

        if license_type == 'E5':
            return "【E5契約】全庁リプレイス狙わず、特定部署への局所最適でZP差し込み"
        elif license_type == 'E3':
            return "【E3契約】Blue Ocean戦略 - Zoom Phoneで電話インフラを握る"
        elif data.get('microsoft_365'):
            return "【Microsoft 365あり】ライセンス種類を確認し戦略決定"
        else:
            return "【Microsoft なし】完全Blue Ocean - 全製品提案可能"

    def close(self):
        self.cur.close()
        self.conn.close()


def analyze_municipality(city_code: str, city_name: str):
    """
    自治体を分析し、推奨パターンを表示
    """
    print("=" * 100)
    print(f"Sales Pattern Analysis: {city_name} ({city_code})")
    print("=" * 100)
    print()

    matcher = SalesPatternMatcher()

    try:
        # データ取得
        data = matcher.get_municipality_data(city_code)

        if not data:
            print("❌ Municipality not found")
            return

        # 基本情報表示
        print("【基本情報】")
        print(f"  人口: {data['population']:,}人" if data['population'] else "  人口: 不明")
        print(f"  財政力指数: {data['fiscal_index']}" if data['fiscal_index'] else "  財政力指数: 不明")
        print()

        # IT基盤情報
        print("【IT基盤情報】")
        if data.get('pbx_vendor'):
            print(f"  ✅ PBX: {data['pbx_vendor']} (内線{data.get('pbx_extension_count', '?')}台)")
        else:
            print(f"  ⚠️  PBX情報: 未収集")

        if data.get('microsoft_365'):
            lic = data.get('microsoft_license', '不明')
            print(f"  ✅ Microsoft 365: {lic}ライセンス")
        else:
            print(f"  ⚠️  Microsoft 365: 契約情報なし")

        if data.get('web_meeting_tool'):
            print(f"  ✅ Web会議: {data['web_meeting_tool']}")
        else:
            print(f"  ⚠️  Web会議: 情報なし")

        print()

        # パターン判定
        patterns = matcher.determine_pattern(city_code)

        if not patterns:
            print("❌ No matching patterns found")
            return

        print("【推奨セールスパターン】")
        print()

        for idx, pattern in enumerate(patterns, 1):
            priority_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }[pattern['priority']]

            print(f"{priority_icon} [{idx}] {pattern['pattern']}")
            print(f"       優先度: {pattern['priority'].upper()}")
            print(f"       確信度: {pattern['confidence']:.0%}")
            print(f"       理由: {pattern['reason']}")
            print(f"       戦略: {pattern['strategy']}")
            print(f"       製品: {', '.join(pattern['products'])}")
            print(f"       用途: {', '.join(pattern['use_cases'])}")
            print()

        print("=" * 100)

    finally:
        matcher.close()


if __name__ == "__main__":
    # 福岡市を分析
    analyze_municipality('401307', '福岡市')
