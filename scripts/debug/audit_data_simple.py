"""
Simple data completeness audit
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

# Check each field individually
fields = [
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

print(f"{'フィールド':30} {'収集済み':>12} {'完全性':>10} {'状態':>8}")
print("-" * 100)

results = []

for field, display_name in fields:
    cur.execute(f"SELECT COUNT(*) as filled FROM municipalities WHERE {field} IS NOT NULL;")
    filled = cur.fetchone()['filled']
    pct = (filled / total_count) * 100

    if pct >= 90:
        status = "✅ 優秀"
    elif pct >= 50:
        status = "⚠️  普通"
    elif pct >= 10:
        status = "❌ 不足"
    else:
        status = "🚫 ほぼ無"

    print(f"{display_name:30} {filled:>12,} {pct:>9.1f}% {status:>8}")
    results.append((field, filled, pct))

print()
print("=" * 100)
print("【カテゴリ別サマリー】")
print("=" * 100)

categories = {
    '基本情報 (必須)': ['city_code', 'prefecture', 'city_name', 'region', 'city_type'],
    '地理情報': ['latitude', 'longitude', 'official_url'],
    '人口統計': ['population', 'households', 'elderly_ratio', 'population_decline_rate'],
    '財政・組織': ['fiscal_index', 'staff_reduction_rate'],
    '行政・DX': ['mayor_name', 'mayor_speech_url', 'dx_status'],
    '連絡先': ['contact_phone', 'contact_email'],
}

for cat, flds in categories.items():
    cat_results = [(f, c, p) for f, c, p in results if f in flds]
    avg = sum(p for _, _, p in cat_results) / len(cat_results) if cat_results else 0

    if avg >= 80:
        status = "✅ 充実"
    elif avg >= 40:
        status = "⚠️  部分的"
    else:
        status = "❌ 不十分"

    print(f"{cat:25} {avg:>6.1f}% {status}")

print()
print("=" * 100)
print("【福岡市 サンプルデータ】")
print("=" * 100)

cur.execute("SELECT * FROM municipalities WHERE city_code = '401307';")
sample = cur.fetchone()

if sample:
    for k, v in sample.items():
        if k in ['id', 'created_at', 'updated_at']:
            continue

        if isinstance(v, dict):
            v_str = json.dumps(v, ensure_ascii=False)[:80] + "..." if len(str(v)) > 80 else json.dumps(v, ensure_ascii=False)
        elif v is None:
            v_str = "❌ NULL"
        else:
            v_str = str(v)[:80]

        print(f"{k:25} : {v_str}")

print()
print("=" * 100)
print("【総合評価】")
print("=" * 100)

avg_all = sum(p for _, _, p in results) / len(results)
print(f"全体データ完全性: {avg_all:.1f}%")
print()

if avg_all >= 60:
    grade = "✅ B+ 良好"
    comment = "スコアリングとAI提案生成には十分なデータあり"
elif avg_all >= 40:
    grade = "⚠️  C+ 普通"
    comment = "基本機能は動作するが、拡充推奨"
else:
    grade = "❌ D 不足"
    comment = "データ収集の大幅強化が必要"

print(f"評価: {grade}")
print(f"コメント: {comment}")
print()
print("=" * 100)

cur.close()
conn.close()
