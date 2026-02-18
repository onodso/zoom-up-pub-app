"""
初期ユーザー作成スクリプト

DBに管理者ユーザーを作成する。
初回セットアップ時に一度だけ実行する。

使い方:
    python backend/scripts/create_initial_user.py
"""
import os
import sys
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor

# パス設定
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))


def get_connection():
    """DB接続を取得する"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'zoom_dx_db'),
        user=os.getenv('POSTGRES_USER', 'zoom_admin'),
        password=os.getenv('POSTGRES_PASSWORD', 'changeme')
    )


def hash_password(plain_password: str) -> str:
    """
    パスワードをbcryptでハッシュ化する

    Args:
        plain_password: 平文パスワード

    Returns:
        bcryptハッシュ文字列
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')


def create_user(
    conn,
    email: str,
    password: str,
    name: str,
    role: str = 'admin',
    assigned_regions: list = None
) -> dict:
    """
    ユーザーをDBに作成する

    Args:
        conn: DB接続
        email: メールアドレス
        password: 平文パスワード
        name: 表示名
        role: ロール（admin/ae）
        assigned_regions: 担当地域リスト

    Returns:
        作成されたユーザー情報
    """
    if assigned_regions is None:
        assigned_regions = ['全国']

    password_hash = hash_password(password)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute(
            """
            INSERT INTO users (email, password_hash, name, role, assigned_regions, is_active)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (email) DO UPDATE SET
                password_hash = EXCLUDED.password_hash,
                name = EXCLUDED.name,
                role = EXCLUDED.role,
                assigned_regions = EXCLUDED.assigned_regions
            RETURNING id, email, name, role
            """,
            (email, password_hash, name, role, assigned_regions)
        )
        user = cur.fetchone()
        conn.commit()
        return dict(user)
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"ユーザー作成エラー: {e}") from e
    finally:
        cur.close()


def main():
    """初期ユーザーを作成するメイン処理"""
    print("🔐 初期ユーザー作成スクリプト")
    print("=" * 40)

    # 作成するユーザー一覧
    initial_users = [
        {
            'email': 'onodso2@gmail.com',
            'password': 'Zoom123!',
            'name': '小野寺 壮',
            'role': 'admin',
            'assigned_regions': ['全国']
        },
    ]

    try:
        conn = get_connection()
        print(f"✅ DB接続成功: {os.getenv('POSTGRES_HOST', 'localhost')}")
    except Exception as e:
        print(f"❌ DB接続失敗: {e}")
        print("  → docker compose up -d postgres を実行してからリトライしてください")
        sys.exit(1)

    for user_data in initial_users:
        try:
            user = create_user(
                conn,
                email=user_data['email'],
                password=user_data['password'],
                name=user_data['name'],
                role=user_data['role'],
                assigned_regions=user_data['assigned_regions']
            )
            print(f"✅ ユーザー作成/更新: {user['email']} (role: {user['role']})")
        except Exception as e:
            print(f"❌ ユーザー作成失敗 ({user_data['email']}): {e}")

    conn.close()
    print("\n✅ 完了！")
    print("  ログイン情報:")
    for u in initial_users:
        print(f"    Email: {u['email']}")
        print(f"    Password: {u['password']}")


if __name__ == '__main__':
    main()
