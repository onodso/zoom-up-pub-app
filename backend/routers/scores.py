"""
スコアAPI
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix='/api/scores', tags=['スコア'])


class PrefectureScore(BaseModel):
    prefecture_code: str
    prefecture_name: str
    avg_score: float
    municipality_count: int


class MunicipalityScore(BaseModel):
    municipality_code: str
    municipality_name: str
    prefecture: str
    score_total: float
    score_dx_maturity: float
    score_online_procedures: float
    score_budget_match: float
    score_news_sentiment: float


# 都道府県別スコア（仮データ）
PREFECTURE_SCORES = {
    "13": {"code": "13", "name": "東京都", "avg_score": 82.5, "count": 62},
    "14": {"code": "14", "name": "神奈川県", "avg_score": 78.3, "count": 33},
    "23": {"code": "23", "name": "愛知県", "avg_score": 75.2, "count": 54},
    "27": {"code": "27", "name": "大阪府", "avg_score": 76.8, "count": 43},
    "01": {"code": "01", "name": "北海道", "avg_score": 65.4, "count": 179},
    "40": {"code": "40", "name": "福岡県", "avg_score": 72.1, "count": 60},
}


@router.get('/by-prefecture')
async def get_scores_by_prefecture():
    """都道府県別スコア取得（地図表示用）"""
    return {
        code: {
            "prefecture_code": data["code"],
            "prefecture_name": data["name"],
            "avg_score": data["avg_score"],
            "municipality_count": data["count"]
        }
        for code, data in PREFECTURE_SCORES.items()
    }


@router.get('/ranking')
async def get_score_ranking(
    region: Optional[str] = Query(None, description="地方名フィルター"),
    limit: int = Query(20, ge=1, le=100)
):
    """スコアランキング取得"""
    # 仮データ
    ranking = [
        {"rank": 1, "code": "131130", "name": "渋谷区", "prefecture": "東京都", "score": 85.5},
        {"rank": 2, "code": "131016", "name": "千代田区", "prefecture": "東京都", "score": 84.2},
        {"rank": 3, "code": "141003", "name": "横浜市", "prefecture": "神奈川県", "score": 82.0},
        {"rank": 4, "code": "271004", "name": "大阪市", "prefecture": "大阪府", "score": 80.3},
        {"rank": 5, "code": "131181", "name": "世田谷区", "prefecture": "東京都", "score": 78.2},
    ]
    return ranking[:limit]


@router.get('/stats')
async def get_score_stats():
    """スコア統計情報取得"""
    return {
        "total_municipalities": 1741,
        "average_score": 68.5,
        "max_score": 92.3,
        "min_score": 32.1,
        "score_distribution": {
            "80-100": 156,
            "60-80": 523,
            "40-60": 789,
            "20-40": 245,
            "0-20": 28
        }
    }
