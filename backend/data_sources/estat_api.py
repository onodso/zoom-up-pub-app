import requests
import sys
from pathlib import Path
import time

# Add to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from backend.config import settings

class EstatAPI:
    def __init__(self):
        self.app_id = settings.ESTAT_APP_ID
        self.base_url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
        
    def get_census_data(self, city_code: str) -> dict:
        """
        Get Population and Elderly data from National Census (2020)
        StatsDataId: 0003410379 (国勢調査 2020)
        """
        if not self.app_id:
            print("⚠️ ESTAT_APP_ID is not set.")
            return {}

        params = {
            "appId": self.app_id,
            "statsDataId": "0003410379",
            "cdArea": city_code
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            return self._parse_census(data)
        except Exception as e:
            print(f"Error fetching Census for {city_code}: {e}")
            return {}

    def get_fiscal_data(self, city_code: str) -> dict:
        """
        Get Fiscal Strength Index (地方財政状況調査)
        StatsDataId: 0003348423
        """
        if not self.app_id:
            return {}
            
        params = {
            "appId": self.app_id,
            "statsDataId": "0003348423",
            "cdArea": city_code
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            return self._parse_fiscal(data)
        except Exception as e:
            print(f"Error fetching Fiscal for {city_code}: {e}")
            return {}

    def _parse_census(self, data: dict) -> dict:
        # Simplified parsing logic (Mock for now as real parsing requires complex JSON traversal)
        # In production, we need to identify specific 'cat01', 'cat02' codes for Total Population and Age 65+
        # This is a placeholder to structure the return
        return {
            "population_2020": 100000, # Mock
            "population_2015": 105000, # Mock
            "age_65_over": 30000,      # Mock
            "total_population": 100000 # Mock
        }

    def _parse_fiscal(self, data: dict) -> dict:
        # Placeholder
        return {
            "fiscal_strength_index": 0.55,
            "real_debt_service_ratio": 12.0,
            "ordinary_balance_ratio": 92.0
        }
