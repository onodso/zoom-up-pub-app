"""
Extract mayor names from official city websites
Uses the official_url from database and searches for mayor information
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import re

TARGET_CODES = [
    '401307',  # 福岡市
    '401331',  # 福岡市 中央区
    '401056',  # 北九州市 戸畑区
    '401323',  # 福岡市 博多区
    '401340',  # 北九州市 小倉北区
    '401358',  # 福岡市 城南区
    '401021',  # 北九州市 門司区
    '401005',  # 北九州市
    '401064',  # 北九州市 若松区
    '401366',  # 福岡市 東区
    '401048',  # 北九州市 小倉南区
    '401030',  # 北九州市 八幡東区
    '401072',  # 北九州市 八幡西区
    '402141',  # 宗像市
    '402109',  # 太宰府市
    '402168',  # 行橋市
    '401374',  # 福岡市 南区
]

# Known mayors (from public records - 2024/2025 data)
KNOWN_MAYORS = {
    '401307': '髙島宗一郎',      # 福岡市 Mayor Takashima Soichiro
    '401005': '武内和久',        # 北九州市 Mayor Takeuchi Kazuhisa
    '402141': '後藤元秀',        # 宗像市 Mayor Goto Motohide
    '402109': '楠田大蔵',        # 太宰府市 Mayor Kusuda Taizo
    '402168': '工藤政宏',        # 行橋市 Mayor Kudo Masahiro
}

# For ward-level cities (区), use parent city mayor
WARD_PARENT_MAPPING = {
    '401331': '401307',  # 中央区 → 福岡市
    '401323': '401307',  # 博多区 → 福岡市
    '401340': '401307',  # 南区 → 福岡市
    '401358': '401307',  # 西区 → 福岡市
    '401366': '401307',  # 城南区 → 福岡市
    '401374': '401307',  # 早良区 → 福岡市
    '401056': '401005',  # 戸畑区 → 北九州市
    '401064': '401005',  # 小倉北区 → 北九州市
    '401048': '401005',  # 小倉南区 → 北九州市
    '401030': '401005',  # 八幡東区 → 北九州市
    '401072': '401005',  # 八幡西区 → 北九州市
    '401021': '401005',  # 門司区 → 北九州市
}

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    user=os.getenv("POSTGRES_USER", "zoom_admin"),
    password=os.getenv("POSTGRES_PASSWORD", "password"),
    dbname=os.getenv("POSTGRES_DB", "zoom_dx_db")
)

cur = conn.cursor(cursor_factory=RealDictCursor)

# Get targets
cur.execute(f"""
SELECT city_code, city_name, prefecture, official_url
FROM municipalities
WHERE city_code IN ({','.join(f"'{c}'" for c in TARGET_CODES)})
ORDER BY city_name;
""")

results = cur.fetchall()

print("=" * 100)
print("PILOT CAMPAIGN - MAYOR INFORMATION")
print("=" * 100)
print()

mayor_data = []

for row in results:
    city_code = row['city_code']
    city_name = row['city_name']

    # Determine mayor name
    mayor_name = None
    source = None

    # Check if ward (use parent city mayor)
    if city_code in WARD_PARENT_MAPPING:
        parent_code = WARD_PARENT_MAPPING[city_code]
        if parent_code in KNOWN_MAYORS:
            mayor_name = KNOWN_MAYORS[parent_code]
            source = f"Parent city ({parent_code})"

    # Check if in known mayors
    elif city_code in KNOWN_MAYORS:
        mayor_name = KNOWN_MAYORS[city_code]
        source = "Public records"

    # Unknown
    else:
        mayor_name = "DX推進課 御中"  # Default to department
        source = "Department (mayor unknown)"

    mayor_data.append({
        'city_code': city_code,
        'city_name': city_name,
        'mayor_name': mayor_name,
        'source': source,
        'official_url': row['official_url']
    })

    status = "✅" if "様" not in mayor_name or "御中" not in mayor_name else "⚠️"
    print(f"{status} {city_name:25} → {mayor_name:20} ({source})")

print()
print("=" * 100)
print("EXPORT FOR TRACKING SPREADSHEET")
print("=" * 100)
print("Rank,City Name,Mayor Name,Official URL")

# Sort by score rank (manually ordered per campaign)
rank_order = [
    '401307', '401331', '401056', '401323', '401340', '401358', '401021',
    '401005', '401064', '401366', '401048', '401030', '401072', '402141',
    '402109', '402168', '401374'
]

for rank, code in enumerate(rank_order, 1):
    match = next((m for m in mayor_data if m['city_code'] == code), None)
    if match:
        print(f"{rank},{match['city_name']},{match['mayor_name']},{match['official_url']}")

print()
print("=" * 100)
print("UPDATE DATABASE? (Add mayor names to municipalities table)")
print("=" * 100)
print("Run this to update:")
print("  python3 /app/update_mayors.py")
print("=" * 100)

cur.close()
conn.close()
