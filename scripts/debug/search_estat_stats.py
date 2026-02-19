import os
import requests
import urllib.parse
from dotenv import load_dotenv

# .env読み込み (ローカル実行時用)
try:
    load_dotenv()
except:
    pass

APP_ID = os.getenv("ESTAT_APP_ID", "ffaf6bbba7989e72e39d796fd0f62977d42e5731")
BASE_URL = "https://api.e-stat.go.jp/rest/3.0/app/json"

def search_stats(keyword):
    url = f"{BASE_URL}/getStatsList"
    params = {
        "appId": APP_ID,
        "searchWord": keyword,
        "limit": 5, # 上位5件
        "lang": "J",
        "statsNameList": "Y" # 統計表名リストあり
    }
    
    print(f"\n🔍 Searching for '{keyword}'...")
    resp = requests.get(url, params=params)
    
    if resp.status_code != 200:
        print(f"❌ Error: {resp.status_code}")
        return

    data = resp.json()
    if "GET_STATS_LIST" not in data:
        print("❌ Invalid response or No hits")
        if "RESULT" in data:
            print(f"   Msg: {data.get('RESULT', {}).get('ERROR_MSG')}")
        return

    datalist = data["GET_STATS_LIST"].get("DATALIST_INF", {}).get("TABLE_INF", [])
    if isinstance(datalist, dict):
        datalist = [datalist]
        
    print(f"   Found {len(datalist)} tables.")
    for tbl in datalist:
        stat_id = tbl.get("@id")
        stat_name = tbl.get("STAT_NAME", {}).get("@name", "Unknown")
        title = tbl.get("TITLE", {}).get("@name", "Unknown")
        cycle = tbl.get("CYCLE", "Unknown")
        print(f"   ID: {stat_id} | {stat_name} - {title} ({cycle})")

if __name__ == "__main__":
    keywords = [
        "地方財政状況調査 R2", 
        "地方財政状況調査 2020",
        "給与実態 R2",
        "給与実態 2020",
        "定員管理 R2" 
    ]
    for k in keywords:
        search_stats(k)
