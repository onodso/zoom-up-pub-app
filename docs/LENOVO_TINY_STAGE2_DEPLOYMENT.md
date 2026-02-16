# Lenovo Tiny Stage 2 Deployment Guide
## Decision Readiness v3.0 本番デプロイ

**Date**: 2026-02-13
**Target**: Lenovo Tiny (Windows 11 + Docker)
**Status**: 既存環境あり（2026-02-08セットアップ済み）

---

## 📋 **前提条件（既に完了）**

以下は2026-02-08時点で完了済み：
- ✅ Docker Desktop インストール
- ✅ PostgreSQL (timescaledb)
- ✅ Ollama + Llama3.2:1b
- ✅ Tailscale VPN (100.107.246.40)
- ✅ FastAPI サーバー稼働中

---

## 🚀 **Stage 2 デプロイ手順**

### **Phase 1: コードの更新**

#### **1-1. Lenovo TinyにSSH接続**

**Macから**:
```bash
# Tailscale経由でSSH接続
ssh ubuntu@100.107.246.40

# または、Lenovo Tinyで直接PowerShellを開く
```

#### **1-2. プロジェクトディレクトリに移動**
```bash
cd /opt/zoom-dx
# または Windowsの場合:
# cd C:\Users\onodera\zoom-dx
```

#### **1-3. 最新コードを取得**
```bash
# Gitから最新版をpull
git pull origin main

# 変更内容確認
git log --oneline -5
```

---

### **Phase 2: データベースマイグレーション**

#### **2-1. 新しいマイグレーションファイルの確認**
```bash
# マイグレーションファイルの存在確認
ls -la backend/db/migrations/008_add_scoring_columns.sql

# 内容確認
cat backend/db/migrations/008_add_scoring_columns.sql
```

#### **2-2. マイグレーション実行**

**Option A: Dockerコンテナ経由（推奨）**
```bash
# PostgreSQLコンテナに接続
docker exec -it zoom-dx-postgres psql -U zoom_admin -d zoom_dx_db

# マイグレーション実行
\i /app/backend/db/migrations/008_add_scoring_columns.sql

# 実行結果確認
SELECT 'Migration 008 completed' AS status;

# テーブル構造確認
\d municipalities
\d decision_readiness_scores

# 終了
\q
```

**Option B: Pythonスクリプト経由**
```bash
# Macから直接実行（Tailscale経由）
export DB_HOST=100.107.246.40
export DB_PORT=5432
export DB_USER=zoom_admin
export DB_PASSWORD=<your_password>
export DB_NAME=zoom_dx_db

python3 backend/scripts/run_migration.py 008_add_scoring_columns.sql
```

#### **2-3. マイグレーション確認**
```bash
# PostgreSQLに再接続
docker exec -it zoom-dx-postgres psql -U zoom_admin -d zoom_dx_db

# 新しいカラムの確認
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'municipalities'
AND column_name IN ('population_decline_rate', 'elderly_ratio', 'dx_status');

# decision_readiness_scores テーブルの確認
SELECT COUNT(*) FROM decision_readiness_scores;
```

---

### **Phase 3: AI依存パッケージのインストール**

#### **3-1. APIコンテナに入る**
```bash
# APIコンテナのシェルに入る
docker exec -it zoom-dx-api /bin/bash
```

#### **3-2. 依存パッケージインストール**
```bash
# コンテナ内で実行
pip3 install torch transformers fugashi ipadic

# インストール確認
python3 -c "import torch; import transformers; print('✅ AI packages installed')"

# コンテナから抜ける
exit
```

**注意**: torchは約2GBあるため、インストールに5-10分かかります。

---

### **Phase 4: データエンリッチメント**

#### **4-1. 軽量版エンリッチメント実行**
```bash
# APIコンテナ内で実行
docker exec -it zoom-dx-api python3 scripts/enrich_dx_status_lite.py

# 期待される出力:
# ✅ DX Status Enrichment Completed (Mock Data)
```

#### **4-2. スコアリング実行（テスト）**
```bash
# 軽量版スコアリング（AI機能なし）
docker exec -it zoom-dx-api python3 scripts/nightly_scoring_lite.py

# または、完全版（AI機能あり）
docker exec -it zoom-dx-api python3 scripts/nightly_scoring.py
```

**期待される出力**:
```
🌙 Starting Nightly Scoring Batch...
🎯 Processing 50 municipalities...
   > Scoring 札幌市 (011002)...
     ✅ Score: 68/100 (Confidence: medium)
        - Structural: 18/30
        - Leadership: 18/25
        - Peer: 12/20
        - Feasibility: 11/15
        - Accountability: 9/10
```

---

### **Phase 5: API動作確認**

#### **5-1. Swagger UIアクセス**
ブラウザで以下にアクセス:
```
http://100.107.246.40:8000/docs
```

#### **5-2. エンドポイントテスト（Macから）**
```bash
# Health Check
curl http://100.107.246.40:8000/api/health

# Score API
curl http://100.107.246.40:8000/api/scores/011002 | jq .

# Map API（全国データ）
curl http://100.107.246.40:8000/api/scores/map/all | jq '.[0:3]'

# Proposal Generation
curl -X POST http://100.107.246.40:8000/api/proposals/generate \
  -H "Content-Type: application/json" \
  -d '{
    "city_code": "011002",
    "product": "Zoom Workplace",
    "target_audience": "CIO"
  }' | jq .
```

---

### **Phase 6: 定期実行設定（Cron）**

#### **6-1. Cronジョブ作成**

**Lenovo Tiny（Linux/WSL）の場合**:
```bash
# Crontabを編集
crontab -e

# 以下を追加（毎日深夜3時に実行）
0 3 * * * docker exec zoom-dx-api python3 /app/scripts/nightly_scoring.py >> /opt/zoom-dx/logs/scoring.log 2>&1
```

**Windows Scheduled Task（PowerShellの場合）**:
```powershell
# タスクスケジューラでバッチファイルを作成
# C:\zoom-dx\run_nightly_scoring.bat
docker exec zoom-dx-api python3 /app/scripts/nightly_scoring.py

# タスクスケジューラに登録
# - トリガー: 毎日 3:00 AM
# - アクション: C:\zoom-dx\run_nightly_scoring.bat
```

---

### **Phase 7: 本番環境変数の設定**

#### **7-1. .env.lenovo ファイル更新**
```bash
# Lenovo Tiny上で編集
nano /opt/zoom-dx/.env.lenovo
```

**追加すべき環境変数**:
```bash
# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=zoom_admin
POSTGRES_PASSWORD=<strong_password_here>
POSTGRES_DB=localgov_intelligence

# Ollama (Docker内)
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2:1b

# e-Stat API（オプション）
ESTAT_APP_ID=<your_estat_app_id>

# Allowed Origins（Next.js frontendのドメイン）
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

#### **7-2. Docker Composeを再起動**
```bash
# 環境変数を再読み込みして再起動
docker compose -f docker-compose.lenovo.yml down
docker compose -f docker-compose.lenovo.yml up -d

# ログ確認
docker compose -f docker-compose.lenovo.yml logs -f api
```

---

## 📊 **デプロイ後の確認チェックリスト**

### **データベース**
- [ ] `decision_readiness_scores` テーブルが存在する
- [ ] `municipalities` テーブルに `dx_status`, `population_decline_rate` カラムが存在
- [ ] 少なくとも50件のスコアデータが入っている

```bash
docker exec -it zoom-dx-postgres psql -U zoom_admin -d localgov_intelligence -c "SELECT COUNT(*) FROM decision_readiness_scores;"
```

### **API**
- [ ] GET `/api/scores/{city_code}` が動作する
- [ ] GET `/api/scores/map/all` が1,918件返す
- [ ] POST `/api/proposals/generate` がOllamaで提案文を生成する
- [ ] POST `/api/scores/batch` がバックグラウンドジョブを起動する

### **AI Engines**
- [ ] BERT ClassifierがLeadership Commitmentを計算できる
- [ ] Ollama Analyzerがキーワード抽出できる

```bash
# BERTテスト
docker exec -it zoom-dx-api python3 -c "
from backend.engines.bert_classifier import BertCommitmentClassifier
bert = BertCommitmentClassifier()
result = bert.predict_commitment('私は、デジタル・トランスフォーメーションを強力に推進します。')
print(result)
"
```

### **定期実行**
- [ ] Cronジョブが登録されている
- [ ] テスト実行が成功する

```bash
# 手動実行テスト
docker exec zoom-dx-api python3 /app/scripts/nightly_scoring.py
```

---

## 🔧 **トラブルシューティング**

### **問題1: マイグレーションエラー**
```
ERROR:  column "dx_status" already exists
```

**解決策**: カラムが既に存在する場合はスキップされます（`ADD COLUMN IF NOT EXISTS`）

---

### **問題2: torch インストールエラー**
```
ModuleNotFoundError: No module named 'torch'
```

**解決策**:
```bash
# APIコンテナを再ビルド
docker compose -f docker-compose.lenovo.yml build api
docker compose -f docker-compose.lenovo.yml up -d api
```

---

### **問題3: Ollama接続エラー**
```
Ollama Error: Connection refused
```

**解決策**:
```bash
# Ollamaコンテナの状態確認
docker ps | grep ollama

# Ollamaコンテナを再起動
docker restart zoom-dx-ollama

# モデルがダウンロードされているか確認
docker exec zoom-dx-ollama ollama list
```

---

### **問題4: メモリ不足**
```
OOM (Out of Memory) killed
```

**解決策**:
```bash
# WSL2のメモリ制限を増やす（Windows）
# C:\Users\onodera\.wslconfig
[wsl2]
memory=12GB  # 8GB → 12GB に増やす
processors=4

# WSL再起動
wsl --shutdown
```

---

## 🎯 **次のステップ（Stage 3）**

Stage 2デプロイが完了したら：

1. **フロントエンド連携**
   - Next.jsから `http://100.107.246.40:8000` にAPI接続
   - Deck.gl地図表示の実装

2. **AWS Lightsailデプロイ（UI層のみ）**
   - Next.jsアプリをLightsailにデプロイ
   - Tailscale経由でLenovo TinyのAPIに接続

3. **監視・ログ設定**
   - Sentry/CloudWatchでエラー監視
   - バックアップ戦略の実装

---

## 📝 **デプロイ完了報告フォーマット**

デプロイ完了後、以下を記録：

```markdown
# Lenovo Tiny Stage 2 Deployment Report

**Date**: 2026-02-13
**Deployed by**: [Your Name]
**Deployment Duration**: X hours

## Deployment Status
- ✅ Database Migration (008)
- ✅ AI Packages Installed
- ✅ Data Enrichment
- ✅ API Endpoints Tested
- ✅ Cron Job Configured

## Performance Metrics
- API Response Time: ~50ms
- Map API (1,918 records): ~200ms
- Proposal Generation: ~3s (Ollama)
- Daily Batch Processing: ~5min (50 cities)

## Known Issues
- None

## Next Actions
- [ ] Frontend Integration
- [ ] AWS Lightsail UI Deployment
```

---

**準備はできましたか？デプロイを開始しましょう！**
