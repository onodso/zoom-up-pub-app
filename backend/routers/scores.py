"""
Decision Readiness Score API
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from datetime import datetime

# Use the config to get connection parameters
# Or use a dependency if you have one. For now, creating a simple dependency.
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

router = APIRouter(prefix='/api/scores', tags=['Scores'])

class ScoreDetails(BaseModel):
    structural: dict
    leadership: dict
    peer: dict
    feasibility: dict
    accountability: dict

class DecisionScoreResponse(BaseModel):
    city_code: str
    city_name: str
    prefecture: str
    total_score: int
    confidence_level: str
    scored_at: datetime
    # 5 Pillars
    structural_pressure: int
    leadership_commitment: int
    peer_pressure: int
    feasibility: int
    accountability: int
    
    evidence_urls: Optional[List[str]] = []
    signal_keywords: Optional[List[str]] = []
    
    # Optional breakdown if stored
    # breakdown: Optional[ScoreDetails]

@router.get('/{city_code}', response_model=DecisionScoreResponse)
async def get_score(city_code: str, conn = Depends(get_db_conn)):
    """
    Get the latest Decision Readiness Score for a municipality.
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
        SELECT 
            m.city_code, m.city_name, m.prefecture,
            s.total_score, s.confidence_level, s.scored_at,
            s.structural_pressure, s.leadership_commitment,
            s.peer_pressure, s.feasibility, s.accountability,
            s.evidence_urls, s.signal_keywords
        FROM decision_readiness_scores s
        JOIN municipalities m ON s.city_code = m.city_code
        WHERE m.city_code = %s
        ORDER BY s.scored_at DESC
        LIMIT 1
    """
    
    cur.execute(query, (city_code,))
    result = cur.fetchone()
    
    if not result:
        # Check if municipality exists
        cur.execute("SELECT city_name FROM municipalities WHERE city_code = %s", (city_code,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Municipality not found")
        raise HTTPException(status_code=404, detail="Score not yet calculated for this municipality")
        
    return result

@router.get('/ranking/{prefecture}', response_model=List[DecisionScoreResponse])
async def get_prefecture_ranking(prefecture: str, conn = Depends(get_db_conn)):
    """
    Get scores for all municipalities in a prefecture.
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
        SELECT 
            m.city_code, m.city_name, m.prefecture,
            COALESCE(s.total_score, 0) as total_score,
            COALESCE(s.confidence_level, 'unknown') as confidence_level,
            COALESCE(s.scored_at, NOW()) as scored_at,
            COALESCE(s.structural_pressure, 0) as structural_pressure,
            COALESCE(s.leadership_commitment, 0) as leadership_commitment,
            COALESCE(s.peer_pressure, 0) as peer_pressure,
            COALESCE(s.feasibility, 0) as feasibility,
            COALESCE(s.accountability, 0) as accountability
        FROM municipalities m
        LEFT JOIN decision_readiness_scores s ON m.city_code = s.city_code
        WHERE m.prefecture = %s
        ORDER BY s.total_score DESC NULLS LAST
    """
    
    cur.execute(query, (prefecture,))
    results = cur.fetchall()
    
    return results

@router.get('/map/all')
async def get_map_data(conn = Depends(get_db_conn)):
    """
    Get lightweight data for all municipalities for map visualization.
    Returns: list of {city_code, lat, lon, score, confidence}
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)
    # Query for latest score (lat/lon optional for now)
    query = """
        SELECT DISTINCT ON (m.city_code)
            m.city_code,
            m.prefecture,
            m.city_name,
            NULL::double precision as latitude,
            NULL::double precision as longitude,
            COALESCE(s.total_score, 0) as total_score,
            COALESCE(s.confidence_level, 'unknown') as confidence
        FROM municipalities m
        LEFT JOIN decision_readiness_scores s ON m.city_code = s.city_code
        ORDER BY m.city_code, s.scored_at DESC NULLS LAST
    """
    
    cur.execute(query)
    results = cur.fetchall()
    return results

# Batch Trigger
from typing import List
from pydantic import BaseModel

class BatchRequest(BaseModel):
    city_codes: Optional[List[str]] = None

@router.post('/batch', status_code=202)
async def trigger_batch_scoring(req: BatchRequest, conn = Depends(get_db_conn)):
    """
    Trigger the scoring batch process.
    In production, this should launch a background task (Celery/RQ).
    Here we use subprocess for simplicity in MVP.
    """
    import subprocess
    import sys
    
    # Launch detached process
    # Note: simple Popen might be killed if main process dies, but sufficient for demo.
    cmd = [sys.executable, "backend/scripts/nightly_scoring.py"]
    subprocess.Popen(cmd)
    
    return {"status": "accepted", "message": "Batch scoring initiated in background"}
