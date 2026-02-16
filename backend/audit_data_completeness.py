"""
Comprehensive audit of municipality data completeness
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    user=os.getenv("POSTGRES_USER", "zoom_admin"),
    password=os.getenv("POSTGRES_PASSWORD", "password"),
    dbname=os.getenv("POSTGRES_DB", "zoom_dx_db")
)

cur = conn.cursor(cursor_factory=RealDictCursor)

# Get total count
cur.execute("SELECT COUNT(*) as total FROM municipalities;")
total_count = cur.fetchone()['total']

print("=" * 100)
print(f"自治体基礎情報 収集状況監査 - 全{total_count:,}自治体")
print("=" * 100)
print()

# Check completeness for each field
fields_to_check = [
    ('city_code', '自治体コード'),
    ('prefecture', '都道府県'),
    ('city_name', '自治体名'),
    ('region', '地域ブロック'),
    ('population', '人口'),
    ('households', '世帯数'),
    ('mayor_name', '市長名'),
    ('official_url', '公式サイトURL'),
    ('contact_phone', '代表電話'),
    ('contact_email', '代表メール'),
    ('latitude', '緯度'),
    ('longitude', '経度'),
    ('fiscal_index', '財政力指数'),
    ('population_decline_rate', '人口減少率'),
    ('elderly_ratio', '高齢化率'),
    ('staff_reduction_rate', '職員削減率'),
    ('dx_status', 'DX推進状況'),
    ('city_type', '自治体種別'),
    ('mayor_speech_url', '市長メッセージURL'),
]

print("【データ完全性レポート】")
print()
print(f"{'フィールド':30} {'収集済み':>12} {'完全性':>10} {'状態':>8}")
print("-" * 100)

completeness_report = []

for field, display_name in fields_to_check:
    # Count non-null values
    cur.execute(f"""
        SELECT COUNT(*) as filled
        FROM municipalities
        WHERE {field} IS NOT NULL
        AND (CASE
            WHEN pg_typeof({field}) = 'text'::regtype THEN {field} != ''
            WHEN pg_typeof({field}) = 'jsonb'::regtype THEN {field} != 'null'::jsonb
            ELSE TRUE
        END);
    """)

    filled_count = cur.fetchone()['filled']
    completeness = (filled_count / total_count) * 100

    # Status indicator
    if completeness >= 90:
        status = "✅ 優秀"
    elif completeness >= 50:
        status = "⚠️  普通"
    elif completeness >= 10:
        status = "❌ 不足"
    else:
        status = "🚫 ほぼ無"

    print(f"{display_name:30} {filled_count:>12,} {completeness:>9.1f}% {status:>8}")

    completeness_report.append({
        'field': field,
        'display_name': display_name,
        'filled': filled_count,
        'total': total_count,
        'completeness': completeness
    })

print()
print("=" * 100)
print("【カテゴリ別サマリー】")
print("=" * 100)

# Category analysis
categories = {
    '基本情報': ['city_code', 'prefecture', 'city_name', 'region', 'city_type'],
    '地理情報': ['latitude', 'longitude', 'official_url'],
    '人口統計': ['population', 'households', 'elderly_ratio', 'population_decline_rate'],
    '財政情報': ['fiscal_index', 'staff_reduction_rate'],
    '行政情報': ['mayor_name', 'mayor_speech_url', 'dx_status'],
    '連絡先情報': ['contact_phone', 'contact_email'],
}

for category, fields in categories.items():
    category_scores = [r for r in completeness_report if r['field'] in fields]
    avg_completeness = sum(r['completeness'] for r in category_scores) / len(category_scores) if category_scores else 0

    if avg_completeness >= 80:
        status = "✅ 充実"
    elif avg_completeness >= 40:
        status = "⚠️  部分的"
    else:
        status = "❌ 不十分"

    print(f"{category:15} {avg_completeness:>6.1f}% {status}")

print()
print("=" * 100)
print("【サンプルデータ】福岡市（パイロット対象 #1）")
print("=" * 100)

cur.execute("""
    SELECT *
    FROM municipalities
    WHERE city_code = '401307';
""")

sample = cur.fetchone()

if sample:
    for key, value in sample.items():
        if key in ['created_at', 'updated_at', 'id']:
            continue

        # Format value
        if isinstance(value, dict):
            display_value = json.dumps(value, ensure_ascii=False, indent=2)[:200] + "..." if len(str(value)) > 200 else json.dumps(value, ensure_ascii=False, indent=2)
        elif value is None:
            display_value = "❌ NULL"
        elif isinstance(value, (int, float)):
            display_value = f"{value:,}" if isinstance(value, int) else f"{value:.2f}"
        else:
            display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)

        print(f"{key:25} : {display_value}")

print()
print("=" * 100)
print("【データソース情報】")
print("=" * 100)

# Check where data came from
print("✅ 確実に収集済み:")
print("   - city_code, prefecture, city_name, region (手動入力/公式リスト)")
print("   - official_url (自治体公式サイト)")
print()
print("⚠️  推定値・部分的:")
print("   - population, households (random推定値 - 実データ未連携)")
print("   - mayor_name (17自治体のみ手動入力)")
print()
print("❌ 未収集:")
print("   - latitude, longitude (地理座標)")
print("   - fiscal_index (財政力指数)")
print("   - population_decline_rate (人口減少率)")
print("   - elderly_ratio (高齢化率)")
print("   - staff_reduction_rate (職員削減率)")
print("   - contact_phone, contact_email (連絡先)")
print("   - mayor_speech_url (市長メッセージURL)")
print()

print("=" * 100)
print("【総合評価】")
print("=" * 100)

total_fields = len(fields_to_check)
avg_overall = sum(r['completeness'] for r in completeness_report) / total_fields

print(f"全体データ完全性: {avg_overall:.1f}%")
print()

if avg_overall >= 70:
    print("評価: ✅ 良好 - スコアリングとAI提案生成には十分なデータあり")
elif avg_overall >= 40:
    print("評価: ⚠️  普通 - 基本機能は動作するが、拡充の余地あり")
else:
    print("評価: ❌ 不足 - データ収集の強化が必要")

print()
print("推奨アクション:")
print("1. e-Stat API連携で人口・財政データ取得（優先度：中）")
print("2. 地理座標の一括取得（優先度：低 - マップ可視化時に必要）")
print("3. 市長情報の拡充（優先度：低 - Phase 2スケール時）")
print("=" * 100)

cur.close()
conn.close()
