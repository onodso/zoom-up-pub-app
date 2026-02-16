import sys
import os
from pathlib import Path
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Add backend to path to import config
sys.path.append(str(Path(__file__).parent.parent.parent))
from backend.config import settings

def main():
    csv_path = Path("data/localgov_master_integrated.csv")
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        return

    print(f"🔄 Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Validation
    # Updated to match integrated CSV headers: lgcode, pref, city, lat, lng
    required_cols = ['lgcode', 'pref', 'city', 'lat', 'lng']
    for col in required_cols:
        if col not in df.columns:
            print(f"❌ Missing column: {col}")
            return

    print(f"🔌 Connecting to DB {settings.DB_HOST}...")
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        cur = conn.cursor()
        
        # Upsert Method
        insert_query = """
            INSERT INTO municipalities 
            (city_code, prefecture, city_name, region, city_type, latitude, longitude, official_url)
            VALUES %s
            ON CONFLICT (city_code) DO UPDATE SET
                prefecture = EXCLUDED.prefecture,
                city_name = EXCLUDED.city_name,
                region = EXCLUDED.region,
                city_type = EXCLUDED.city_type,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                official_url = EXCLUDED.official_url,
                updated_at = NOW()
        """
        
        data_tuples = []
        for _, row in df.iterrows():
            official_url = row.get('url', None)
            city_name = row['city']
            
            # Simple city type detection if not present
            city_type = row.get('city_type') 
            # In integrated CSV, it might not exist, infer from name
            if pd.isna(city_type) or not city_type:
                if '市' in city_name: city_type = '市'
                elif '区' in city_name: city_type = '区'
                elif '町' in city_name: city_type = '町'
                elif '村' in city_name: city_type = '村'
            
            
            # Region Inference
            region_map = {
                "北海道": "北海道",
                "青森県": "東北", "岩手県": "東北", "宮城県": "東北", "秋田県": "東北", "山形県": "東北", "福島県": "東北",
                "茨城県": "関東", "栃木県": "関東", "群馬県": "関東", "埼玉県": "関東", "千葉県": "関東", "東京都": "関東", "神奈川県": "関東",
                "新潟県": "中部", "富山県": "中部", "石川県": "中部", "福井県": "中部", "山梨県": "中部", "長野県": "中部", "岐阜県": "中部", "静岡県": "中部", "愛知県": "中部",
                "三重県": "近畿", "滋賀県": "近畿", "京都府": "近畿", "大阪府": "近畿", "兵庫県": "近畿", "奈良県": "近畿", "和歌山県": "近畿",
                "鳥取県": "中国", "島根県": "中国", "岡山県": "中国", "広島県": "中国", "山口県": "中国",
                "徳島県": "四国", "香川県": "四国", "愛媛県": "四国", "高知県": "四国",
                "福岡県": "九州", "佐賀県": "九州", "長崎県": "九州", "熊本県": "九州", "大分県": "九州", "宮崎県": "九州", "鹿児島県": "九州", "沖縄県": "沖縄"
            }
            region = region_map.get(row['pref'], "その他")

            data_tuples.append((
                str(row['lgcode']).zfill(6), # lgcode to city_code
                row['pref'],      # pref to prefecture
                city_name,        # city to city_name
                region,
                city_type,
                row['lat'],
                row['lng'],
                official_url
            ))
            
        execute_values(cur, insert_query, data_tuples)
        conn.commit()
        print(f"✅ Successfully imported {len(data_tuples)} municipalities.")
        
    except Exception as e:
        print(f"❌ DB Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    main()
