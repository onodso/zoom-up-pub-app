"""
Update mayor names in database for the 17 pilot campaign targets
"""
import psycopg2
import os

MAYOR_DATA = {
    '401307': '髙島宗一郎',    # 福岡市
    '401005': '武内和久',      # 北九州市
    '402141': '後藤元秀',      # 宗像市
    '402109': '楠田大蔵',      # 太宰府市
    '402168': '工藤政宏',      # 行橋市

    # Wards use parent city mayor
    '401331': '髙島宗一郎',    # 福岡市 中央区
    '401323': '髙島宗一郎',    # 福岡市 博多区
    '401340': '髙島宗一郎',    # 福岡市 南区
    '401358': '髙島宗一郎',    # 福岡市 西区
    '401366': '髙島宗一郎',    # 福岡市 城南区
    '401374': '髙島宗一郎',    # 福岡市 早良区
    '401056': '武内和久',      # 北九州市 戸畑区
    '401064': '武内和久',      # 北九州市 小倉北区
    '401048': '武内和久',      # 北九州市 小倉南区
    '401030': '武内和久',      # 北九州市 八幡東区
    '401072': '武内和久',      # 北九州市 八幡西区
    '401021': '武内和久',      # 北九州市 門司区
}

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    user=os.getenv("POSTGRES_USER", "zoom_admin"),
    password=os.getenv("POSTGRES_PASSWORD", "password"),
    dbname=os.getenv("POSTGRES_DB", "zoom_dx_db")
)

cur = conn.cursor()

print("=" * 80)
print("UPDATING MAYOR NAMES IN DATABASE")
print("=" * 80)

for city_code, mayor_name in MAYOR_DATA.items():
    cur.execute("""
        UPDATE municipalities
        SET mayor_name = %s, updated_at = NOW()
        WHERE city_code = %s
        RETURNING city_name;
    """, (mayor_name, city_code))

    result = cur.fetchone()
    if result:
        city_name = result[0]
        print(f"✅ {city_name:25} → {mayor_name}")
    else:
        print(f"❌ City code {city_code} not found")

conn.commit()

print()
print("=" * 80)
print(f"✅ Updated {len(MAYOR_DATA)} municipalities")
print("=" * 80)

cur.close()
conn.close()
