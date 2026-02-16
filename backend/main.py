"""
Zoom UP Public App - FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# .envファイルを読み込む（親ディレクトリにある場合を想定）
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

from routers import auth, municipalities, scores, proposals, map_data

app = FastAPI(
    title="Local Gov DX Intelligence API",
    description="全国自治体向けZoom営業支援ダッシュボードAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS設定
# 本番環境では、必要な origins, methods, headers のみを許可してください
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    max_age=600,  # プリフライトリクエストのキャッシュ（10分）
)

# ルーター登録
app.include_router(auth.router)
app.include_router(municipalities.router)
app.include_router(scores.router)
app.include_router(proposals.router)
app.include_router(map_data.router)


@app.get("/api/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Local Gov DX Intelligence API",
        "docs": "/docs"
    }
