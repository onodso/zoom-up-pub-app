import requests
import xml.etree.ElementTree as ET
import json

# KKJ API Endpoint
# URL: https://www.kkj.go.jp/api/
# Params:
#  Query: Search keyword
#  LG_Code: Local Government Code (Prefecture JIS Code 2 digits?)
#  Count: Max results
#  Start: Offset?

API_URL = "https://www.kkj.go.jp/api/rss" 
# Wait, search result said "http://www.kkj.go.jp/api/". 
# But usually RSS/Atom feeds are common for these.
# Let's try the base URL documented in search result: https://www.kkj.go.jp/api/

def fetch_kkj_sample(keyword="Zoom", lg_code="29"):
    # Try constructing query
    # Documentation implies parameters.
    # Let's try GET request
    
    params = {
        "Query": keyword,
        "LG_Code": lg_code,
        "Count": 10
    }
    
    print(f"🚀 Fetching from {API_URL} with params: {params}")
    try:
        response = requests.get("https://www.kkj.go.jp/api/", params=params, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # print raw for debug
            print(f"Raw Response (First 500 chars):\n{response.text[:500]}")
            
            # Parse XML
            try:
                root = ET.fromstring(response.content)
                # Structure is usually <rss> or <results>?
                # Let's see the tag
                print(f"Root Tag: {root.tag}")
                
                items = root.findall(".//SearchResult") 
                
                print(f"Found {len(items)} items.")
                for item in items:
                    title_elem = item.find("ProjectName")
                    if title_elem is None:
                         # Sometimes tag differs?
                         pass
                    
                    title = title_elem.text if title_elem is not None else "No Title"
                    date = item.find("Date").text if item.find("Date") is not None else "No Date"
                    # summary = item.find("Summary").text ...
                    
                    print(f"- {date}: {title}")
                    
            except ET.ParseError as e:
                print(f"XML Parse Error: {e}")
        else:
            print("❌ Request failed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing 'PBX' in '29' (Nara)...")
    fetch_kkj_sample(keyword="PBX", lg_code="29")
    
    print("\nTesting 'Zoom' in '29' (Nara)...")
    fetch_kkj_sample(keyword="Zoom", lg_code="29")
