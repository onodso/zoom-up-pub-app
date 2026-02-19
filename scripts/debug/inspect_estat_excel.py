"""
e-Stat Excelファイルの構造を調査
"""

import httpx
import pandas as pd
import io

ESTAT_URL = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032143614&fileKind=0"

print("=" * 80)
print("Downloading and inspecting e-Stat Excel file...")
print("=" * 80)
print()

client = httpx.Client(timeout=60.0, follow_redirects=True)
response = client.get(ESTAT_URL)

print(f"✅ Downloaded: {len(response.content):,} bytes")
print()

# Excelファイルとして読み込み（最初の30行を表示）
df = pd.read_excel(io.BytesIO(response.content), sheet_name=0, header=None)

print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print()
print("First 30 rows:")
print("=" * 80)

for i in range(min(30, len(df))):
    row = df.iloc[i]
    # 最初の10カラムのみ表示
    values = [str(v)[:30] for v in row[:10]]
    print(f"Row {i:2}: {' | '.join(values)}")

print()
print("=" * 80)
print("\nLooking for header row with '市区町村' or 'コード'...")

for i in range(min(30, len(df))):
    row = df.iloc[i]
    row_str = ' '.join([str(v) for v in row if pd.notna(v)])

    if '市区町村' in row_str or 'コード' in row_str or '人口' in row_str:
        print(f"\n✅ Potential header row found at index {i}:")
        print(f"   {list(row[:15])}")

client.close()
