from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.municipality import Municipality as DbMunicipality
from pydantic import BaseModel

class MunicipalityResponse(BaseModel):
    id: int
    code: str
    prefecture: str
    name: str
    region: str
    population: int
    households: int
    mayor_name: Optional[str] = None
    official_url: Optional[str] = None

    class Config:
        from_attributes = True

class MunicipalityDetailResponse(MunicipalityResponse):
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    score_total: Optional[float] = None
    created_at: datetime
    updated_at: datetime

router = APIRouter(prefix='/api/municipalities', tags=['自治体'])

@router.get('/', response_model=List[MunicipalityResponse])
async def list_municipalities(
    region: Optional[str] = Query(None, description="地方名フィルター"),
    prefecture: Optional[str] = Query(None, description="都道府県名フィルター"),
    search: Optional[str] = Query(None, description="検索キーワード"),
    limit: int = Query(50, ge=1, le=1000), # 全件表示したいニーズに対応してlimit上限UP
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """自治体一覧取得"""
    query = db.query(DbMunicipality)
    
    if region:
        query = query.filter(DbMunicipality.region == region)
    if prefecture:
        query = query.filter(DbMunicipality.prefecture == prefecture)
    if search:
        query = query.filter(
            (DbMunicipality.name.contains(search)) | 
            (DbMunicipality.prefecture.contains(search))
        )
    
    query = query.order_by(DbMunicipality.code)
    return query.offset(offset).limit(limit).all()

@router.get('/{code}', response_model=MunicipalityDetailResponse)
async def get_municipality(code: str, db: Session = Depends(get_db)):
    """自治体詳細取得"""
    municipality = db.query(DbMunicipality).filter(DbMunicipality.code == code).first()
    if not municipality:
        raise HTTPException(status_code=404, detail="自治体が見つかりません")
    return municipality

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
async def list_prefectures(db: Session = Depends(get_db)):
    """都道府県一覧取得 (DBから取得するように変更も可能だが、固定リストの方が軽い)"""
    # ... 固定リスト実装のまま ...
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
