from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from services.news_collector import NewsCollector

router = APIRouter(
    prefix="/api/collector",
    tags=["collector"]
)

class NewsItem(BaseModel):
    title: str
    link: str
    snippet: str
    source: str
    published_at: str

@router.get("/news", response_model=List[NewsItem])
async def get_news(
    keyword: str = Query("Zoom DX", description="検索キーワード"),
    limit: int = Query(5, description="取得件数")
):
    """
    最新のニュースを取得する
    """
    collector = NewsCollector()
    news = await collector.search_news(query=keyword, num=limit)
    return news

@router.post("/run")
async def run_collector_job():
    """
    収集ジョブの手動実行（現在は検索結果を返すだけ）
    """
    collector = NewsCollector()
    # ここでDB保存などの処理を入れる想定
    news = await collector.search_news()
    return {"status": "success", "message": f"Collected {len(news)} items", "data": news}
