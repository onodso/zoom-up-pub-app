import os
import httpx
from datetime import datetime
from typing import List, Dict, Optional

class NewsCollector:
    """
    Google Custom Search APIを使用してニュースを収集するクラス
    APIキーがない場合はモックデータを返す
    """
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    async def search_news(self, query: str = "Zoom DX", num: int = 5) -> List[Dict]:
        """
        ニュースを検索する
        """
        # APIキーがない場合はモックデータを返す
        if not self.api_key or not self.engine_id:
            return self._get_mock_news()

        try:
            params = {
                "key": self.api_key,
                "cx": self.engine_id,
                "q": f"{query} site:lg.jp OR site:go.jp", # 自治体・政府ドメインに限定
                "num": num,
                "sort": "date", # 日付順
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params)
                data = response.json()
                
                if "items" not in data:
                    return []

                news_list = []
                for item in data["items"]:
                    news_list.append({
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "snippet": item.get("snippet", ""),
                        "source": item.get("displayLink", ""),
                        "published_at": self._parse_date(item.get("snippet", "")) or datetime.now().isoformat()
                    })
                return news_list

        except Exception as e:
            print(f"Error fetching news: {e}")
            return self._get_mock_news() # エラー時もモックを返す（開発用）

    def _get_mock_news(self) -> List[Dict]:
        """
        開発用のモックデータ
        """
        return [
            {
                "title": "〇〇市、Web会議システム「Zoom」を全庁導入へ",
                "link": "#",
                "snippet": "〇〇市は1日、全職員を対象にWeb会議システム「Zoom」を導入すると発表した。DX推進の一環として...",
                "source": "www.city.mock.lg.jp",
                "published_at": datetime.now().isoformat()
            },
            {
                "title": "令和6年度 XX町 DX推進計画の策定について",
                "link": "#",
                "snippet": "XX町では、行政手続きのオンライン化やオンライン相談窓口の開設を含むDX推進計画を策定しました。",
                "source": "www.town.xx.lg.jp",
                "published_at": datetime.now().isoformat()
            },
            {
                "title": "【入札公告】Web会議用ライセンスの調達",
                "link": "#",
                "snippet": "件名: Web会議用ライセンスの調達 / 期間: 令和6年4月1日から令和7年3月31日まで / 入札方式: ...",
                "source": "www.pref.mock.lg.jp",
                "published_at": datetime.now().isoformat()
            },
             {
                "title": "オンライン窓口の実証実験を開始します",
                "link": "#",
                "snippet": "市民課において、自宅から相談ができるオンライン窓口の実証実験を開始します。",
                "source": "www.city.test.lg.jp",
                "published_at": datetime.now().isoformat()
            }
        ]

    def _parse_date(self, snippet: str) -> Optional[str]:
        # スニペットから日付抽出は困難なため、簡易実装
        # 本番ではGoogleのレスポンスに含まれるpagemapなどから抽出推奨
        return datetime.now().isoformat()
