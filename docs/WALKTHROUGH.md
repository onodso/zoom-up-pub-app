# 2026-02-19 実施報告書：プロジェクト戦略的リファクタリング (外部レビュー版)

## 担当: Gemini Pro (by Google DeepMind)
## 日付: 2026-02-19

---

## 1. 概要

5人の専門家パネル（v2）による戦略的リファクタリングを実施。第三者レビュー2件の指摘を反映し、以下の主要課題を解決しました。
- **Gitリポジトリの肥大化**: 10GB → 16MB (99.8%削減)
- **コードベースの分断**: Next.jsの一部機能をViteへ統合し、フロントエンドを一本化
- **DB/コードの不整合**: スキーマと実装の乖離を解消
- **MLモジュールの復旧**: BERT依存関係を適切に管理し機能を復旧

---

## 2. ディレクトリ構成の最終形

### Backend (`/backend`)
不要なスクリプト（21ファイル）を `scripts/debug` 等へ移動し、責務を明確化。
```text
backend/
├── main.py                  # FastAPI エントリーポイント
├── database.py              # DB接続 (SQLAlchemy/psycopg2)
├── models/                  # DBモデル (SQLAlchemy)
│   ├── entities.py          # Municipalities, Users等
│   └── ...
├── routers/                 # APIエンドポイント
│   ├── auth.py              # JWT認証 (OAuth2PasswordBearer)
│   ├── map_data.py          # 地図データ提供
│   └── ...
├── services/                # ビジネスロジック
│   ├── score_calculator.py  # 統合されたスコア計算エンジン
│   └── ...
├── engines/                 # AI/MLエンジン
│   ├── bert_classifier.py   # BERT分類器 (Torch)
│   └── ...
└── scripts/                 # 運用・バッチスクリプト
    ├── nightly_scoring.py   #定期スコアリングバッチ
    └── ...
```

### Frontend (`/frontend`)
Next.js (`.next`, `app/`) を全削除し、Vite + React + Tailwind CSS v4 に一本化。
```text
frontend/
├── index.html               # エントリーポイント
├── vite.config.ts           # Vite設定 (Port 3000, Proxy /api)
├── tailwind.config.cjs      # Tailwind設定 (v4互換)
├── postcss.config.cjs       # PostCSS設定
└── src/
    ├── main.tsx             # Reactルート
    ├── App.tsx              # ルーティング設定
    ├── contexts/
    │   └── AuthContext.tsx  # 認証状態管理 (JWT/LocalStorage)
    ├── pages/
    │   ├── Login.tsx        # ログイン画面
    │   └── Dashboard.tsx    # メインダッシュボード (MapLibre)
    └── api/
        └── client.ts        # Axios設定 (Interceptor対応)
```

---

## 3. 実装詳細（Phase 1-3）

### Phase 1: Gitリポジトリ浄化
- **手法**: `BFG Repo-Cleaner` を使用し、履歴から `.zip`, `.csv.gz`, `backend/*.csv` を物理削除。
- **結果**: 10GB超 → **16MB**。
- **インフラ**: `.gitignore` を更新し、今後大きなファイルが混入しないよう制御。

### Phase 2: DBスキーマとコードの整合性
- **課題**: `init.sql` が古く、Pythonコードが参照するカラム（`latitude` 等）が存在しなかった。
- **対応**:
    - `municipality_patterns` テーブル追加
    - `municipalities` テーブルへのカラム追加 (`dx_status`, `city_name` 等)
    - `scripts/update_lenovo_local.ps1` からハードコードされたAPIキーを削除（セキュリティ対応）

### Phase 3: 認証統合とフロントエンド一本化
- **課題**: 認証が Next.js Middleware に依存しており、Vite 側だけで完結していなかった。
- **対応**:
    1. **Backend**: FastAPI `routers/auth.py` が標準的な OAuth2 フローを提供。
    2. **Frontend**: `AuthContext` を実装。
        - ログイン時: `/api/auth/login` へ JSON で Credentials 送信。
        - トークン保存: `localStorage` に JWT を保存。
        - リクエスト: `client.ts` の Interceptor で `Authorization: Bearer` ヘッダーを自動付与。
    3. **Cleanup**: Next.js 関連ファイル（`.next`, `app` ディレクトリ）を完全削除。

---

## 4. 検証結果エビデンス

### ✅ 1. Gitサイズ確認
```bash
$ du -sh .git
16M	.git  # 成功
```

### ✅ 2. バックエンド統合テスト (Docker)
DBマイグレーション、認証、APIエンドポイントの疎通を確認。
```bash
$ docker compose exec api pytest
...
55 passed in 0.17s
```

### ✅ 3. BERT推論テスト
`nightly_scoring.py` にてダミーデータを用いた推論を実行。
```bash
$ docker compose exec api python3 scripts/nightly_scoring.py
...
✅ BERT model loaded.
✅ Batch Completed Successfully.
```

### ✅ 4. ログインフロー検証 (Browser)
1. 未ログインでアクセス → `/login` へリダイレクト
2. `admin@example.com` でログイン → 成功
3. ダッシュボード表示と地図描画 → 成功（下図参照）

![ダッシュボード表示確認](/Users/sonodera/.gemini/antigravity/brain/54064a3b-59c1-4f38-b193-950c576229e7/dashboard_view.png)

---

## 5. 意思決定ログ (Decision Log)

プロジェクトの将来を見据え、以下の技術選定を行いました。

| 項目 | 選択 | 理由 | 備考 |
|------|------|------|------|
| **フロントエンド統合** | **Vite採用** | SSR不要（BtoBダッシュボード用途）、ビルド高速化、Reactエコシステム最大活用 | Next.js特有の複雑性を排除 |
| **DB接続方式** | **psycopg2維持** | `asyncpg` への移行コスト過大、現状の同期処理で性能要件を満たせるため | 将来の非同期化へのパスは残す |
| **MLモジュール** | **BERT復旧** | ルールベースだけでは限界がある「本気度」判定のため。CPU推論で実用可能と判断 | 将来的な自前学習への布石 |

---

## 6. 残存リスクと対策

成功報告だけでなく、現状のリスクも透明化します。

| リスク項目 | 影響度 | 対策方針 |
|------------|--------|----------|
| **メモリ負荷** | 中 | BERTモデル展開時に約900MB消費。Lenovo Tiny (16GB) では問題ないが、Lightsail (1GB/2GB) ではOOMの危険あり。本番スペック選定に注意。 |
| **認証セキュリティ** | 低 | `localStorage` へのJWT保存はXSS脆弱性の影響を受ける。Phase 4以降で `HttpOnly Cookie` 化を検討推奨。 |
| **環境差異** | 中 | 開発(Mac/Docker) と本番(Lenovo/Windows) でのパス区切り文字や権限周りの差異。デプロイスクリプトで吸収済みだが継続監視が必要。 |

---

## 7. 性能ベンチマーク結果 (Docker環境)

BERT再有効化に伴うリソースインパクトを計測しました。

- **計測環境**: Docker (CPU Inference)
- **モデル**: `cl-tohoku/bert-base-japanese-whole-word-masking`

| 項目 | 結果 | 評価 |
|------|------|------|
| **モデルロード時間** | **6.81 sec** | アプリ起動時にのみ発生。許容範囲。 |
| **メモリ使用量** | **887.41 MB** | 予想より軽量。4GBメモリ環境でも動作可能。 |
| **推論速度** | **519.69 ms** | 1件あたり約0.5秒。夜間バッチ処理（数千件）でも数十分で完了するため実用上問題なし。 |

---

## 8. 技術ロードマップ (Next Steps)

単なるリファクタリングで終わらせず、プロダクトとしての進化プロセスを定義します。

- **Phase 4: 品質安定化** (今回完了直後)
    - スコア計算ロジックの回帰テストケース追加
    - 本番環境（Lenovo Tiny）へのデプロイと動作確認
- **Phase 5: 運用自動化**
    - CI/CDパイプライン導入 (GitHub Actions)
    - 夜間バッチの定期実行設定 (Cron/Systemd)
- **Phase 6: 観測性強化**
    - ログ基盤の整備 (Prometheus/Grafana検討)
    - エラー通知連携 (Slack/Teams)

---

## 9. 結論

本日のリファクタリングにより、プロジェクトは「プロトタイプ」から「運用可能なプロダクト」へと進化しました。
Gitリポジトリの軽量化、DBスキーマの整合性確保、そして最新のVite+FastAPI構成への移行が完了し、開発基盤が整いました。

以上、報告いたします。
