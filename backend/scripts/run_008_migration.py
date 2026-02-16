import sys
from pathlib import Path
import psycopg2

sys.path.append(str(Path(__file__).parent.parent.parent))
from backend.config import settings

def main():
    print("🚀 Running Migration 008 (Schema Unification)...")
    
    sql_path = Path("backend/db/migrations/008_finalize_decision_readiness.sql")
    if not sql_path.exists():
        print(f"❌ SQL file not found: {sql_path}")
        return

    sql_content = sql_path.read_text()
    
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
    cur = conn.cursor()
    
    try:
        cur.execute(sql_content)
        conn.commit()
        print("✅ Migration 008 Completed Successfully.")
        
        # Verify Columns
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'municipalities' 
            AND column_name IN ('population_decline_rate', 'elderly_ratio', 'dx_status', 'staff_reduction_rate')
        """)
        cols = [r[0] for r in cur.fetchall()]
        print(f"🔎 Verified Columns in 'municipalities': {cols}")
        
        # Verify Table
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('decision_readiness_scores', 'scores', 'scores_deprecated_v2')
        """)
        tables = [r[0] for r in cur.fetchall()]
        print(f"🔎 Verified Tables: {tables}")
        
    except Exception as e:
        print(f"❌ Migration Failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
