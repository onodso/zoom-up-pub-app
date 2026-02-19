"""
Extract mayor and contact information for pilot campaign targets
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os

# 17 target cities from pilot campaign
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

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    user=os.getenv("POSTGRES_USER", "zoom_admin"),
    password=os.getenv("POSTGRES_PASSWORD", "password"),
    dbname=os.getenv("POSTGRES_DB", "zoom_dx_db")
)

cur = conn.cursor(cursor_factory=RealDictCursor)

# First check what columns exist
cur.execute("""
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'municipalities'
ORDER BY ordinal_position;
""")
columns = [row['column_name'] for row in cur.fetchall()]

print("=" * 100)
print("MUNICIPALITY DATABASE SCHEMA")
print("=" * 100)
print(f"Available columns: {', '.join(columns)}")
print()

# Query target municipalities
cur.execute(f"""
SELECT *
FROM municipalities
WHERE city_code IN ({','.join(f"'{c}'" for c in TARGET_CODES)})
ORDER BY city_name;
""")

results = cur.fetchall()

print("=" * 100)
print("PILOT CAMPAIGN TARGET MUNICIPALITIES (17 cities)")
print("=" * 100)

for idx, row in enumerate(results, 1):
    print(f"\n[{idx}] {row['city_name']} ({row['city_code']})")
    print(f"    Prefecture: {row['prefecture']}")
    print(f"    Region: {row['region']}")
    print(f"    Population: {row.get('population', 'N/A'):,}" if row.get('population') else "    Population: N/A")

    # Check for DX status
    dx_status = row.get('dx_status')
    if dx_status:
        print(f"    DX Status: {json.dumps(dx_status, ensure_ascii=False, indent=8)}")

    # Check for any contact/mayor fields
    for col in ['mayor_name', 'mayor', 'contact', 'official_url', 'email']:
        if col in row and row[col]:
            print(f"    {col}: {row[col]}")

print("\n" + "=" * 100)
print("NEXT STEPS")
print("=" * 100)
print("If mayor names are not in the database, we need to:")
print("1. Scrape from official city websites")
print("2. Or send to department: 'DX推進課 御中' or '企画調整課 御中'")
print("=" * 100)

cur.close()
conn.close()
