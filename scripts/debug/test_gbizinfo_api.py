import os
import requests
import json
from dotenv import load_dotenv

try:
    load_dotenv()
except:
    pass

API_KEY = os.getenv("GBIZINFO_API_KEY")
BASE_URL = os.getenv("GBIZINFO_BASE_URL", "https://info.gbiz.go.jp/hojin/v1/")

if not API_KEY:
    print("❌ GBIZINFO_API_KEY not found")
    exit(1)

print(f"🔑 Using API Key: {API_KEY[:5]}...")

def test_gbizinfo():
    url = f"{BASE_URL}hojin"
    headers = {
        "Accept": "application/json",
        "X-Ho-Info-Gbiz-Access-Token": API_KEY
    }
    # Try specific address and specific company name
    tests = [
        {"type": "address", "val": "東京都千代田区霞が関1-3-1"}, # METI
        {"type": "name", "val": "北海道電力株式会社"} # Known large company
    ]
    
    for t in tests:
        val = t["val"]
        print(f"🚀 Searching gBizINFO for {t['type']}='{val}'...")
        params = {
            t["type"]: val,
            "limit": 1
        }
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=20)
            print(f"📥 Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("hojin-infos", [])
                print(f"✅ Found {len(results)} results.")
                if results:
                    for i, info in enumerate(results):
                        name = info.get("name", "Unknown")
                        corp_number = info.get("corporate_number", "")
                        addr = info.get("location", "No Address")
                        print(f"   [{i+1}] {name} ({corp_number}) @ {addr}")
            else:
                print(f"❌ Error: {resp.text}")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_gbizinfo()
