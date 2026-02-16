import sys
from pathlib import Path
import psycopg2

sys.path.append(str(Path(__file__).parent.parent.parent))
from backend.config import settings

def main():
    print("🚀 Starting Migration to add Stat columns...")
    
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
    cur = conn.cursor()
    
    try:
        # Add columns if not exist
        columns = [
            ("population_decline_rate", "FLOAT"),
            ("elderly_ratio", "FLOAT"),
            ("fiscal_index", "FLOAT"),
            ("staff_reduction_rate", "FLOAT"),
            ("dx_status", "JSONB") # Ensure this exists too as I used it in enrich_dx_progress
        ]
        
        for col, dtype in columns:
            print(f"Checking column {col}...")
            cur.execute(f"ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS {col} {dtype};")
            
        conn.commit()
        print("✅ Migration Completed.")
        
    except Exception as e:
        print(f"❌ Migration Failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
