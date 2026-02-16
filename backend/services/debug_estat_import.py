"""
e-Stat データのパース処理をデバッグ
"""

import httpx
import pandas as pd
import io

ESTAT_URL = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032143614&fileKind=0"

print("Downloading and parsing e-Stat data...")

client = httpx.Client(timeout=60.0, follow_redirects=True)
response = client.get(ESTAT_URL)

# header=8でロード
df = pd.read_excel(io.BytesIO(response.content), sheet_name=0, header=8)

print(f"Total rows: {len(df)}")
print()

print("First 20 data rows:")
print("=" * 100)

for i in range(min(20, len(df))):
    row = df.iloc[i]

    # カラム1から市区町村情報を取得
    city_info = str(row.iloc[1])
    population = row.iloc[4]

    # コード抽出
    if '_' in city_info:
        city_code_raw, city_name = city_info.split('_', 1)
        city_code = ''.join(filter(str.isdigit, city_code_raw))
        city_code_6digit = city_code.zfill(6)
    else:
        city_code_raw = "N/A"
        city_name = city_info
        city_code = "N/A"
        city_code_6digit = "N/A"

    print(f"Row {i:3}: {city_info[:30]:30} | Pop: {population:>12} | Code: {city_code_6digit}")

print()
print("=" * 100)

# 市区町村のみをカウント
city_count = 0
for i in range(len(df)):
    row = df.iloc[i]
    city_info = str(row.iloc[1])

    if '_' not in city_info:
        continue

    city_code_raw, _ = city_info.split('_', 1)
    city_code = ''.join(filter(str.isdigit, city_code_raw))

    if len(city_code) >= 5:  # 市区町村レベル
        city_count += 1

print(f"\nTotal municipalities (code length >= 5): {city_count}")

client.close()
