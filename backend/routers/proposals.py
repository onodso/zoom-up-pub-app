from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from config import settings

router = APIRouter(prefix='/api/proposals', tags=['Proposals'])

class ProposalRequest(BaseModel):
    city_code: str
    focus_area: str = "general" # structural, leadership, etc.

class ProposalResponse(BaseModel):
    city_code: str
    proposal_text: str
    generated_at: str

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

@router.post('/generate', response_model=ProposalResponse)
async def generate_proposal(req: ProposalRequest, conn = Depends(get_db_conn)):
    """
    Generate a sales proposal based on the decision readiness score.
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # 1. Fetch Score & City Info
    cur.execute("""
        SELECT 
            m.city_name, m.prefecture, m.population,
            s.total_score, s.structural_pressure, s.leadership_commitment,
            s.peer_pressure, s.feasibility, s.accountability
        FROM municipalities m
        JOIN decision_readiness_scores s ON m.city_code = s.city_code
        WHERE m.city_code = %s
        ORDER BY s.scored_at DESC
        LIMIT 1
    """, (req.city_code,))
    
    data = cur.fetchone()
    if not data:
        raise HTTPException(status_code=404, detail="Score data not found for valid proposal generation.")
        
    # 2. Construct Prompt for Ollama
    # In a real app, this prompt engineering would be more sophisticated
    prompt = f"""
    You are a top-tier sales strategist for Zoom. Write a short, punchy sales proposal email for the Mayor of {data['city_name']} ({data['prefecture']}).

    Context:
    - Population: {data.get('population', 'Unknown')}
    - Decision Readiness Score: {data['total_score']}/100 (Higher is better for readiness)
    
    Analysis:
    - Structural Pressure (Need): {data['structural_pressure']}/30
    - Leadership Commitment: {data['leadership_commitment']}/25
    - Budget/Feasibility: {data['feasibility']}/15
    
    Focus Area: {req.focus_area}

    The city has a total score of {data['total_score']}. 
    If score is low (<40), focus on "starting small" and "solving immediate pain points".
    If score is high (>70), focus on "advanced innovation" and "becoming a model city".

    Write the email body in Japanese. Keep it under 400 characters.
    """
    
    # 3. Call Ollama using httpx
    import httpx
    from datetime import datetime

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            generated_text = result.get("response", "Error generating text.")

    except Exception as e:
        print(f"Ollama Gen Error: {e}")
        generated_text = "申し訳ありません。AIプロポーザル生成中にエラーが発生しました。既存のテンプレートをご利用ください。"

    return {
        "city_code": req.city_code,
        "proposal_text": generated_text,
        "generated_at": datetime.now().isoformat()
    }
