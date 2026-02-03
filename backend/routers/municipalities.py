"""
自治体API
"""
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix='/api/municipalities', tags=['自治体'])


class Municipality(BaseModel):
    id: int
    code: str
    prefecture: str
    name: str
    region: str
    population: int = 0
    households: int = 0
    mayor_name: Optional[str] = None
    official_url: Optional[str] = None


class MunicipalityDetail(Municipality):
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    score_total: Optional[float] = None
    created_at: datetime
    updated_at: datetime


# 仮の自治体データ（本番ではDB接続）
# パフォーマンス改善: datetime.now() を定数として1回だけ呼び出す
_MOCK_TIMESTAMP = datetime.now()

MOCK_MUNICIPALITIES = [
    {
        "id": 1, "code": "131130", "prefecture": "東京都", "name": "渋谷区",
        "region": "関東", "population": 229000, "households": 132000,
        "mayor_name": "長谷部健", "official_url": "https://www.city.shibuya.tokyo.jp",
        "score_total": 85.5, "created_at": _MOCK_TIMESTAMP, "updated_at": _MOCK_TIMESTAMP
    },
    {
        "id": 2, "code": "131181", "prefecture": "東京都", "name": "世田谷区",
        "region": "関東", "population": 917000, "households": 472000,
        "mayor_name": "保坂展人", "official_url": "https://www.city.setagaya.lg.jp",
        "score_total": 78.2, "created_at": _MOCK_TIMESTAMP, "updated_at": _MOCK_TIMESTAMP
    },
    {
        "id": 3, "code": "141003", "prefecture": "神奈川県", "name": "横浜市",
        "region": "関東", "population": 3749000, "households": 1740000,
        "mayor_name": "山中竹春", "official_url": "https://www.city.yokohama.lg.jp",
        "score_total": 82.0, "created_at": _MOCK_TIMESTAMP, "updated_at": _MOCK_TIMESTAMP
    },
    {
        "id": 4, "code": "231002", "prefecture": "愛知県", "name": "名古屋市",
        "region": "中部", "population": 2320000, "households": 1100000,
        "mayor_name": "河村たかし", "official_url": "https://www.city.nagoya.jp",
        "score_total": 75.8, "created_at": _MOCK_TIMESTAMP, "updated_at": _MOCK_TIMESTAMP
    },
    {
        "id": 5, "code": "271004", "prefecture": "大阪府", "name": "大阪市",
        "region": "近畿", "population": 2750000, "households": 1460000,
        "mayor_name": "横山英幸", "official_url": "https://www.city.osaka.lg.jp",
        "score_total": 80.3, "created_at": _MOCK_TIMESTAMP, "updated_at": _MOCK_TIMESTAMP
    },
]


@router.get('/', response_model=list[Municipality])
async def list_municipalities(
    region: Optional[str] = Query(None, description="地方名フィルター"),
    prefecture: Optional[str] = Query(None, description="都道府県名フィルター"),
    search: Optional[str] = Query(None, description="検索キーワード"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """自治体一覧取得"""
    result = MOCK_MUNICIPALITIES
    
    if region:
        result = [m for m in result if m["region"] == region]
    if prefecture:
        result = [m for m in result if m["prefecture"] == prefecture]
    if search:
        result = [m for m in result if search in m["name"] or search in m["prefecture"]]
    
    return result[offset:offset + limit]


@router.get('/{code}', response_model=MunicipalityDetail)
async def get_municipality(code: str):
    """自治体詳細取得"""
    for m in MOCK_MUNICIPALITIES:
        if m["code"] == code:
            return m
    raise HTTPException(status_code=404, detail="自治体が見つかりません")


@router.get('/regions/list')
async def list_regions():
    """地方一覧取得"""
    return [
        {"id": "hokkaido", "name": "北海道"},
        {"id": "tohoku", "name": "東北"},
        {"id": "kanto", "name": "関東"},
        {"id": "chubu", "name": "中部"},
        {"id": "kinki", "name": "近畿"},
        {"id": "chugoku", "name": "中国"},
        {"id": "shikoku", "name": "四国"},
        {"id": "kyushu", "name": "九州"}
    ]


@router.get('/prefectures/list')
async def list_prefectures():
    """都道府県一覧取得"""
    prefectures = [
        "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
        "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
        "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
        "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
        "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
        "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
        "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
    ]
    return [{"id": i+1, "name": p} for i, p in enumerate(prefectures)]
