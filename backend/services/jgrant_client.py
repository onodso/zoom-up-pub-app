"""
J-Grant MCP クライアント（補正予算データ取得）
"""
import os
import httpx
from typing import List, Dict

JGRANT_API_KEY = os.getenv('JGRANT_API_KEY', '')
JGRANT_BASE_URL = 'https://info.gbiz.go.jp/hojin/v1'


class JGrantClient:
    def __init__(self):
        self.api_key = JGRANT_API_KEY
        self.base_url = JGRANT_BASE_URL
    
    async def search_subsidies(
        self, 
        municipality_code: str,
        fiscal_year: int = 2024
    ) -> List[Dict]:
        """自治体向け補助金・交付金検索"""
        if not self.api_key:
            return []
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.base_url}/subsidy',
                headers={'X-hojinInfo-api-token': self.api_key},
                params={
                    'prefecture': municipality_code[:2],
                    'fiscal_year': fiscal_year,
                    'target': '地方公共団体'
                },
                timeout=30.0
            )
            return response.json().get('subsidies', [])
    
    async def get_subsidy_detail(self, subsidy_id: str) -> Dict:
        """補助金詳細取得"""
        if not self.api_key:
            return {"error": "JGRANT_API_KEY not configured"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.base_url}/subsidy/{subsidy_id}',
                headers={'X-hojinInfo-api-token': self.api_key},
                timeout=30.0
            )
            return response.json()
