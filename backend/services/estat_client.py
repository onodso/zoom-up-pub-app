"""
e-Stat MCP クライアント（統計データ取得）
"""
import os
import httpx
from typing import Dict, List

ESTAT_APP_ID = os.getenv('ESTAT_APP_ID', '')
ESTAT_BASE_URL = 'https://api.e-stat.go.jp/rest/3.0/app/json'


class EStatClient:
    def __init__(self):
        self.app_id = ESTAT_APP_ID
        self.base_url = ESTAT_BASE_URL
    
    async def get_population_data(self, municipality_code: str) -> Dict:
        """人口データ取得（国勢調査）"""
        if not self.app_id:
            return {"error": "ESTAT_APP_ID not configured"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.base_url}/getStatsData',
                params={
                    'appId': self.app_id,
                    'statsDataId': '0003410379',  # 国勢調査
                    'cdCat01': municipality_code
                },
                timeout=30.0
            )
            return response.json()
    
    async def get_education_data(self, prefecture_code: str) -> Dict:
        """教育データ取得（学校基本調査）"""
        if not self.app_id:
            return {"error": "ESTAT_APP_ID not configured"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.base_url}/getStatsData',
                params={
                    'appId': self.app_id,
                    'statsDataId': '0003431415',  # 学校基本調査
                    'cdCat01': prefecture_code
                },
                timeout=30.0
            )
            return response.json()
    
    async def search_stats(self, keyword: str, limit: int = 10) -> List[Dict]:
        """統計データ検索"""
        if not self.app_id:
            return []
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.base_url}/getStatsList',
                params={
                    'appId': self.app_id,
                    'searchWord': keyword,
                    'limit': limit
                },
                timeout=30.0
            )
            data = response.json()
            return data.get('GET_STATS_LIST', {}).get('DATALIST_INF', {}).get('TABLE_INF', [])
