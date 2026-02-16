import os
import requests
import json

# E-Stat App ID (from env or hardcoded for testing)
APP_ID = os.getenv("ESTAT_APP_ID", "ffaf6bbba7989e72e39d796fd0f62977d42e5731")
BASE_URL = "https://api.e-stat.go.jp/rest/3.0/app/json"

def get_meta_info(statsDataId):
    url = f"{BASE_URL}/getStatsData"
    params = {
        "appId": APP_ID,
        "statsDataId": statsDataId,
        "limit": 1, # メタデータだけでよいのでデータは最小限
        "lang": "J"
    }
    
    print(f"📡 Fetching metadata for {statsDataId}...")
    resp = requests.get(url, params=params)
    
    if resp.status_code != 200:
        print(f"❌ Error: {resp.status_code}")
        print(resp.text)
        return

    data = resp.json()
    if "GET_STATS_DATA" not in data:
        print("❌ Invalid response format (No GET_STATS_DATA)")
        print(data)
        return

    get_stats = data["GET_STATS_DATA"]
    result_info = get_stats.get("RESULT", {})
    if result_info.get("STATUS") != 0:
        print(f"❌ API Reported Error: {result_info.get('ERROR_MSG')}")
        print(f"   Status Code: {result_info.get('STATUS')}")
        print(f"   Details: {result_info.get('DATE')}")
        return

    result = get_stats.get("STATISTICAL_DATA")
    if result is None:
        print("❌ STATISTICAL_DATA is missing but STATUS=0? Dumping keys:")
        print(get_stats.keys())
        return

    class_inf = result.get("CLASS_INF", {}).get("CLASS_OBJ", [])
    
    print(f"📊 Table Info: {result.get('TABLE_INF', {}).get('STAT_NAME', {}).get('@name', 'Unknown')}")
    print(f"   Note: {result.get('TABLE_INF', {}).get('TITLE', {}).get('@name', 'Unknown')}")

    for cls in class_inf:
        cls_id = cls.get("@id")
        cls_name = cls.get("@name")
        print(f"\n📂 Class: {cls_name} (ID: {cls_id})")
        
        objects = cls.get("CLASS", [])
        if isinstance(objects, dict):
            objects = [objects]
            
        # Search for specific keywords or dump all if small count
        keywords = ["歳入", "歳出", "職員", "一般行政", "総額", "総数"]
        
        for obj in objects:
            code = obj.get("@code")
            name = obj.get("@name")
            unit = obj.get("@unit", "")
            
            # Print ALL items for detailed inspection (or matching keywords)
            # If matches keyword, highligh it
            if any(k in name for k in keywords):
                print(f"   ✨ MATCH! {name} (Code: {code}) unit={unit}")
            else:
                print(f"   - {name} (Code: {code}) unit={unit}")

if __name__ == "__main__":
    # 特定したID: 
    # 0003197607: 地方財政状況調査 決算 (歳入歳出)
    # 0003172929: 職員数の状況 (職員数)
    ids = ["0003197607", "0003172929"]
    
    for i in ids:
        print(f"\n{'='*30}\nID: {i}")
        get_meta_info(i)
