import sys
import os
from pathlib import Path
import psycopg2
import time

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from backend.config import settings
from backend.data_sources.estat_api import EstatAPI

def main():
    print("🚀 Starting Census Enrichment...")
    
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
    cur = conn.cursor()
    
    # Get all cities
    cur.execute("SELECT city_code FROM municipalities")
    cities = cur.fetchall()
    
    api = EstatAPI()
    
    count = 0
    for (city_code,) in cities:
        # Rate limit
        time.sleep(0.5) 
        
        data = api.get_census_data(city_code)
        if not data:
            continue
            
        print(f"Processing {city_code}...")
        
        # In a real scenario, we would update the 'municipalities' table or a separate 'stats' table
        # For now, let's assume we update population in municipalities
        cur.execute("""
            UPDATE municipalities 
            SET population = %s,
                updated_at = NOW()
            WHERE city_code = %s
        """, (data.get('population_2020'), city_code))
        
        count += 1
        if count % 10 == 0:
            conn.commit()
            print(f"✅ Committed {count} records")
            
    conn.commit()
    conn.close()
    print("🎉 Enrichment Complete!")

if __name__ == "__main__":
    main()
