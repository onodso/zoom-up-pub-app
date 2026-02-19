import os
import requests
import json
from dotenv import load_dotenv

try:
    load_dotenv()
except:
    pass

APP_ID = os.getenv("ESTAT_APP_ID", "ffaf6bbba7989e72e39d796fd0f62977d42e5731")
BASE_URL = "https://api.e-stat.go.jp/rest/3.0/app/json"

def dump_sapporo():
    # Categories to check: D (Admin/Finance), K (Labor?), F (Labor?), I (Safety)
    cats = ["D", "I", "K", "F"]
    
    print(f"🚀 Dumping Sapporo stats from 0000020101 (Categories: {cats})...")
    
    for cat in cats:
        url = f"{BASE_URL}/getStatsData"
        params = {
            "appId": APP_ID,
            "statsDataId": "0000020101",
            "cdArea": "01100", # Sapporo
            "cdCat01": cat,   # Exact category code prefix might be needed?
                     # API doc says: cdCat01 uses codes.
            "limit": 100, 
            "lang": "J"
        }
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code != 200:
                print(f"[{cat}] ❌ HTTP {resp.status_code}")
                continue
                
            data = resp.json()
            if "GET_STATS_DATA" not in data:
                print(f"[{cat}] ❌ Invalid JSON")
                continue
                
            result = data["GET_STATS_DATA"].get("STATISTICAL_DATA")
            if not result:
                msg = data["GET_STATS_DATA"].get("RESULT", {}).get("ERROR_MSG")
                print(f"[{cat}] ❌ No Data (Msg: {msg})")
                continue

            # Keys analysis
            class_inf = result.get("CLASS_INF", {}).get("CLASS_OBJ", [])
            code_map = {}
            for cls in class_inf:
                if cls.get("@id") == "cat01":
                     objects = cls.get("CLASS", [])
                     if isinstance(objects, dict): objects = [objects]
                     for obj in objects:
                         code_map[obj.get("@code")] = obj.get("@name")
            
            data_inf = result.get("DATA_INF", {}).get("VALUE", [])
            if isinstance(data_inf, dict): data_inf = [data_inf]
            
            print(f"[{cat}] ✅ Found {len(data_inf)} items.")
            for i, d in enumerate(data_inf):
                if i >= 10: break # Print first 10
                cat_code = d.get("@cat01")
                name = code_map.get(cat_code, "Unknown")
                val = d.get("$")
                year = d.get("@time")
                print(f"   {cat_code} {name}: {val} (Year: {year})")
        
        except Exception as e:
            print(f"[{cat}] ❌ Exception: {e}")

if __name__ == "__main__":
    dump_sapporo()
