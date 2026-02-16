from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from datetime import datetime

from config import settings

def get_db_conn():
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
    try:
        yield conn
    finally:
        conn.close()

class MunicipalityResponse(BaseModel):
    city_code: str
    prefecture: str
    city_name: str
    city_type: Optional[str] = None
    region: Optional[str] = None
    population: Optional[int] = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    official_url: Optional[str] = None
    # dx_status: Optional[dict] = None

class MunicipalityDetailResponse(MunicipalityResponse):
    dx_status: Optional[dict] = None
    updated_at: Optional[datetime] = None

router = APIRouter(prefix='/api/municipalities', tags=['Municipalities'])

@router.get('/', response_model=List[MunicipalityResponse])
async def list_municipalities(
    region: Optional[str] = Query(None, description="Region Filter"),
    prefecture: Optional[str] = Query(None, description="Prefecture Filter"),
    search: Optional[str] = Query(None, description="Search Keyword"),
    limit: int = Query(50, ge=1, le=2000), 
    offset: int = Query(0, ge=0),
    conn = Depends(get_db_conn)
):
    """List municipalities with filters"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    query = "SELECT city_code, prefecture, city_name, city_type, region, population, NULL as latitude, NULL as longitude, official_url FROM municipalities WHERE 1=1"
    params = []
    
    if region:
        query += " AND region = %s"
        params.append(region)
    if prefecture:
        query += " AND prefecture = %s"
        params.append(prefecture)
    if search:
        query += " AND (city_name LIKE %s OR prefecture LIKE %s)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")
        
    query += " ORDER BY city_code LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    cur.execute(query, params)
    return cur.fetchall()

@router.get('/{city_code}', response_model=MunicipalityDetailResponse)
async def get_municipality(city_code: str, conn = Depends(get_db_conn)):
    """Get municipality details"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM municipalities WHERE city_code = %s", (city_code,))
    result = cur.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Municipality not found")
        
    return result

@router.get('/lists/regions')
async def list_regions():
    return [
        {"id": "hokkaido", "name": "北海道/東北", "prefs": ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県"]},
        {"id": "kanto", "name": "関東", "prefs": ["茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県"]},
        {"id": "chubu", "name": "中部", "prefs": ["新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県"]},
        {"id": "kinki", "name": "近畿", "prefs": ["三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県"]},
        {"id": "chugoku_shikoku", "name": "中国/四国", "prefs": ["鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県"]},
        {"id": "kyushu", "name": "九州/沖縄", "prefs": ["福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]}
    ]
