"""
Nightly Scoring Batch (Lite Version - No AI)
AI Engines をスキップして、DBデータのみでスコアリングを実行
"""
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

def main():
    print("🌙 Starting Nightly Scoring Batch (Lite Mode - No AI)...")

    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )

    # Initialize Engines
    scorer = DecisionReadinessScorerV3(conn)

    # NOTE: BERT/Ollama engines are skipped in lite mode
    print("   ⚠️ Running in LITE MODE (AI Engines disabled)")

    try:
        cur = conn.cursor()

        # 1. Select Target Cities
        # Select cities with enriched data (not requiring lat/lon)
        cur.execute("""
            SELECT city_code, city_name
            FROM municipalities
            WHERE population_decline_rate IS NOT NULL
            ORDER BY population DESC NULLS LAST
            -- LIMIT 2000  -- All municipalities
        """)
        targets = cur.fetchall()

        print(f"🎯 Processing {len(targets)} municipalities...")

        success_count = 0
        error_count = 0

        for city_code, city_name in targets:
            print(f"   > Scoring {city_name} ({city_code})...")

            try:
                # 3. Empty analysis_result (No AI)
                analysis_result = {
                    "bert_score": 0,
                    "ollama_keywords": [],
                    "ollama_score": 0
                }

                # 4. Score
                result = scorer.score(city_code, analysis_result)

                print(f"     ✅ Score: {result.total}/100 (Confidence: {result.confidence})")
                print(f"        - Structural: {result.structural_pressure}/30")
                print(f"        - Leadership: {result.leadership_commitment}/25 (⚠️ No AI)")
                print(f"        - Peer: {result.peer_pressure}/20")
                print(f"        - Feasibility: {result.feasibility}/15")
                print(f"        - Accountability: {result.accountability}/10")

                # 5. Save
                save_score(conn, result)
                success_count += 1

            except Exception as e:
                print(f"     ❌ Error scoring {city_name}: {e}")
                error_count += 1
                continue

            time.sleep(0.1)

        conn.commit()
        print(f"\n✅ Batch Completed Successfully.")
        print(f"   📊 Success: {success_count}, Errors: {error_count}")

    except Exception as e:
        print(f"❌ Batch Failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

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
