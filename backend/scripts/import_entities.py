"""
import_entities.py — Entities統一モデルへのデータ投入

1,835ノードを統一管理:
- 市区町村 (1,741件) <- municipalities テーブルから
- 都道府県 (47件) <- 新規作成
- 教育委員会 (47件) <- 新規作成
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# models と database をインポート
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.entities import Entity, Base
from models.municipality import Municipality
from database import SQLALCHEMY_DATABASE_URL

# 都道府県マスタ（47件）
PREFECTURES = [
    {"code": "01", "name": "北海道", "lat": 43.0642, "lng": 141.3469},
    {"code": "02", "name": "青森県", "lat": 40.8244, "lng": 140.7400},
    {"code": "03", "name": "岩手県", "lat": 39.7036, "lng": 141.1527},
    {"code": "04", "name": "宮城県", "lat": 38.2682, "lng": 140.8720},
    {"code": "05", "name": "秋田県", "lat": 39.7186, "lng": 140.1024},
    {"code": "06", "name": "山形県", "lat": 38.2404, "lng": 140.3633},
    {"code": "07", "name": "福島県", "lat": 37.7503, "lng": 140.4676},
    {"code": "08", "name": "茨城県", "lat": 36.3418, "lng": 140.4468},
    {"code": "09", "name": "栃木県", "lat": 36.5658, "lng": 139.8836},
    {"code": "10", "name": "群馬県", "lat": 36.3911, "lng": 139.0608},
    {"code": "11", "name": "埼玉県", "lat": 35.8569, "lng": 139.6489},
    {"code": "12", "name": "千葉県", "lat": 35.6047, "lng": 140.1233},
    {"code": "13", "name": "東京都", "lat": 35.6895, "lng": 139.6917},
    {"code": "14", "name": "神奈川県", "lat": 35.4478, "lng": 139.6425},
    {"code": "15", "name": "新潟県", "lat": 37.9026, "lng": 139.0235},
    {"code": "16", "name": "富山県", "lat": 36.6953, "lng": 137.2113},
    {"code": "17", "name": "石川県", "lat": 36.5946, "lng": 136.6256},
    {"code": "18", "name": "福井県", "lat": 36.0652, "lng": 136.2217},
    {"code": "19", "name": "山梨県", "lat": 35.6642, "lng": 138.5684},
    {"code": "20", "name": "長野県", "lat": 36.6513, "lng": 138.1810},
    {"code": "21", "name": "岐阜県", "lat": 35.3912, "lng": 136.7222},
    {"code": "22", "name": "静岡県", "lat": 34.9769, "lng": 138.3831},
    {"code": "23", "name": "愛知県", "lat": 35.1802, "lng": 136.9066},
    {"code": "24", "name": "三重県", "lat": 34.7303, "lng": 136.5086},
    {"code": "25", "name": "滋賀県", "lat": 35.0045, "lng": 135.8686},
    {"code": "26", "name": "京都府", "lat": 35.0211, "lng": 135.7556},
    {"code": "27", "name": "大阪府", "lat": 34.6863, "lng": 135.5200},
    {"code": "28", "name": "兵庫県", "lat": 34.6913, "lng": 135.1830},
    {"code": "29", "name": "奈良県", "lat": 34.6851, "lng": 135.8329},
    {"code": "30", "name": "和歌山県", "lat": 34.2261, "lng": 135.1675},
    {"code": "31", "name": "鳥取県", "lat": 35.5014, "lng": 134.2381},
    {"code": "32", "name": "島根県", "lat": 35.4723, "lng": 133.0505},
    {"code": "33", "name": "岡山県", "lat": 34.6618, "lng": 133.9349},
    {"code": "34", "name": "広島県", "lat": 34.3965, "lng": 132.4596},
    {"code": "35", "name": "山口県", "lat": 34.1860, "lng": 131.4714},
    {"code": "36", "name": "徳島県", "lat": 34.0658, "lng": 134.5595},
    {"code": "37", "name": "香川県", "lat": 34.3402, "lng": 134.0434},
    {"code": "38", "name": "愛媛県", "lat": 33.8416, "lng": 132.7657},
    {"code": "39", "name": "高知県", "lat": 33.5597, "lng": 133.5311},
    {"code": "40", "name": "福岡県", "lat": 33.6064, "lng": 130.4183},
    {"code": "41", "name": "佐賀県", "lat": 33.2495, "lng": 130.2988},
    {"code": "42", "name": "長崎県", "lat": 32.7503, "lng": 129.8779},
    {"code": "43", "name": "熊本県", "lat": 32.7898, "lng": 130.7417},
    {"code": "44", "name": "大分県", "lat": 33.2382, "lng": 131.6126},
    {"code": "45", "name": "宮崎県", "lat": 31.9111, "lng": 131.4239},
    {"code": "46", "name": "鹿児島県", "lat": 31.5602, "lng": 130.5581},
    {"code": "47", "name": "沖縄県", "lat": 26.2124, "lng": 127.6809}
]


def main():
    print("🚀 Entities統一モデルへのデータ投入開始")
    
    # DB接続
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 1. 市区町村 (1,741件) を municipalities から読み込み
        print("\n📍 Step 1: 市区町村データの投入...")
        municipalities = session.query(Municipality).all()
        municipality_count = 0
        skipped_count = 0
        
        for muni in municipalities:
            # 政令市の区を除外（東京23区のみ許可）
            # 理由: 大阪市・札幌市などは区単位で教育委員会や意思決定が分かれていない
            if '区' in muni.name and muni.prefecture != '東京都':
                skipped_count += 1
                continue
            
            entity = Entity(
                entity_id=f"M{muni.code}",
                name=muni.name,
                entity_type="municipality",
                prefecture_code=muni.code[:2],  # 最初の2桁が都道府県コード
                latitude=muni.latitude,
                longitude=muni.longitude,
                population=muni.population,
                fiscal_index=muni.fiscal_index,
                official_url=muni.official_url,
                activity_index=0.0  # 初期値
            )
            session.add(entity)
            municipality_count += 1
        
        session.commit()
        print(f"   ✅ {municipality_count}件の市区町村を投入")
        print(f"   ⏭️  {skipped_count}件の政令市区をスキップ（東京23区以外）")
        
        # 2. 都道府県 (47件) を新規作成
        print("\n🏛️  Step 2: 都道府県データの投入...")
        prefecture_count = 0
        
        for pref in PREFECTURES:
            entity = Entity(
                entity_id=f"P{pref['code']}",
                name=pref['name'],
                entity_type="prefecture",
                prefecture_code=pref['code'],
                latitude=pref['lat'],
                longitude=pref['lng'],
                population=None,  # 都道府県レベルの人口は将来的に追加
                fiscal_index=None,
                official_url=None,
                activity_index=0.0
            )
            session.add(entity)
            prefecture_count += 1
        
        session.commit()
        print(f"   ✅ {prefecture_count}件の都道府県を投入")
        
        # 3. 教育委員会 (47件) を新規作成
        print("\n🎓 Step 3: 教育委員会データの投入...")
        education_count = 0
        
        for pref in PREFECTURES:
            entity = Entity(
                entity_id=f"E{pref['code']}",
                name=f"{pref['name']}教育委員会",
                entity_type="education_board",
                prefecture_code=pref['code'],
                latitude=pref['lat'],
                longitude=pref['lng'],
                population=None,
                fiscal_index=None,
                official_url=None,
                activity_index=0.0
            )
            session.add(entity)
            education_count += 1
        
        session.commit()
        print(f"   ✅ {education_count}件の教育委員会を投入")
        
        # 検証
        from sqlalchemy import text
        print("\n📊 検証結果:")
        total = session.query(Entity).count()
        by_type = session.execute(text("""
            SELECT entity_type, COUNT(*) as count
            FROM entities
            GROUP BY entity_type
            ORDER BY entity_type
        """)).fetchall()
        
        print(f"   合計: {total}件")
        for row in by_type:
            print(f"   - {row[0]}: {row[1]}件")
        
        print("\n✅ Entities統一モデルへのデータ投入完了！")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ エラー: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
