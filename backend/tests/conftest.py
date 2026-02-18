"""
pytest設定・フィクスチャ

テスト用のDBとFastAPIクライアントをセットアップする。
"""
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# テスト環境用のDB設定を事前に設定
os.environ.setdefault('POSTGRES_HOST', 'localhost')
os.environ.setdefault('POSTGRES_PORT', '5432')
os.environ.setdefault('POSTGRES_USER', 'zoom_admin')
os.environ.setdefault('POSTGRES_PASSWORD', 'changeme')
os.environ.setdefault('POSTGRES_DB', 'zoom_dx_db')
os.environ.setdefault('JWT_SECRET_KEY', 'test_secret_key_for_testing_only')

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.fixture(scope='session')
def client():
    """
    テスト用FastAPIクライアント

    全テストセッションで共有するHTTPクライアント。
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_db_conn():
    """
    モックDBコネクションフィクスチャ

    DB接続を必要とするテストでのモック用。
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


@pytest.fixture
def admin_token(client):
    """
    管理者ユーザーのJWTトークンを取得するフィクスチャ

    認証が必要なエンドポイントのテストで使用。
    """
    import bcrypt
    from psycopg2.extras import RealDictCursor

    # 認証APIをモックしてトークンを取得
    admin_user = {
        'id': 1,
        'email': 'onodso2@gmail.com',
        'password_hash': bcrypt.hashpw(b'Zoom123!', bcrypt.gensalt(rounds=4)).decode('utf-8'),
        'name': '小野寺 壮',
        'role': 'admin',
        'is_active': True
    }

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = admin_user

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    from routers.auth import get_db_conn
    app.dependency_overrides[get_db_conn] = lambda: iter([mock_conn])

    response = client.post('/api/auth/login', json={
        'email': 'onodso2@gmail.com',
        'password': 'Zoom123!'
    })

    app.dependency_overrides.clear()

    if response.status_code == 200:
        return response.json()['access_token']
    return None
