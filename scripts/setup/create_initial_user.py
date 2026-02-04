#!/usr/bin/env python3
"""
初期管理ユーザー作成スクリプト
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# .env読み込み
load_dotenv(Path(__file__).parent.parent.parent / '.env')

sys.path.append(str(Path(__file__).parent.parent.parent / 'backend'))

try:
    import psycopg2
    import bcrypt
except ImportError:
    print("❌ 必要なパッケージがインストールされていません")
    print("   pip install bcrypt psycopg2-binary")
    sys.exit(1)

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', 5432),
    'user': os.getenv('POSTGRES_USER', 'zoom_admin'),
    'password': os.getenv('POSTGRES_PASSWORD', 'changeme'),
    'database': os.getenv('POSTGRES_DB', 'zoom_dx_db')
}


def create_initial_user():
    """初期管理ユーザー作成"""
    
    # ユーザー情報
    user_data = {
        'email': 'onodso2@gmail.com',
        'password': 'Zoom123!',
        'name': '小野寺 壮',
        'role': 'admin',
        'assigned_regions': ['全国']
    }
    
    # パスワードハッシュ化 (bcrypt)
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), salt).decode('utf-8')
    
    try:
        # データベース接続
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # INSERT
        cur.execute("""
            INSERT INTO users (email, password_hash, name, role, assigned_regions, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, TRUE, NOW())
            ON CONFLICT (email) DO UPDATE SET
                password_hash = EXCLUDED.password_hash,
                name = EXCLUDED.name
            RETURNING id, email, name
        """, (
            user_data['email'],
            password_hash,
            user_data['name'],
            user_data['role'],
            user_data['assigned_regions']
        ))
        
        result = cur.fetchone()
        conn.commit()
        
        print("✅ 初期ユーザー作成完了")
        print(f"   ID: {result[0]}")
        print(f"   Email: {result[1]}")
        print(f"   Name: {result[2]}")
        print(f"   Password: {user_data['password']}")
        
        cur.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"❌ データベース接続エラー: {e}")
        print("   Docker が起動しているか確認してください")
        sys.exit(1)


if __name__ == '__main__':
    create_initial_user()
