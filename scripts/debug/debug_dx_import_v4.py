import os
import io
import zipfile
import pandas as pd
import httpx
import sys

DATA_URL = "https://www.digital.go.jp/assets/contents/node/basic_page/field_ref_resources/51a5a201-e0dd-493f-9c21-0692402d93e6/85162d87/20240712_resources_govdashboard_local_governmentdx_table_01.zip"

def decode_zip_filename(filename):
    try:
        return filename.encode('cp437').decode('cp932')
    except:
        return filename

def inspect_zip_v4():
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
            print("\n=== FULL ZIP Content List ===")
            
            for info in z.infolist():
                decoded_name = decode_zip_filename(info.filename)
                print(f"File: {decoded_name}")
                
                if decoded_name.endswith('.xlsx') or decoded_name.endswith('.csv'):
                    print(f"   >> Processing: {decoded_name}")
                    try:
                        with z.open(info.filename) as f:
                            if decoded_name.endswith('.xlsx'):
                                xls = pd.ExcelFile(f)
                                print(f"      Sheet Names: {xls.sheet_names}")
                                df = pd.read_excel(xls, sheet_name=0) # First sheet
                            else:
                                try:
                                    df = pd.read_csv(f, encoding='utf-8')
                                except:
                                    f.seek(0)
                                    df = pd.read_csv(f, encoding='shift_jis')
                            
                            print(f"      Shape: {df.shape}")
                            print(f"      Columns: {list(df.columns)[:5]}")
                            print(f"      Head(1):\n{df.head(1).to_string()}")
                            
                    except Exception as e:
                        print(f"      Error: {e}")
                print("-" * 40)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_zip_v4()
