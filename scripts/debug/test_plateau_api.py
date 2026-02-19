import requests
import json

# PLATEAU CKAN API (Base URL for G-Spatial Information Center)
CKAN_BASE_URL = "https://www.geospatial.jp/ckan/api/3"

def search_plateau_dataset(query):
    url = f"{CKAN_BASE_URL}/action/package_search"
    
    params = {
        "q": query,
        "rows": 5
    }
    
    print(f"🚀 Searching PLATEAU CKAN for '{query}'...")
    try:
        resp = requests.get(url, params=params, timeout=10)
        print(f"📥 Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                results = data.get("result", {}).get("results", [])
                print(f"✅ Found {len(results)} datasets.")
                
                for i, ds in enumerate(results):
                    title = ds.get("title", "No Title")
                    org_title = ds.get("organization", {}).get("title", "No Org")
                    print(f"   [{i+1}] {title} ({org_title})")
                    
                    resources = ds.get("resources", [])
                    found_formats = [r.get("format", "").upper() for r in resources]
                    print(f"       Formats: {found_formats}")
            else:
                print("❌ API returned success=False")
        else:
            print(f"❌ Error: {resp.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    search_plateau_dataset("札幌市 3D都市モデル")
