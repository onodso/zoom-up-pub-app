import sys
import os
from pathlib import Path
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from backend.config import settings

def main():
    print("🚀 Starting DX Progress Enrichment...")
    
    # Check CSV
    csv_path = Path("data/dx_progress.csv")
    if not csv_path.exists():
        print(f"⚠️ CSV not found: {csv_path}")
        print("Please place the Digital Agency 'Status of Municipality DX Promotion' CSV at data/dx_progress.csv")
        return

    print(f"📖 Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Expected columns mapping (Adjust based on actual CSV header)
    # Assumed headers: '団体コード', 'DX推進組織', 'CIO設置', '外部CIO', '情報専門人材', 'ガバメントクラウド', 'LGWAN'
    col_map = {
        'code': '団体コード',
        'dept': 'DX推進組織',
        'cio': 'CIO設置',
        'ext_cio': '外部CIO',
        'staff': '情報専門人材',
        'cloud': 'ガバメントクラウド',
        'lgwan': 'LGWAN'
    }
    
    # Validate headers (Soft check)
    if col_map['code'] not in df.columns:
        print(f"❌ Missing column: {col_map['code']}")
        return

    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
    cur = conn.cursor()
    
    # We will store this data in a JSONB column or separate table? 
    # For now, let's assume we might need to alter 'municipalities' to verify this data, 
    # OR we use this data to PRE-CALCULATE part of "score" and insert into 'decision_readiness_scores'
    # BUT Stage 0 goal is just "Import".
    # Let's assume we have a 'dx_status' JSONB column in 'municipalities' OR we just save it for Stage 1.
    # Wait, the SCHEMA I created for 'municipalities' does not have 'dx_status'.
    # I should ALERT the user or ALTER the table.
    # For now, I will ALTER the table here to add a storage column.
    
    print("🔧 Altering table to store DX data...")
    cur.execute("ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS dx_status JSONB;")
    conn.commit()
    
    print("💾 Updating municipalities...")
    
    update_query = """
        UPDATE municipalities 
        SET dx_status = %s,
            updated_at = NOW()
        WHERE city_code = %s
    """
    
    count = 0
    for _, row in df.iterrows():
        city_code = str(row[col_map['code']]).zfill(6) # Ensure 6 digits
        
        dx_data = {
            "dept": row.get(col_map['dept']),
            "cio": row.get(col_map['cio']),
            "ext_cio": row.get(col_map['ext_cio']),
            "staff": row.get(col_map['staff']),
            "cloud": row.get(col_map['cloud']),
            "lgwan": row.get(col_map['lgwan'])
        }
        
        # JSON dump via psycopg2 automatic adaptation? No, needed json.dumps or Json adapter
        from psycopg2.extras import Json
        
        cur.execute(update_query, (Json(dx_data), city_code))
        
        count += 1
        if count % 100 == 0:
            print(f"Processed {count}...")
            
    conn.commit()
    conn.close()
    print(f"✅ Successfully enriched {count} municipalities with DX data.")

if __name__ == "__main__":
    main()
