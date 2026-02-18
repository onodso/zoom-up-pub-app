"""
認証API - DB接続方式
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/auth', tags=['認証'])
security = HTTPBearer()

# JWT設定
JWT_SECRET = os.getenv('JWT_SECRET_KEY')
if not JWT_SECRET:
    logger.warning("JWT_SECRET_KEY が未設定です。開発用デフォルト値を使用します。")
    JWT_SECRET = "insecure_default_secret_key_for_dev_only_ChangeMe"

JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_HOURS = int(os.getenv('JWT_EXPIRE_HOURS', '8'))


def get_db_conn():
    """DB接続を生成するジェネレーター"""
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
    try:
        yield conn
    finally:
        conn.close()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "ae"
    assigned_regions: list[str] = []


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    パスワードをbcryptで検証する

    Args:
        plain_password: 平文パスワード
        hashed_password: DBに保存されたbcryptハッシュ

    Returns:
        検証結果（True/False）
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"パスワード検証エラー: {e}")
        return False


def _create_access_token(user_data: dict) -> str:
    """
    JWTアクセストークンを生成する

    Args:
        user_data: ユーザー情報辞書

    Returns:
        JWTトークン文字列
    """
    token_data = {
        'sub': str(user_data['id']),
        'email': user_data['email'],
        'role': user_data['role'],
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    }
    return jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.post('/login', response_model=LoginResponse)
async def login(request: LoginRequest, conn=Depends(get_db_conn)):
    """
    ログインエンドポイント

    DBからユーザーを取得し、bcryptでパスワードを検証してJWTを発行する。
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # DBからユーザー取得
        cur.execute(
            "SELECT id, email, password_hash, name, role, is_active FROM users WHERE email = %s",
            (request.email,)
        )
        user = cur.fetchone()
    except Exception as e:
        logger.error(f"DB接続エラー（ログイン）: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="データベースに接続できません"
        )

    # ユーザー存在確認 + パスワード検証
    if not user or not _verify_password(request.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません"
        )

    # アカウント有効確認
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このアカウントは無効化されています"
        )

    # 最終ログイン時刻を更新
    try:
        cur.execute(
            "UPDATE users SET last_login = NOW() WHERE id = %s",
            (user['id'],)
        )
        conn.commit()
    except Exception as e:
        logger.warning(f"最終ログイン時刻の更新に失敗: {e}")

    # JWTトークン生成
    access_token = _create_access_token(user)

    logger.info(f"ログイン成功: {user['email']} (role: {user['role']})")

    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'user': {
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'role': user['role']
        }
    }


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    現在のユーザー取得（ミドルウェア）

    JWTトークンを検証してペイロードを返す。
    """
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('sub')
        if user_id is None:
            raise HTTPException(status_code=401, detail="無効なトークン")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="無効なトークン")


@router.get('/me')
async def get_me(current_user: dict = Depends(get_current_user)):
    """現在のユーザー情報取得"""
    return current_user
