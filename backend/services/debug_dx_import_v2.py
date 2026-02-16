import os
import io
import zipfile
import pandas as pd
import httpx
import sys

# デジタル庁 データダウンロードURL (2024/7/12更新版)
DATA_URL = "https://www.digital.go.jp/assets/contents/node/basic_page/field_ref_resources/51a5a201-e0dd-493f-9c21-0692402d93e6/85162d87/20240712_resources_govdashboard_local_governmentdx_table_01.zip"

def inspect_zip_details():
    print(f"Downloading ZIP from {DATA_URL}...")
    try:
        response = httpx.get(DATA_URL, timeout=60.0, follow_redirects=True)
        response.raise_for_status()
    except Exception as e:
        print(f"Error downloading file: {e}")
        return

    print(f"Download complete. Size: {len(response.content)} bytes")

    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            print("\n=== ZIP Content List ===")
            for info in z.infolist():
                print(f"File: {info.filename} (Size: {info.file_size} bytes)")
            
            print("\n=== Inspecting Excel/CSV Files ===")
            for filename in z.namelist():
                if not (filename.endswith('.xlsx') or filename.endswith('.csv')):
                    continue

                print(f"\n>> Processing File: {filename}")
                with z.open(filename) as f:
                    if filename.endswith('.xlsx'):
                        try:
                            # Load workbook to get sheet names
                            xls = pd.ExcelFile(f)
                            print(f"   Sheet Names: {xls.sheet_names}")
                            
                            for sheet in xls.sheet_names:
                                print(f"   -- Sheet: {sheet}")
                                df = pd.read_excel(xls, sheet_name=sheet)
                                print(f"      Shape: {df.shape}")
                                print(f"      Columns (first 10): {list(df.columns)[:10]}")
                                
                                # Check for specific keywords in columns or values
                                has_hokkaido = "北海道" in df.to_string()
                                has_sapporo = "札幌市" in df.to_string()
                                print(f"      Contains '北海道': {has_hokkaido}")
                                print(f"      Contains '札幌市': {has_sapporo}")
                                
                                print("      First 3 rows:")
                                print(df.head(3).to_string())
                        except Exception as e:
                            print(f"      Error reading Excel: {e}")

                    elif filename.endswith('.csv'):
                         # CSV processing (simplified)
                        try:
                            df = pd.read_csv(f, encoding='utf-8') # try utf-8 first
                        except:
                            f.seek(0)
                            df = pd.read_csv(f, encoding='shift_jis') # fallback
                        
                        print(f"   Shape: {df.shape}")
                        print(f"   Columns: {list(df.columns)[:10]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_zip_details()
