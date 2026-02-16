import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SQLALCHEMY_DATABASE_URL
from models.entities import Entity
from models.municipality import Municipality
from services.scoring_engine import ScoringEngine

def main():
    print("🚀 Updating Activity Index for all municipalities...")
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    scoring_engine = ScoringEngine(session)
    
    try:
        # Get all municipality entities
        entities = session.query(Entity).filter(Entity.entity_type == 'municipality').all()
        print(f"📋 Found {len(entities)} municipal entities.")
        
        updated_count = 0
        
        for entity in entities:
            # Extract code (M12345 -> 12345)
            # entity_id is guaranteed to start with M via import_entities.py
            muni_code = entity.entity_id[1:]
            
            # Find Municipality record
            muni = session.query(Municipality).filter(Municipality.code == muni_code).first()
            if not muni:
                print(f"⚠️ Municipality not found for code: {muni_code} (Entity: {entity.entity_id})")
                continue
                
            # Calculate Activity Index
            # Note: ScoringEngine expects municipality_id (PK), not code
            score = scoring_engine.calculate_activity_index(muni.id)
            
            # Update Entity
            entity.activity_index = score
            updated_count += 1
            
            if updated_count % 100 == 0:
                print(f"   Processed {updated_count} entities... (Last: {entity.name} = {score})")
        
        session.commit()
        print(f"✅ Successfully updated Activity Index for {updated_count} municipalities.")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()
