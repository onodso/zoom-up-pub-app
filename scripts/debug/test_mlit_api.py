import os
import requests
import json
from dotenv import load_dotenv

# .env読み込み
load_dotenv()

API_KEY = os.getenv("MLIT_API_KEY")
BASE_URL = os.getenv("MLIT_BASE_URL", "https://data-platform.mlit.go.jp/api/v1/")

if not API_KEY:
    print("❌ MLIT_API_KEY not found in environment variables.")
    exit(1)

print(f"🔑 Using API Key: {API_KEY[:5]}...{API_KEY[-5:]}")
print(f"🌍 Base URL: {BASE_URL}")

# GraphQL Query (Direct string interpolation)
query = """
query {
  search(term: "人口", first: 0, size: 5) {
    totalNumber
    searchResults {
      id
      title
      lat
      lon
      dataset_id
      catalog_id
    }
  }
}
"""

headers = {
    "Content-Type": "application/json",
    "apikey": API_KEY
}

try:
    print("\n🚀 Sending GraphQL request...")
    # No variables needed
    response = requests.post(
        BASE_URL,
        json={"query": query},
        headers=headers,
        timeout=10
    )
    
    print(f"📥 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            print("❌ GraphQL Errors:")
            print(json.dumps(data["errors"], indent=2, ensure_ascii=False))
        else:
            print("✅ Success!")
            search_res = data.get("data", {}).get("search", {})
            print(f"   Total Hits: {search_res.get('totalNumber', 'Unknown')}")
            
            items = search_res.get("searchResults", [])
            for i, item in enumerate(items):
                print(f"   [{i+1}] {item.get('title')} (ID: {item.get('id')})")
                print(f"       Dataset: {item.get('dataset_id')}")
    else:
        print("❌ HTTP Error:")
        print(response.text)

except Exception as e:
    print(f"❌ Exception: {e}")
