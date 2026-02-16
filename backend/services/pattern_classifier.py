#!/usr/bin/env python3
"""
DX推進パターン分類スクリプト

自治体のDX推進状況を分析し、7つの典型的なパターンに自動分類します。
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Tuple
import re


class PatternClassifier:
    """DX推進パターン分類器"""
    
    # パターン定義
    PATTERNS = {
        1: 'DX Leaders',
        2: 'Digital Followers',
        3: 'Selective Adopters',
        4: 'Budget Constrained',
        5: 'Early Starters',
        6: 'Laggards',
        7: 'Data Insufficient'
    }
    
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
    
    def parse_percentage(self, value: Optional[str]) -> float:
        """パーセンテージ文字列を0.0-1.0の浮動小数点数に変換"""
        if not value:
            return 0.0
        
        # '75%' -> 0.75
        match = re.search(r'(\d+)', value)
        if match:
            return float(match.group(1)) / 100.0
        return 0.0
    
    def get_municipality_data(self, city_code: str) -> Optional[Dict]:
        """自治体の基本データとDXステータスを取得"""
        self.cur.execute("""
            SELECT 
                m.city_code,
                m.city_name,
                m.population,
                m.dx_status
            FROM municipalities m
            WHERE m.city_code = %s
        """, (city_code,))
        
        return self.cur.fetchone()
    
    def classify_municipality(self, city_code: str) -> Tuple[int, str, float, Dict]:
        """
        単一自治体のパターン分類
        
        Returns:
            (pattern_id, pattern_name, confidence_score, indicators)
        """
        # データ取得
        data = self.get_municipality_data(city_code)
        
        if not data or not data['dx_status']:
            return (7, self.PATTERNS[7], 0.0, {
                'policy_status': None,
                'mynumber_rate': 0.0,
                'online_proc_rate': 0.0,
                'population': data['population'] if data else 0
            })
        
        dx_status = data['dx_status']
        population = data['population'] or 0
        
        # 指標の抽出
        policy = dx_status.get('自治体DXの推進体制等_全体方針策定', '') == '実施'
        mynumber = self.parse_percentage(
            dx_status.get('住民サービスのDX_マイナンバーカードの保有状況', '0%')
        )
        online_proc = self.parse_percentage(
            dx_status.get('住民サービスのDX_よく使う32手続のオンライン化状況', '0%')
        )
        
        indicators = {
            'policy_status': '実施' if policy else '未実施',
            'mynumber_rate': mynumber,
            'online_proc_rate': online_proc,
            'population': population
        }
        
        # パターン判定 (Decision Tree - 実績優先版)
        # Pattern 1: DX Leaders - 方針策定済み + 高実績
        if policy and mynumber >= 0.75 and online_proc >= 0.50:
            return (1, self.PATTERNS[1], 0.95, indicators)
        
        # Pattern 2: Digital Followers - 方針策定済み OR 高実績（方針なしでも実績あり）
        elif (policy and mynumber >= 0.70 and online_proc >= 0.30) or \
             (not policy and mynumber >= 0.70 and online_proc >= 0.50):
            # 神戸市のようなケース: 方針未策定だが実績は高水準
            return (2, self.PATTERNS[2], 0.90, indicators)
        
        # Pattern 3: Selective Adopters - 特定分野で高実績（マイナンバーカードのみ高い）
        elif not policy and mynumber >= 0.75 and online_proc < 0.50:
            return (3, self.PATTERNS[3], 0.85, indicators)
        
        # Pattern 4: Budget Constrained - 方針あるが実装遅延
        elif policy and online_proc < 0.20 and population < 50000:
            return (4, self.PATTERNS[4], 0.80, indicators)
        
        # Pattern 5: Early Starters - 方針策定済みだが実績はこれから
        elif policy and mynumber < 0.70:
            return (5, self.PATTERNS[5], 0.75, indicators)
        
        # Pattern 6: Laggards - 方針未策定 + 実績も低水準
        else:
            return (6, self.PATTERNS[6], 0.70, indicators)
    
    def save_classification(self, city_code: str, pattern_id: int, pattern_name: str,
                          confidence: float, indicators: Dict):
        """分類結果をデータベースに保存"""
        self.cur.execute("""
            INSERT INTO municipality_patterns 
            (city_code, pattern_id, pattern_name, confidence_score, 
             policy_status, mynumber_rate, online_proc_rate, population, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (city_code) DO UPDATE SET
                pattern_id = EXCLUDED.pattern_id,
                pattern_name = EXCLUDED.pattern_name,
                confidence_score = EXCLUDED.confidence_score,
                policy_status = EXCLUDED.policy_status,
                mynumber_rate = EXCLUDED.mynumber_rate,
                online_proc_rate = EXCLUDED.online_proc_rate,
                population = EXCLUDED.population,
                updated_at = NOW();
        """, (
            city_code, pattern_id, pattern_name, confidence,
            indicators['policy_status'],
            indicators['mynumber_rate'],
            indicators['online_proc_rate'],
            indicators['population']
        ))
    
    def classify_all(self):
        """全自治体の一括分類"""
        print("🚀 全自治体のパターン分類を開始します...")
        
        # 全自治体のcity_codeを取得
        self.cur.execute("SELECT city_code FROM municipalities ORDER BY city_code;")
        city_codes = [row['city_code'] for row in self.cur.fetchall()]
        
        total = len(city_codes)
        success_count = 0
        pattern_counts = {i: 0 for i in range(1, 8)}
        
        for i, city_code in enumerate(city_codes, 1):
            try:
                pattern_id, pattern_name, confidence, indicators = self.classify_municipality(city_code)
                self.save_classification(city_code, pattern_id, pattern_name, confidence, indicators)
                
                pattern_counts[pattern_id] += 1
                success_count += 1
                
                if i % 100 == 0:
                    self.conn.commit()
                    print(f"  進捗: {i}/{total} ({i*100//total}%)")
            
            except Exception as e:
                print(f"❌ Error processing {city_code}: {e}")
        
        self.conn.commit()
        
        print(f"\n✅ 分類完了: {success_count}/{total} 自治体")
        print("\n📊 パターン分布:")
        for pattern_id, count in pattern_counts.items():
            pattern_name = self.PATTERNS[pattern_id]
            percentage = count * 100 / total if total > 0 else 0
            print(f"  {pattern_id}. {pattern_name}: {count} ({percentage:.1f}%)")
    
    def close(self):
        """データベース接続を閉じる"""
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    classifier = PatternClassifier()
    try:
        classifier.classify_all()
    finally:
        classifier.close()
