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

def inspect_zip_v3():
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
            print("\n=== ZIP Content List (Decoded) ===")
            target_files = []
            
            for info in z.infolist():
                decoded_name = decode_zip_filename(info.filename)
                print(f"File: {decoded_name} (Original: {info.filename}, Size: {info.file_size} bytes)")
                
                # Filter for Excel files that might contain municipality data
                if decoded_name.endswith('.xlsx'):
                     target_files.append((info.filename, decoded_name))

            print("\n=== Inspecting Potential Municipality Files ===")
            for original_name, decoded_name in target_files:
                print(f"\n>> Checking: {decoded_name}")
                
                # Skip Likely Prefecture files based on name (if recognizable)
                if "都道府県" in decoded_name and "市町村" not in decoded_name:
                    print("   Skipping (seems to be prefecture data)")
                    continue

                try:
                    with z.open(original_name) as f:
                        xls = pd.ExcelFile(f)
                        print(f"   Sheet Names: {xls.sheet_names}")
                        
                        for sheet in xls.sheet_names:
                            df = pd.read_excel(xls, sheet_name=sheet)
                            print(f"   Shape: {df.shape}")
                            
                            # Check if it looks like municipality data (many columns or specific keywords in header)
                            # Transpose check: if headers are municipalities, columns should be > 1000
                            # If headers are items, rows should be > 1000 (if one row per muni)
                            
                            print(f"   Columns (first 5): {list(df.columns)[:5]}")
                            
                            # Check for Sapporo or specific city codes
                            sample_text = df.head().to_string() + str(list(df.columns))
                            has_sapporo = "札幌" in sample_text
                            has_city_code = "01100" in sample_text or "1100" in sample_text
                            
                            print(f"   Contains '札幌': {has_sapporo}")
                            print(f"   Contains '01100': {has_city_code}")
                            
                            # If it looks promising, show more info
                            if has_sapporo or df.shape[1] > 1000 or df.shape[0] > 1000:
                                print("   *** MATCH: Likely Municipality Data ***")
                                print(f"   First 3 rows:\n{df.head(3).to_string()}")

                except Exception as e:
                    print(f"   Error reading file: {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_zip_v3()
