import sys
import os
import requests
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from models.spatial import Company, Mesh
from utils.spatial import geocode_address, lat_lon_to_mesh
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GBIZINFO_API_KEY")
BASE_URL = os.getenv("GBIZINFO_BASE_URL", "https://info.gbiz.go.jp/hojin/v1/")

def import_gbizinfo_sample():
    print("🚀 Starting gBizINFO Import (Sample)...")
    
    db = SessionLocal()
    
    # Use "株式会社" to get *some* data for PoC
    # In production, we would loop through all pages or specific lists.
    url = f"{BASE_URL}hojin"
    headers = {
        "Accept": "application/json",
        "X-Ho-Info-Gbiz-Access-Token": API_KEY
    }
    params = {
        "name": "株式会社", # Generic query that works
        "limit": 50
    }
    
    try:
        print(f"📡 Fetching data from {url}...")
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        
        if resp.status_code != 200:
            print(f"❌ API Error: {resp.status_code} {resp.text}")
            print("⚠️ Switching to MOCK DATA due to API failure...")
            results = [
                {"corporate_number": "1000020011002", "name": "札幌市役所", "location": "札幌市中央区北1条西2丁目"},
                {"corporate_number": "4430005000959", "name": "国立大学法人北海道大学", "location": "北海道札幌市北区北8条西5丁目"},
                {"corporate_number": "9430001021437", "name": "株式会社北海道銀行", "location": "北海道札幌市中央区大通西4丁目1番地"},
                {"corporate_number": "3430001020612", "name": "株式会社北海道放送", "location": "北海道札幌市中央区北1条西5丁目2番地"},
                {"corporate_number": "6430001022874", "name": "北海電気工事株式会社", "location": "北海道札幌市白石区菊水2条1丁目8番21号"}
            ]
        else:
            data = resp.json()
            results = data.get("hojin-infos", [])
            
        print(f"✅ Processing {len(results)} companies...")
        
        count_geocoded = 0
        seen_meshes = set()
        
        for info in results:
            c_number = info.get("corporate_number")
            c_name = info.get("name")
            c_addr = info.get("location")
            
            if not c_addr:
                continue
                
            # Geocode
            coords = geocode_address(c_addr)
            if coords:
                lat, lon = coords
                mesh_code = lat_lon_to_mesh(lat, lon, level=3) # 3rd Mesh (1km)
                
                # Upsert Company
                company = db.query(Company).filter(Company.corporate_number == c_number).first()
                if not company:
                    company = Company(corporate_number=c_number)
                
                company.name = c_name
                company.address = c_addr
                company.lat = lat
                company.lon = lon
                company.mesh_code = mesh_code
                
                # Check for certs (using dummy parsing/flags for now as API response varies)
                # In real scenario, we parse 'certification' key
                company.cert_flags = {} 
                
                db.add(company)
                
                # Ensure Mesh exists
                # Check local cache first to avoid duplicates in same session
                if mesh_code not in seen_meshes:
                    mesh = db.query(Mesh).filter(Mesh.code == mesh_code).first()
                    if not mesh:
                        # Create mesh master (approx center)
                        mesh = Mesh(code=mesh_code, lat=lat, lon=lon, level=3)
                        db.add(mesh)
                        seen_meshes.add(mesh_code)
                    else:
                        seen_meshes.add(mesh_code)
                
                count_geocoded += 1
                print(f"   📍 {c_name} -> {mesh_code} ({lat:.4f}, {lon:.4f})")
            else:
                print(f"   ⚠️ Could not geocode: {c_addr}")
        
        db.commit()
        print(f"✅ Imported {count_geocoded} companies with spatial index.")
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import_gbizinfo_sample()
