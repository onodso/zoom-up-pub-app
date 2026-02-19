# 技術スタック棚卸し（2026-02-19更新）

> 本ドキュメントは、プロジェクト「Zoom Gov Intelligence」で**実際に使われている技術**と**コードは存在するが未稼働**のものを区別して記録する。

---

## バックエンド（実稼働）

| 技術 | バージョン | 用途 | 状態 |
|------|-----------|------|------|
| Python | 3.x | メイン言語 | ✅ 稼働 |
| FastAPI | ≥0.115 | REST APIフレームワーク | ✅ 稼働 |
| Uvicorn | ≥0.30 | ASGIサーバー | ✅ 稼働 |
| Pydantic | ≥2.9 | データバリデーション | ✅ 稼働 |
| pydantic-settings | ≥2.0 | 環境変数管理 | ✅ 稼働 |
| psycopg2-binary | ≥2.9 | PostgreSQL接続（同期・全面使用） | ✅ 稼働 |
| SQLAlchemy | ≥2.0 | ORM（同期）・4モデル定義 | ✅ 稼働 |
| Alembic | ≥1.13 | DBマイグレーション | ✅ 稼働 |
| httpx | ≥0.27 | 非同期HTTPクライアント | ✅ 稼働 |
| requests | ≥2.31 | 同期HTTPクライアント | ✅ 稼働 |
| python-dotenv | ≥1.0 | 環境変数読み込み | ✅ 稼働 |
| python-multipart | ≥0.0.9 | フォームデータ解析 | ✅ 稼働 |
| email-validator | 2.1.0 | メールアドレス検証 | ✅ 稼働 |

## データベース・インフラ（実稼働）

| 技術 | バージョン | 用途 | デプロイ先 |
|------|-----------|------|-----------|
| PostgreSQL | 16-alpine | メインDB | Docker |
| Redis | 7.2-alpine | キャッシュ | Docker |
| Docker Compose | v3.9 | コンテナ管理 | ローカル/Lenovo |
| AWS Lightsail | - | 本番フロントエンド＋API | クラウド |
| Lenovo Tiny (Ubuntu) | - | AI処理・DB・クローリング | オンプレ |

## フロントエンド（実稼働 = Viteダッシュボード）

| 技術 | バージョン | 用途 |
|------|-----------|------|
| React | 19.2 | UIフレームワーク |
| TypeScript | 5.9 | 型安全 |
| Vite | 7.3 | ビルドツール |
| MapLibre GL JS | 5.18 | 地図表示（コロプレスマップ） |
| Recharts | 3.7 | グラフ描画 |
| TopoJSON Client | 3.1 | 地理データ変換 |
| Axios | 1.13 | HTTP通信 |

### フロントエンド（旧・移行予定）

| 技術 | バージョン | 状態 |
|------|-----------|------|
| Next.js | 14.2 | ⚠️ 認証ミドルウェアのみ使用中。Viteへの移植後に削除予定 |
| React | 18.3 | ⚠️ Next.js側 |
| deck.gl | 9.1 | ⚠️ Next.js側のみ |
| Framer Motion | 11.0 | ⚠️ Next.js側のみ |
| Tailwind CSS | 3.4 | ⚠️ Next.js側のみ |
| MapLibre GL | 3.6 | ⚠️ Next.js側（旧版） |

## 認証・セキュリティ

| 技術 | 用途 |
|------|------|
| python-jose[cryptography] | JWT生成・検証 |
| passlib[bcrypt] + bcrypt | パスワードハッシュ |
| Next.js Middleware | Cookie JWTベースのルート保護（移植予定） |

## AI/ML/DL

### ✅ 実稼働中（DS + ML）

| 技術/手法 | 分類 | 用途 | 実装ファイル |
|-----------|------|------|-------------|
| Z-score正規化 | **DS** | DXスコア標準化（カテゴリ2,3） | `services/score_calculator.py` |
| 指数減衰ペナルティ関数 | **DS** | カバレッジ不足の自治体に減点 | `services/score_calculator.py` |
| 5カテゴリ重み付けスコア | **DS** | 住民DX(30%)+推進体制(25%)+業務DX(20%)+教育DX(10%)+情報発信(10%) | `services/score_calculator.py` |
| NumPy | **DS** | ベクトル演算・統計計算 | 各サービス |
| Pandas | **DS** | データ操作・ETLパイプライン | 各サービス |
| ルールベース決定木 | **ML** | 7パターン分類（DX Leaders〜Laggards） | `services/pattern_classifier.py` |
| Ollama (Llama3) | **ML/LLM** | 首長施政方針分析・ニュース分析 | `engines/ollama_analyzer.py`, `services/llm_analyzer.py` |
| Gemini API | **ML/LLM** | クラウドLLM（記事選別） | `.env`設定 |
| Google Custom Search API | **DS** | ニュース検索・データ収集 | `services/google_search_collector.py` |

### ⏸️ 凍結中（DL）

| 技術 | 分類 | 状態 | 実装ファイル |
|------|------|------|-------------|
| BERT (cl-tohoku/bert-base-japanese) | **DL** | コード存在・torch未インストール | `engines/bert_classifier.py` |
| PyTorch | **DL** | requirements.txtでコメントアウト | - |
| Transformers (HuggingFace) | **DL** | requirements.txtでコメントアウト | - |

> **凍結理由**: Lightsail環境でのtorch(3GB)運用は非現実的。Lenovo Tinyでの将来運用の余地を残して保持。`nightly_scoring.py`からのimportはオプショナル化済み。

### ⛔ 未使用（コードには残存）

| 技術 | 状態 |
|------|------|
| asyncpg | requirements.txtでコメントアウト。実コード使用ゼロ |

## データ収集パイプライン

| データソース | 収集手段 | 実装ファイル |
|-------------|---------|-------------|
| 総務省DX調査 | HTTPダウンロード＋CSV解析 | `services/download_dx_survey.py` |
| e-Stat（政府統計API） | REST API | `services/estat_client.py`, `estat_collector.py` |
| GIGAスクール構想 | HTTPダウンロード | `services/download_giga_data.py` |
| gBizINFO | REST API＋CSVインポート | `scripts/import_gbizinfo_csv.py` |
| ニュース記事 | Google Custom Search | `services/collect_news_top500.py` |
| 入札・調達情報 | Webスクレイピング | `services/bidding_scraper.py` |

## テスト

| 技術 | 用途 |
|------|------|
| pytest | テストフレームワーク |
| pytest-asyncio | 非同期テスト |
| unittest.mock | モック・スタブ |

---

## アーキテクチャ概要

```
[ブラウザ]
    |
    v
[Viteダッシュボード (React 19 + MapLibre 5.18)]
    |  Axios/fetch
    v
[FastAPI (Uvicorn)] ← JWT認証
    |
    +---> [PostgreSQL 16] ← psycopg2 (同期)
    +---> [Redis 7.2] ← キャッシュ
    +---> [Ollama (Llama3)] ← LLM分析（Lenovo Tiny）
    +---> [Gemini API] ← クラウドLLM
    +---> [Google Custom Search API] ← ニュース収集
    +---> [e-Stat API] ← 政府統計
```
