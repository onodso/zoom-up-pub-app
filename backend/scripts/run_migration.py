"""
Simple Migration Runner
指定したSQLファイルをPostgreSQLで実行
"""
import sys
import os
from pathlib import Path
import psycopg2

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from backend.config import settings

def run_migration(migration_file: str):
    """Execute a SQL migration file"""
    migration_path = Path(__file__).parent.parent / "db" / "migrations" / migration_file

    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_path}")
        return False

    print(f"🔄 Running migration: {migration_file}")

    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )

        cur = conn.cursor()

        # Read and execute SQL
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql = f.read()

        cur.execute(sql)
        conn.commit()

        print("✅ Migration completed successfully")
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_migration.py <migration_file>")
        print("Example: python run_migration.py 008_add_scoring_columns.sql")
        sys.exit(1)

    migration_file = sys.argv[1]
    success = run_migration(migration_file)
    sys.exit(0 if success else 1)
