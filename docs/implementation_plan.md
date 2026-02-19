# 改訂版：5人の専門家（v2）による戦略的リファクタリング計画

> 第三者レビュー2件の指摘を反映した最終版。
> 「整理」ではなく「戦略的選択」に踏み込む。

## 新パネル（前回と異なる5人）

| 専門家 | 役割 | 視点 |
|--------|------|------|
| 🎯 プロダクトオーナー | 営業ツールとしての価値判断 | 何が本当に必要か |
| ⚡ パフォーマンスエンジニア | Git/インフラ最適化 | 10GBのGitをどうするか |
| 🔬 ML/AIエンジニア | DS/ML/DLの戦略判断 | BERTを捨てるか否か |
| 🏗️ バックエンドアーキテクト | DB/API設計の統一 | psycopg2 vs asyncpg |
| 🖥️ フロントエンドリード | Next.js vs Vite判断 | 二重構造の解消 |

---

## 調査で判明した事実（前回から追加）

| 項目 | 事実 |
|------|------|
| `.git` サイズ | **10GB**（clone不可能レベル） |
| asyncpg 使用箇所 | `requirements.txt` にのみ記載。**実コード使用ゼロ** |
| psycopg2 使用箇所 | ルーター3個、サービス12個、スクリプト多数 = **全面使用** |
| BERT参照 | `nightly_scoring.py` でimportのみ。**ダミーテキストでモック状態** |
| Next.js の役割 | 認証ミドルウェア＋旧ダッシュボード（`frontend/app/page.tsx`：245行） |
| Viteダッシュボード | **現在のメイン機能**。ドリルダウン地図＋サイドパネル＋StatsBar |
| database.py | SQLAlchemy**同期のみ**。4モデル＋複数スクリプトが依存 |

---

## Step 1: Git履歴浄化（即日 ⚡🎯 全員一致）

> [!CAUTION]
> `.git` が **10GB**。zip 3本（計8.5GB）が履歴に焼き付いている。

**⚡ パフォーマンスエンジニア**: 「git rm --cached では履歴は消えない。BFGで根治が必須。ただし注意点が3つある」

### 実行手順

```bash
# 1. バックアップ（必須）
cp -r .git .git_backup

# 2. BFG Repo-Cleaner でzip除外
brew install bfg  # macOSの場合
bfg --delete-files '*.zip' .

# 3. 履歴クリーン
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. force push（リモートにも反映）
git push --force
```

**🎯 プロダクトオーナー**: 「force pushの前に、チーム全員への連絡は必須。ただし開発者は小野寺さん1人なので、即実行可」

**⚡ 反論**: 「jageocoder_dbのtrieファイル群（計20MB）もGit追跡されている。データファイル全般を`.gitignore`に追加すべき」

### .gitignore 追加内容

```diff
+# 大容量データ
+*.zip
+*.csv.gz
+data/jageocoder_db/
+data/gbizinfo/

+# ログ・デバッグ
+*.log
+logs*.txt
+header_dump.txt

+# バックエンドのダンプ
+backend/*.csv
```

---

## Step 2: 不要ファイル整理（即日 🏗️🎯 全員一致）

### 2-1. ディレクトリ構成の改善

**第三者レビューの「用途別分離」を採用**:

```
scripts/
  debug/       ← 調査・デバッグスクリプト（21個移動）
  migration/   ← DB移行スクリプト（既存の migrate_db.py 等）
  oneoff/      ← 一度きりのインポートスクリプト
```

### 2-2. backend/ 直下から移動するファイル（15個）

`scripts/debug/` へ:
- `audit_data_completeness.py`, `audit_data_simple.py`
- `debug_gbizinfo_deep.py`, `dump_sapporo_stats.py`
- `extract_mayors.py`, `get_mayor_info.py`, `import_mp.py`
- `inspect_estat_meta.py`, `search_estat_stats.py`
- `test_gbizinfo_api.py`, `test_mlit_api.py`
- `test_multi_proposals.py`, `test_plateau_api.py`, `test_proposal.py`
- `update_mayors_to_db.py`

### 2-3. services/ 内のデバッグスクリプト（6個） → `scripts/debug/`

- `debug_dx_import.py` ~ `debug_dx_import_v4.py`
- `debug_estat_import.py`, `inspect_estat_excel.py`

### 2-4. ルートの不要ファイル削除

- `backend.log`, `exec.log` （`.gitignore`対象、ローカル削除）
- `logs.txt`, `logs_tail.txt`, `header_dump.txt` （git追跡解除＋削除）

---

## Step 3: スコアエンジン統合（即日 🔬🏗️ 合意）

### 議論内容

**🔬 ML/AIエンジニア**: 「`score_calculator.py`（299行）と`improved_score_calculator.py`（478行）は重複。改善版にはZ-score正規化、カバレッジペナルティ、分母正規化がある。明らかに上位互換」

**🏗️ バックエンドアーキテクト**: 「旧版を参照しているファイルはあるか？」

**調査結果**: `score_calculator.py` を直接importしている箇所は**ゼロ**。両方とも `__main__` で直接実行する設計。

### 実行方針

1. `improved_score_calculator.py` → `score_calculator.py` にリネーム
2. 旧 `score_calculator.py` → `scripts/debug/score_calculator_legacy.py` にアーカイブ
3. 第三者指摘：「improved」という名前を残さない

---

## Step 4: BERT/DL戦略の決定（🔬🎯 議論あり）

### 激しい議論

**🔬 ML/AI（存続派）**: 「BERTコードは将来の自前推論に必要。Lightsailでは動かなくてもLenovo Tinyで動く。GPU不要、CPU推論で十分」

**🎯 プロダクトオーナー（廃止派）**: 「現時点でダミーテキストしか使っていない。torch 3GBを入れてテストすらできていない。Gemini APIで十分」

**⚡ パフォーマンス（現実派）**: 「第三者が指摘した通り、Lightsailでは無理。Lenovo Tinyで動かすなら可能だが、この環境は第三者が把握していない」

> [!IMPORTANT]
> **全員一致の結論**: BERTコードは**削除しない**が、**Phase 2として凍結**する。
> - `requirements.txt` の torch/transformers はコメントアウトのまま維持
> - `engines/bert_classifier.py` は残すが、`nightly_scoring.py` からのimportをオプショナルにする
> - 現在のML/DLは **Ollama(LLM) + ルールベース決定木 + Z-score統計** の3本柱で運用
>
> **理由**: Lenovo TinyにOllamaが動く環境があり、将来的にBERTも試せる余地を残す

### nightly_scoring.py の修正

```python
# 変更前
from engines.bert_classifier import BertCommitmentClassifier

# 変更後（オプショナル化）
try:
    from engines.bert_classifier import BertCommitmentClassifier
    BERT_AVAILABLE = True
except ImportError:
    BERT_AVAILABLE = False
```

---

## Step 5: フロントエンド統合戦略（🖥️🎯 議論あり）

### 激しい議論

**第三者A**: 「Next.js一本化」
**第三者B**: 「Vite一本化。思い切って完全削除」

**🖥️ フロントエンドリード**: 「事実を見よう」

| 比較項目 | Next.js (`frontend/`) | Vite (`frontend/dashboard/`) |
|----------|----------------------|------------------------------|
| 機能 | 認証＋旧ダッシュボード | ドリルダウン地図（最新メイン） |
| React | 18.3 | **19.2** |
| MapLibre | 3.6 | **5.18** |
| 開発中？ | 作業ログ(2/19)で**言及なし** | 作業ログ(2/19)で**全面改修済み** |
| 認証 | middleware.ts（Cookie JWT） | **なし** |
| コード行数 | page.tsx 245行 | App.tsx 215行 + MapView 31K |

**🖥️ 結論**: 「Viteが明確にメイン。Next.jsの唯一の価値は認証ミドルウェア。これはVite側に移植できる」

> [!WARNING]
> **全員一致の結論**: 以下の段階的移行を推奨（一気に削除はリスク）
> 1. **今回**: Next.jsの旧ダッシュボードコード（`frontend/app/page.tsx`等）を削除
> 2. **次回**: 認証ロジックをViteダッシュボードに移植 → Next.js完全削除
>
> **第三者の「思い切って完全削除」は理想だが、認証が消えるリスクを無視している**

---

## Step 6: DB接続方式の整理（🏗️ 議論あり）

### 激しい議論

**第三者指摘**: 「asyncpgベースへ統一が理想」

**🏗️ バックエンドアーキテクト**: 「現実を見よう。**asyncpgは1行も使われていない**。psycopg2が全面使用。SQLAlchemy同期で4モデルが定義済み。asyncpg統一はフルリライトと同義」

**🎯 プロダクトオーナー**: 「それは今やるべきじゃない。営業ツールとしての価値が先」

> **全員一致**: asyncpgへの移行は**しない**。`requirements.txt`からasyncpgを削除し、現状の`psycopg2 + SQLAlchemy同期`に正直に統一する。

### requirements.txt 変更

```diff
-asyncpg>=0.29.0
+# asyncpg は現時点で未使用。将来のasync化時に導入
+# asyncpg>=0.29.0
```

---

## Step 7: 技術スタックドキュメント作成

#### [NEW] [docs/TECH_STACK.md](file:///Users/sonodera/zoom-up-pub-app/docs/TECH_STACK.md)

Phase 2 の棚卸し結果を、**実際に使われている/使われていないを明記**した形で文書化。

---

## Phase 3: 認証統合と完全移行（Step 11-13）

**🖥️ フロントエンドリード**: 「Next.js を残す理由はもはやない。Vite一本化により、ビルド時間・認知負荷・依存関係の全てが改善する」

### Step 11: 認証ロジック移植（FastAPI + React Context）

現状の `middleware.ts`（Cookie検証）を、Reactの `AuthProvider` と FastAPI の依存性注入に置き換える。

#### 1. Frontend (Vite)
- `AuthProvider.tsx`: アプリ起動時に `/api/v1/auth/me` を検証。
- `ProtectedRoute.tsx`: 未ログイン時に `/login` へリダイレクト。
- `Login.tsx`: FastAPI の `/auth/login` (OAuth2Password) に credentials を送信し、Cookie (HttpOnly) をセット。

#### 2. Backend (FastAPI)
- `routers/auth.py`: 既に実装済み（`login_for_access_token`, `read_users_me`）。
- `test_auth.py`: 9件のテストがPASSしているため、バックエンド修正は不要の可能性大。

### Step 12: Next.js削除

Viteへの移行確認後、以下を削除：
- `frontend/app/`
- `frontend/public/` (Vite側に必要なものは移動済)
- `frontend/next.config.mjs`
- `frontend/middleware.ts`

### Step 13: BERT有効化

`backend/scripts/nightly_scoring.py` のコメントアウトを解除。

```python
# nightly_scoring.py

# 復活
from engines.bert_classifier import BertCommitmentClassifier
```

---

## 実行優先順位（全専門家合意）

| 優先度 | Step | 理由 | 破壊的？ |
|--------|------|------|----------|
| 🔴 P0 | Step 1: Git浄化 | 10GBは即座に対処が必要 | ⚠️ force push |
| 🟠 P1 | Step 2: ファイル整理 | コードの見通し改善 | ✅ 安全 |
| 🟠 P1 | Step 3: スコアエンジン統合 | 重複排除 | ✅ 安全 |
| 🟡 P2 | Step 4: BERT凍結対応 | importエラー防止 | ✅ 安全 |
| 🟡 P2 | Step 5: 旧ダッシュボード削除 | 認知負荷削減 | ⚠️ 要確認 |
| 🟢 P3 | Step 6: requirements整理 | 正直な依存管理 | ✅ 安全 |
| 🟢 P3 | Step 7: 技術ドキュメント | 知識の保存 | ✅ 安全 |
| 🔵 P4 | Step 11: 認証移植 | Next.js削除の前提 | ⚠️ 要テスト |
| 🔵 P4 | Step 12: Next.js削除 | 完全な一本化 | ⚠️ 破壊的 |

---

## 検証計画

```bash
# 1. Git浄化後のサイズ確認
du -sh .git  # 目標: 100MB以下

# 2. テスト実行
cd backend && python -m pytest tests/ -v

# 3. main.py インポート確認（移動ファイルが壊していないか）
cd backend && python -c "from main import app; print('OK')"

# 4. Viteダッシュボードビルド確認
cd frontend/dashboard && npm run build
```

---

## Phase 4: 本番デプロイと品質安定化 (Lenovo Tiny)

Phase 3で完成したアプリケーションを、本番環境である **Lenovo Tiny (Windows + WSL2)** に展開し、安定稼働させます。

### Step 14: デプロイスクリプト整備
- **現状**: `deploy_lenovo_windows.ps1` が古く、Next.jsのビルド手順などが残っている。
- **改修**:
    - `docker-compose.lenovo.yml` を正とする。
    - フロントエンドのビルドはDocker内で行うか、成果物のみ転送する形式に統一。
    - バージョン管理されたDockerイメージを使用するよう修正。

### Step 15: 本番環境設定
- **Secrets管理**: `.env` ファイルを安全に転送する手順を確立（scp/sftp）。
- **ネットワーク**: WSL2特有のポートフォワーディング設定を確認（Host 0.0.0.0 bind）。

### Step 16: 本番DBマイグレーション
- 既存データのバックアップを取得 (`pg_dump`)。
- `docker compose run api alembic upgrade head` を実行し、スキーマを最新化。

### Step 17: 本番動作確認
- **ヘルスチェック**: `/api/health`
- **シナリオテスト**: ログイン → 地図表示 → スコア詳細確認。
- **負荷確認**: `htop` / タスクマネージャーでメモリ・CPU使用率を監視。

---

## Phase 5: 運用自動化

### Step 18: 定期実行設定
- `nightly_scoring.py` を毎晩実行するジョブを作成。
- Windows Task Scheduler または WSL2内の `cron` を使用。

### Step 19: CI/CD (GitHub Actions)
- Push時に `pytest` と `npm run build` を自動実行。
- 品質の回帰を防止。

---
```
