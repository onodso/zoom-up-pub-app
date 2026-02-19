# タスク一覧

- [x] Step 1: Git履歴浄化（.gitignore更新 + BFG + gc → 10GB→16MB）
- [x] Step 2: 不要ファイル整理（21個移動 + ログ削除）
- [x] Step 3: スコアエンジン統合（improved版→score_calculator.py）
- [x] Step 4: BERT凍結対応（importオプショナル化）
- [x] Step 5: 旧ダッシュボード削除（.next削除完了）
- [x] Step 6: requirements.txt整理（asyncpgコメントアウト）
- [x] Step 7: 技術スタックドキュメント作成（TECH_STACK.md）

## 追加検証・反映フェーズ
- [x] Step 8: スコアエンジン回帰テスト作成（37件PASS + バグ修正）
- [x] Step 9: Docker統合テスト（`docker compose up -d` + `pytest`）
- [x] Step 10: リモート反映（`git push --force-with-lease`）

## Phase 3: 認証統合と完全移行（完了）
- [x] Step 11: 認証フロー統合 (FastAPI Dependency + React Context)
- [x] Step 12: Next.js完全削除 (.next, middleware.ts等)
- [x] Step 13: BERT再有効化 (nightly_scoring.py)

## Phase 4: 本番デプロイと品質安定化
- [x] Step 14: デプロイスクリプト整備 (Windows/WSL2対応)
- [x] Step 15: 本番環境設定 (.env/Secrets)
- [x] Step 16: 本番DBマイグレーション
- [x] Step 17: 本番動作確認 (Lenovo Tiny - Remote)

## Phase 5: 運用自動化
- [x] Step 18: 定期実行設定 (Cron/Task Scheduler)
- [x] Step 19: CI/CDパイプライン構築 (GitHub Actions)
- [x] Step 20: ログ基盤整備 (Monitoring)
