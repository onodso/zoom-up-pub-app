# Zoom UP Public App

全国1,741自治体＋47都道府県教育委員会を対象としたZoom営業支援ダッシュボード「Local Gov DX Intelligence」

## 🚀 Production Environment

### AWS Lightsail (Tokyo) - Frontend
- **Status**: Backend Services Running
- **Host IP**: `54.150.207.122`
- **Swagger UI**: [http://54.150.207.122:8000/docs](http://54.150.207.122:8000/docs)
- **Role**: Lightweight Frontend + Thin API
- **Cost**: $10/month (1,500円/月)

### Lenovo Tiny (On-Premise) - AI Engine
- **Status**: Setup Pending
- **Role**: AI Processing (Ollama) + Database + Crawling
- **Cost**: Electricity only (~500円/月)
- **Setup Guide**: [docs/lenovo_tiny_setup_guide.md](docs/lenovo_tiny_setup_guide.md)

**Total Monthly Cost**: ~2,000円 (予算5,000円以内)

## Local Development

- **Frontend**: Next.js 16 + React 19 + Tailwind CSS
- **Backend**: FastAPI + PostgreSQL + Redis
- **Maps**: Deck.gl 9.1 + MapLibre GL
- **AI**: Ollama（ローカル）+ Gemini API（クラウド）
- **Infrastructure**: AWS Lightsail + Lenovo Tiny

## セットアップ

```bash
# 1) 環境変数設定
cp .env.example .env
# .env を編集してAPIキー等を設定

# 2) Docker起動（Lenovo Tiny）
docker compose up -d

# 3) フロントエンド依存関係インストール
cd frontend && npm install

# 4) 初期ユーザー作成
python scripts/setup/create_initial_user.py

# 5) フロントエンド開発サーバー起動
cd frontend && npm run dev
```

## 開発環境アクセス

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 初期ユーザー

- Email: `onodso2@gmail.com`
- Password: `Zoom123!`

## デプロイ

```bash
# AWS Lightsailへデプロイ
./scripts/deploy/deploy_to_aws.sh
```

## ディレクトリ構成

```
zoom-up-pub-app/
├── frontend/         # Next.js フロントエンド
├── backend/          # FastAPI バックエンド
├── scripts/          # セットアップ・デプロイスクリプト
├── data/             # マスタデータ・GeoJSON
├── docs/             # ドキュメント
└── .github/          # GitHub Actions
```
