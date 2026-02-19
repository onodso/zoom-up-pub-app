import sys
import os
from pathlib import Path
import psycopg2
import time
from typing import List

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))  # Add /app to path
from config import settings
from engines.decision_readiness_scorer import DecisionReadinessScorerV3
from engines.ollama_analyzer import OllamaAnalyzer

# BERTはオプショナル（torch/transformersが未インストールの場合はスキップ）
try:
    from engines.bert_classifier import BertCommitmentClassifier
    BERT_AVAILABLE = True
except ImportError:
    BERT_AVAILABLE = False
    print("⚠️ BERT分類器は利用不可（torch/transformersが未インストール）。Ollamaのみで動作します。")

def main():
    print("🌙 Starting Nightly Scoring Batch...")
    
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
    
    # Initialize Engines
    scorer = DecisionReadinessScorerV3(conn)
    
    # テキスト分析エンジンの初期化
    bert = BertCommitmentClassifier() if BERT_AVAILABLE else None
    ollama = OllamaAnalyzer()
    
    try:
        cur = conn.cursor()
        
        # 1. Select Target Cities (Limit 10 for testing)
        cur.execute("SELECT city_code, city_name, official_url FROM municipalities LIMIT 10")
        targets = cur.fetchall()
        
        print(f"🎯 Processing {len(targets)} municipalities...")
        
        for city_code, city_name, speech_url in targets:
            print(f"   > Scoring {city_name} ({city_code})...")
            
            # 2. Text Collection
            texts = fetch_mayor_speech_text(city_code, speech_url)
            combined_text = " ".join(texts)
            
            # 3. Analyze Text (Real Integration)
            analysis_result = {
                "bert_score": 0,
                "ollama_keywords": [],
                "ollama_score": 0
            }
            
            if combined_text:
                # BERT（利用可能な場合のみ）
                if bert:
                    try:
                        bert_res = bert.predict_commitment(combined_text[:512])
                        analysis_result["bert_score"] = bert_res.get("score", 0)
                    except Exception as e:
                        print(f"     ⚠️ BERT Failed: {e}")
                    
                # Ollama
                try:
                    # In real usage, pass fuller text. 
                    ollama_res = ollama.analyze_mayor_speech(combined_text[:2000])
                    # Map Ollama result to keywords
                    if ollama_res.get("first_person_commitment"):
                        analysis_result["ollama_keywords"].append("first_person")
                    if ollama_res.get("budget_mentioned"):
                        analysis_result["ollama_keywords"].append("budget")
                except Exception as e:
                    print(f"     ⚠️ Ollama Failed: {e}")

            # 4. Score
            result = scorer.score(city_code, analysis_result)
            
            print(f"     ✅ Score: {result.total} (Confidence: {result.confidence})")
            
            # 5. Save (Already done inside scorer.score() in my previous implementation? 
            # No, looking at my previous implementations, I usually separate save.
            # Let's check DecisionReadinessScorerV3 source.
            # Ah, I see I didn't implement 'save_to_db' inside the 'score' method in the python file I wrote in Step 1921.
            # I returned the object. So I need to save it here.
            
            save_score(conn, result)
            
            time.sleep(0.1)
            
        conn.commit()
        print("✅ Batch Completed Successfully.")
        
    except Exception as e:
        print(f"❌ Batch Failed: {e}")
        conn.rollback()
    finally:
        conn.close()

def fetch_mayor_speech_text(city_code: str, url: str) -> List[str]:
    """
    Mock function to fetch text. 
    In Stage 2, this will be a real scraper.
    """
    # Return dummy text that triggers some points
    if not url:
        return [""]
        
    return [
        "私は、デジタル・トランスフォーメーション（DX）を強力に推進します。",
        "補正予算にて5億円を計上し、全庁的な改革を行います。"
    ]

def save_score(conn, result):
    """
    Save the score to DB.
    """
    cur = conn.cursor()
    
    # Simple Update/Insert (total_score is auto-generated)
    query = """
        INSERT INTO decision_readiness_scores
        (city_code, structural_pressure, leadership_commitment, peer_pressure,
         feasibility, accountability, confidence_level, scored_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (city_code, ((scored_at)::DATE)) DO UPDATE SET
            structural_pressure = EXCLUDED.structural_pressure,
            leadership_commitment = EXCLUDED.leadership_commitment,
            peer_pressure = EXCLUDED.peer_pressure,
            feasibility = EXCLUDED.feasibility,
            accountability = EXCLUDED.accountability,
            confidence_level = EXCLUDED.confidence_level
    """

    cur.execute(query, (
        result.city_code,
        result.structural_pressure,
        result.leadership_commitment,
        result.peer_pressure,
        result.feasibility,
        result.accountability,
        result.confidence
    ))

if __name__ == "__main__":
    main()
