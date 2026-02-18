"""
認証APIテスト (test_auth.py)

/api/auth/login と /api/auth/me のテストケース。
"""
import pytest
import bcrypt
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from routers.auth import get_db_conn

client_instance = None


def get_test_client():
    """テストクライアントを返す（遅延初期化）"""
    from fastapi.testclient import TestClient
    return TestClient(app)


def make_mock_user(password: str = 'Zoom123!', is_active: bool = True) -> dict:
    """テスト用モックユーザーを生成する"""
    return {
        'id': 1,
        'email': 'onodso2@gmail.com',
        'password_hash': bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt(rounds=4)  # テスト用に低ラウンドで高速化
        ).decode('utf-8'),
        'name': '小野寺 壮',
        'role': 'admin',
        'is_active': is_active
    }


def make_db_override(user: dict | None):
    """
    dependency_overrides用のDB関数を生成する

    FastAPIのDependsはジェネレーター関数を期待するため、
    呼び出し可能な関数を返す。
    """
    def override():
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = user
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        yield mock_conn
    return override


class TestLoginEndpoint:
    """ログインエンドポイント (/api/auth/login) のテスト"""

    def test_login_success(self, client):
        """正常系: 正しい認証情報でログインできること"""
        user = make_mock_user('Zoom123!')
        app.dependency_overrides[get_db_conn] = make_db_override(user)

        try:
            response = client.post('/api/auth/login', json={
                'email': 'onodso2@gmail.com',
                'password': 'Zoom123!'
            })
            assert response.status_code == 200, f"期待: 200, 実際: {response.status_code}\n{response.text}"
            body = response.json()
            assert 'access_token' in body
            assert body['token_type'] == 'bearer'
            assert body['user']['email'] == 'onodso2@gmail.com'
            assert body['user']['role'] == 'admin'
        finally:
            app.dependency_overrides.clear()

    def test_login_invalid_password(self, client):
        """異常系: 間違ったパスワードでは401が返ること"""
        user = make_mock_user('Zoom123!')
        app.dependency_overrides[get_db_conn] = make_db_override(user)

        try:
            response = client.post('/api/auth/login', json={
                'email': 'onodso2@gmail.com',
                'password': 'WrongPassword!'
            })
            assert response.status_code == 401
            assert 'パスワード' in response.json()['detail']
        finally:
            app.dependency_overrides.clear()

    def test_login_nonexistent_user(self, client):
        """異常系: 存在しないユーザーでは401が返ること"""
        app.dependency_overrides[get_db_conn] = make_db_override(None)  # ユーザーなし

        try:
            response = client.post('/api/auth/login', json={
                'email': 'nobody@example.com',
                'password': 'Zoom123!'
            })
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_login_inactive_user(self, client):
        """異常系: 無効化されたアカウントでは403が返ること"""
        user = make_mock_user('Zoom123!', is_active=False)
        app.dependency_overrides[get_db_conn] = make_db_override(user)

        try:
            response = client.post('/api/auth/login', json={
                'email': 'onodso2@gmail.com',
                'password': 'Zoom123!'
            })
            assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()

    def test_login_invalid_email_format(self, client):
        """境界値: 不正なメール形式では422が返ること"""
        # PydanticバリデーションエラーのためDB接続は発生しないが念のためoverride
        app.dependency_overrides[get_db_conn] = make_db_override(None)
        try:
            response = client.post('/api/auth/login', json={
                'email': 'not-an-email',
                'password': 'Zoom123!'
            })
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()

    def test_login_missing_password(self, client):
        """境界値: パスワードなしのリクエストでは422が返ること"""
        # PydanticバリデーションエラーのためDB接続は発生しないが念のためoverride
        app.dependency_overrides[get_db_conn] = make_db_override(None)
        try:
            response = client.post('/api/auth/login', json={
                'email': 'onodso2@gmail.com'
            })
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()


class TestGetMeEndpoint:
    """ユーザー情報取得エンドポイント (/api/auth/me) のテスト"""

    def _get_valid_token(self, client) -> str:
        """有効なJWTトークンを取得するヘルパー"""
        user = make_mock_user('Zoom123!')
        app.dependency_overrides[get_db_conn] = make_db_override(user)

        response = client.post('/api/auth/login', json={
            'email': 'onodso2@gmail.com',
            'password': 'Zoom123!'
        })
        app.dependency_overrides.clear()

        if response.status_code == 200:
            return response.json().get('access_token', '')
        return ''

    def test_get_me_with_valid_token(self, client):
        """正常系: 有効なトークンでユーザー情報を取得できること"""
        token = self._get_valid_token(client)
        assert token, "トークン取得失敗"

        response = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        body = response.json()
        assert 'email' in body
        assert body['email'] == 'onodso2@gmail.com'

    def test_get_me_without_token(self, client):
        """異常系: トークンなしでは401が返ること（HTTPBearerの動作）"""
        response = client.get('/api/auth/me')
        # HTTPBearerはAuthorizationヘッダーなしで401を返す
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        """異常系: 不正なトークンでは401または403が返ること"""
        response = client.get('/api/auth/me', headers={'Authorization': 'Bearer invalid_token'})
        assert response.status_code in [401, 403]
