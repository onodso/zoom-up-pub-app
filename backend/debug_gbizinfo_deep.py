import os
import sys
import requests
import urllib.parse
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

API_KEY = os.getenv("GBIZINFO_API_KEY")
BASE_URL = os.getenv("GBIZINFO_BASE_URL", "https://info.gbiz.go.jp/hojin/v1/")

def debug_request(params, label):
    print(f"\n--- Test: {label} ---")
    url = f"{BASE_URL}hojin"
    headers = {
        "Accept": "application/json",
        "X-Ho-Info-Gbiz-Access-Token": API_KEY
    }
    
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    try:
        # 1. Standard Requests
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            count = data.get("hojin-infos", [])
            print(f"Success! Count: {len(count)}")
            if len(count) > 0:
                print(f"Sample: {count[0].get('name')} / {count[0].get('location')}")
        else:
            print(f"Error Body: {resp.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

def main():
    print(f"Debugging gBizINFO with Key: {API_KEY[:5]}...")
    
    # Test 1: Simple Name Search (Known to work sometimes)
    debug_request({"name": "株式会社"}, "Simple Name '株式会社'")
    
    # Test 2: Specific Name
    debug_request({"name": "北海道電力株式会社"}, "Specific Name '北海道電力株式会社'")
    
    # Test 3: Address Search (Broad)
    debug_request({"address": "北海道"}, "Address '北海道'")
    
    # Test 4: Address Search (Specific)
    debug_request({"address": "北海道札幌市"}, "Address '北海道札幌市'")
    
    # Test 5: Name + Address
    debug_request({"name": "株式会社", "address": "北海道"}, "Name + Address")
    
    # Test 6: Get by Corporate Number (Sapporo City)
    print("\n--- Test: Get by Corporate Number (Sapporo City) ---")
    url_id = f"{BASE_URL}hojin/1000020011002"
    headers = {
        "Accept": "application/json",
        "X-Ho-Info-Gbiz-Access-Token": API_KEY
    }
    try:
        resp = requests.get(url_id, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Success! Body: {resp.json().get('name')}")
        else:
            print(f"Error Body: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()

