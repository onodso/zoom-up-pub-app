import os
import io
import zipfile
import pandas as pd
import httpx
import sys

# デジタル庁 データダウンロードURL (2024/7/12更新版)
DATA_URL = "https://www.digital.go.jp/assets/contents/node/basic_page/field_ref_resources/51a5a201-e0dd-493f-9c21-0692402d93e6/85162d87/20240712_resources_govdashboard_local_governmentdx_table_01.zip"

def inspect_zip_content():
    print(f"Downloading ZIP from {DATA_URL}...")
    try:
        response = httpx.get(DATA_URL, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
    except Exception as e:
        print(f"Error downloading file: {e}")
        return

    print(f"Download complete. Size: {len(response.content)} bytes")

    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            print("\n--- ZIP Content List ---")
            for info in z.infolist():
                print(f"File: {info.filename} (Size: {info.file_size} bytes)")
            
            print("\n--- Inspecting CSV/Excel Files ---")
            for filename in z.namelist():
                if filename.endswith('.csv') or filename.endswith('.xlsx'):
                    print(f"\nProcessing: {filename}")
                    with z.open(filename) as f:
                        if filename.endswith('.csv'):
                            # Try different encodings
                            try:
                                df = pd.read_csv(f, encoding='utf-8')
                            except UnicodeDecodeError:
                                f.seek(0)
                                df = pd.read_csv(f, encoding='shift_jis')
                        else:
                            df = pd.read_excel(f)
                        
                        print(f"Columns ({len(df.columns)}):")
                        for col in df.columns:
                            print(f"  - {col}")
                        
                        print("\nFirst 3 rows:")
                        print(df.head(3).to_string())
                        print("-" * 50)

    except zipfile.BadZipFile:
        print("Error: The downloaded file is not a valid ZIP file.")
    except Exception as e:
        print(f"Error inspecting ZIP content: {e}")

if __name__ == "__main__":
    inspect_zip_content()
