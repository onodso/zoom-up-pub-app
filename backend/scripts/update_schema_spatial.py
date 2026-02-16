import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base
from models.spatial import Mesh, Company, Building

def update_schema():
    print("🚀 Updating DB Schema for Spatial Indexing...")
    try:
        # Check connection
        with engine.connect() as conn:
            print("✅ Database connected.")
        
        # Create tables
        # This only creates tables that don't exist
        Base.metadata.create_all(bind=engine)
        print("✅ Schema updated successfully.")
        print("   Created tables: meshes, companies, buildings (if missing)")
        
    except Exception as e:
        print(f"❌ Schema update failed: {e}")

if __name__ == "__main__":
    update_schema()
