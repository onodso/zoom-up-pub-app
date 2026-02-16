import os
import sys
import zipfile
import csv
import io
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SQLALCHEMY_DATABASE_URL
from models.spatial import Company, Mesh
from utils.spatial import geocode_address, lat_lon_to_mesh

# File path config
DATA_DIR = "/app/data/gbizinfo"
ZIP_FILE_NAME = "hojin_kihon.zip" # User should rename their download to this or script scans
TARGET_PREFECTURE = "北海道"

def import_csv_from_zip():
    print("🚀 Starting gBizINFO CSV Import (Streaming ZIP)...")
    
    zip_path = os.path.join(DATA_DIR, ZIP_FILE_NAME)
    
    # Check if file exists
    if not os.path.exists(zip_path):
        # Scan for any .zip in the dir
        files = [f for f in os.listdir(DATA_DIR) if f.endswith(".zip")]
        if files:
            zip_path = os.path.join(DATA_DIR, files[0])
            print(f"ℹ️  Found ZIP file: {files[0]}")
        else:
            print(f"❌ No ZIP file found in {DATA_DIR}. Please place the gBizINFO download there.")
            return

    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Find the distinct csv file
            csv_files = [f for f in zf.namelist() if f.endswith(".csv")]
            if not csv_files:
                print("❌ No CSV file found in ZIP.")
                return
            
            target_csv = csv_files[0] # Assume first CSV is the main one
            print(f"📖 Reading {target_csv} inside ZIP...")
            
            seen_meshes = set()
            count_processed = 0
            count_imported = 0
            
            with zf.open(target_csv, 'r') as f:
                # Wrap bytes in text wrapper
                reader = csv.reader(io.TextIOWrapper(f, encoding='utf-8', errors='replace'))
                
                header = next(reader, None) # Skip header
                # Need to map header columns to index?
                # Usually gBizINFO CSV has specific columns. 
                # For basic info: 
                # 0: 法人番号, 1: 法人名, ..., 所在地 is usually around index 6-8?
                # Let's inspect header or use DictReader if encoding allows simple parsing
                
                # Re-opening with DictReader for safety (assuming header exists)
                f.seek(0)
                # To use DictReader on stream, we need TextIOWrapper again? 
                # Seek invalidates wrapper? No, zip stream not seekable?
                # ZipExtFile is seekable?
                pass 
                # Re-do with DictReader logic if possible.
            
            # Re-open for clean DictReader
            # User provided file is likely UTF-8 with BOM
            encoding_to_use = 'utf-8-sig' 
            
            with zf.open(target_csv, 'r') as f_read:
                csv_reader = csv.DictReader(io.TextIOWrapper(f_read, encoding=encoding_to_use, errors='replace'))
                
                print(f"   Using Encoding: {encoding_to_use}")
                # print(f"   Columns found: {csv_reader.fieldnames}")
                
                count_batch = 0
                
                for row in csv_reader:
                    count_processed += 1
                    
                    # Map CSV columns to Variables
                    # Header: "法人番号","商号または名称",...,"登記住所",...
                    name = row.get("商号または名称") or row.get("法人名") or row.get("name")
                    
                    # API calls it "location" or "国内所在地", CSV calls it "登記住所"
                    address = row.get("登記住所")
                    if not address:
                        # Try constructing from parts if available
                        pref = row.get("都道府県") or ""
                        city = row.get("市区町村（郡）") or ""
                        addr_detail = row.get("番地以下") or ""
                        if pref or city:
                            address = f"{pref}{city}{addr_detail}"
                    
                    c_number = row.get("法人番号") or row.get("corporate_number")
                    
                    if not address:
                        continue

                    if not address.startswith(TARGET_PREFECTURE):
                        continue
                        
                    # Geocode
                    coords = geocode_address(address)
                    if coords:
                        lat, lon = coords
                        mesh_code = lat_lon_to_mesh(lat, lon, level=3)
                        
                        # 1. Add Mesh if not exists (Must be before Company due to FK)
                        if mesh_code not in seen_meshes:
                             if not session.query(Mesh).filter(Mesh.code == mesh_code).first():
                                 mesh = Mesh(code=mesh_code, lat=lat, lon=lon, level=3)
                                 session.add(mesh)
                                 # Flush mesh immediately to prevent FK error during Company query/flush
                                 session.flush()
                             seen_meshes.add(mesh_code)
                        
                        # 2. Upsert Company
                        company = session.query(Company).filter(Company.corporate_number == c_number).first()
                        if not company:
                            company = Company(corporate_number=c_number)
                        
                        company.name = name
                        company.address = address
                        company.lat = lat
                        company.lon = lon
                        company.mesh_code = mesh_code
                        company.cert_flags = {} # Populate if extra cols exist
                        
                        session.add(company)
                        
                        count_imported += 1
                        count_batch += 1
                        
                        if count_batch >= 100:
                            session.commit()
                            count_batch = 0
                            print(f"   Saved {count_imported} companies... (Last: {name})")
                    
                    if count_processed % 10000 == 0:
                        print(f"   Scanned {count_processed} rows...")
                        
                session.commit()
                print(f"✅ Finished! Scanned {count_processed}, Imported {count_imported} (Hokkaido).")

    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    import_csv_from_zip()
