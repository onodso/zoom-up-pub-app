import os
import requests
import json
from dotenv import load_dotenv

# Mock DB interaction for now
def update_municipality_plateau(city_code, dataset_url, formats):
    print(f"💾 Saving to DB: Code={city_code} URL={dataset_url} Formats={formats}")
    # In real impl, would connect to DB and update

CKAN_BASE_URL = os.getenv("PLATEAU_CKAN_URL", "https://www.geospatial.jp/ckan/api/3")

def import_plateau_data():
    # Target: Sapporo (01100)
    city_name = "札幌市"
    city_code = "01100"
    
    url = f"{CKAN_BASE_URL}/action/package_search"
    query = f"{city_name} 3D都市モデル"
    
    print(f"🚀 Searching PLATEAU for {city_name}...")
    params = {"q": query, "rows": 5}
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                results = data.get("result", {}).get("results", [])
                
                # Find the best match (e.g. latest year)
                best_dataset = None
                for ds in results:
                    title = ds.get("title", "")
                    if city_name in title and "3D都市モデル" in title:
                        best_dataset = ds
                        break
                
                if best_dataset:
                    title = best_dataset.get("title")
                    resources = best_dataset.get("resources", [])
                    formats = list(set([r.get("format", "").upper() for r in resources]))
                    
                    # Look for CityGML or 3D Tiles URL
                    citygml_url = None
                    tiles_url = None
                    for r in resources:
                        fmt = r.get("format", "").upper()
                        if "ZIP" in fmt and "CityGML" in r.get("name", ""): 
                            citygml_url = r.get("url")
                        if "3D Tiles" in r.get("name", ""): # Check name for tiles
                             tiles_url = r.get("url")
                    
                    print(f"✅ Found Dataset: {title}")
                    print(f"   Formats: {formats}")
                    
                    update_municipality_plateau(city_code, citygml_url or "Found", formats)
                else:
                    print("⚠️ No matching dataset found.")
            else:
                print("❌ API success=False")
        else:
            print(f"❌ Error: {resp.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    import_plateau_data()
