---
description: Antigravity IDE実装ルール v2.0
---

📌 Antigravity設定情報
Activation Mode
Always Active: このWorkspace内の全てのチャットで自動適用
ファイル保存場所: zoom-up-pub-app/.agent/rules/zoom-dx-rules.md
推奨AI設定
デフォルト: Gemini Pro 3 (High) ← 設計・調査・判断
コード実装: Claude Code ← トークンに余裕があれば優先
緊急時: GPT-4o ← Gemini/Claude障害時のフォールバック
🎯 Phase 1 最終成果物 (10日後)
動作要件
✅ ログイン可能 (onodso2@gmail.com / Zoom123!)
✅ 47都道府県地図表示 (Canvas2D)
✅ 都道府県クリックで色変化
✅ 50自治体の詳細データ表示
✅ ZRAスコアランキング表示 (0-100点, S/A/B/C/Dランク)
✅ エラーなし (コンソール・サーバーログ)
環境要件
✅ docker compose up で起動成功
✅ AWS Lightsailデプロイ準備完了
✅ テストカバレッジ 70%以上
除外項目 (Phase 2以降)
❌ 入札情報スクレイピング → 手動入力で代替
❌ Ollama AI推論 → ルールベース計算のみ
❌ PDF生成機能
❌ 全1,741自治体データ → 50自治体のみ
❌ Deck.gl → Canvas2Dのみ
❌ アニメーション効果
📂 プロジェクト構成 (厳守)
~/zoom-up-pub-app/
├── .env                          # 環境変数 (Git管理外)
├── docker-compose.yml            # ⚠️ 修正必要: TimescaleDB削除
├── ARCHITECTURE.md               # 設計書 (参照必須)
├── README.md                     # 起動手順
│
├── backend/
│   ├── .env                      # 🆕 作成必要
│   ├── main.py                   # FastAPIエントリポイント ✅
│   ├── requirements.txt          # ✅
│   │
│   ├── models/                   # 🆕 作成必要: SQLAlchemyモデル
│   │   ├── __init__.py
│   │   ├── municipality.py       # 自治体マスター
│   │   ├── score.py              # ZRAスコア
│   │   └── user.py               # ユーザー認証
│   │
│   ├── routers/                  # APIエンドポイント ✅
│   │   ├── auth.py               # 認証 (5KB) ✅
│   │   ├── municipalities.py     # 自治体API (5KB) ✅
│   │   ├── scores.py             # スコアAPI (3KB) ✅
│   │   └── collector.py          # データ収集 ✅
│   │
│   ├── services/                 # ビジネスロジック
│   │   ├── estat_client.py       # e-Stat API連携 ✅
│   │   ├── zra_calculator.py     # 🆕 ZRA計算ロジック
│   │   └── news_collector.py     # ✅
│   │
│   ├── db/
│   │   └── init.sql              # ⚠️ 修正必要: TimescaleDB拡張削除
│   │
│   └── tests/                    # 🆕 作成必要
│       ├── test_auth.py
│       ├── test_municipalities.py
│       └── test_scores.py
│
├── frontend/
│   ├── .env.local                # 🆕 作成必要
│   ├── package.json              # ⚠️ 修正必要: Deck.gl 9.1.0固定
│   │
│   ├── app/
│   │   ├── page.tsx              # メインページ (12KB) ✅
│   │   ├── login/
│   │   │   └── page.tsx          # ログイン
│   │   └── dashboard/
│   │       └── page.tsx          # ダッシュボード
│   │
│   └── components/
│       ├── map/
│       │   └── JapanMap.tsx      # ⚠️ Canvas2D化必要
│       ├── auth/
│       │   └── LoginForm.tsx
│       └── dashboard/
│           ├── ScoreCard.tsx
│           └── RankingTable.tsx
│
└── scripts/
    └── data/
        ├── import_municipalities.py  # 🆕 50自治体データ投入
        └── calculate_initial_scores.py  # 🆕 ZRA初期計算
🔧 技術スタック (固定版)
バックエンド (変更禁止)
CopyPython 3.11+
FastAPI 0.115+
PostgreSQL 16 (Alpine) ⚠️ TimescaleDB拡張不要
Redis 7 (Alpine)
SQLAlchemy 2.0+
psycopg2-binary 2.9+
pydantic 2.5+
python-jose[cryptography]
passlib[bcrypt]
pytest 7.4+
pytest-asyncio 0.21+
httpx 0.24+
フロントエンド (変更禁止)
Copy{
  "next": "14.2.0",
  "react": "18.3.0",
  "typescript": "5.3.3",
  "tailwindcss": "3.4.1",
  "@tailwindcss/forms": "0.5.7",
  "maplibre-gl": "3.6.2"
}
⚠️ Phase 1で使用しないライブラリ (Phase 2以降)
❌ deck.gl (Canvas2Dで代替)
❌ framer-motion (アニメーション不要)
❌ @deck.gl/layers
❌ @deck.gl/geo-layers
📋 コード品質基準
Python (backend)
Copy# ✅ 良い例
from typing import List, Optional
from sqlalchemy.orm import Session

def get_municipalities(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Municipality]:
    """
    自治体一覧を取得する
    
    Args:
        db: データベースセッション
        skip: スキップ件数
        limit: 取得件数上限
        
    Returns:
        自治体リストのリスト
        
    Raises:
        DatabaseError: DB接続エラー時
    """
    try:
        return db.query(Municipality).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Failed to fetch municipalities: {e}")
        raise DatabaseError("自治体データ取得失敗")

# ❌ 悪い例
def get_data(db, skip=0, limit=100):  # 型ヒントなし
    return db.query(Municipality).offset(skip).limit(limit).all()  # エラーハンドリングなし
Copy
TypeScript (frontend)
Copy// ✅ 良い例
interface Municipality {
  id: number;
  name: string;
  code: string;
  population: number;
  zra_score: number | null;
}

const fetchMunicipalities = async (): Promise<Municipality[]> => {
  try {
    const res = await fetch('/api/municipalities');
    if (!res.ok) throw new Error('Failed to fetch');
    return await res.json();
  } catch (error) {
    console.error('Error:', error);
    return [];
  }
};

// ❌ 悪い例
const fetchMunicipalities = async () => {  // 戻り値型なし
  const res = await fetch('/api/municipalities');  // エラーハンドリングなし
  return await res.json();
};
コード品質ルール
✅ 関数は50行以内
✅ ファイルは300行以内
✅ McCabe複雑度 ≤ 10
✅ 全ての関数に型ヒント (Python) / 型定義 (TS)
✅ Google Styleのdocstring (Python)
✅ try-except でエラーハンドリング
✅ ログ出力 (logger.info/error)
禁止事項
❌ print() デバッグ (logger使用必須)
❌ TODO FIXME コメント (Issue化)
❌ 未使用のimport
❌ マジックナンバー (定数化必須)
❌ グローバル変数
🧪 テスト基準
pytest (backend)
Copy# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login_success():
    response = client.post(
        "/api/auth/login",
        json={"email": "onodso2@gmail.com", "password": "Zoom123!"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_password():
    response = client.post(
        "/api/auth/login",
        json={"email": "onodso2@gmail.com", "password": "wrong"}
    )
    assert response.status_code == 401
カバレッジ要件
✅ 全体カバレッジ: 70%以上
✅ 認証API: 90%以上
✅ ZRAスコア計算: 80%以上
✅ DB操作: 75%以上
テスト項目 (最低3ケース/エンドポイント)
正常系 (200/201)
異常系 (400/401/404)
境界値テスト
🌿 Git運用ルール
ブランチ戦略
main          ← 本番デプロイ用 (保護)
└── develop   ← 開発統合用
    ├── feature/auth        ← 認証機能
    ├── feature/map         ← 地図機能
    ├── feature/scores      ← スコア機能
    └── feature/tests       ← テスト実装
コミットメッセージ
Copy[feat] 自治体詳細APIエンドポイント追加
[fix] ZRAスコア計算の丸め誤差修正
[refactor] DB接続プール設定最適化
[test] 認証APIのテストケース追加
[docs] README起動手順更新
[chore] requirements.txt依存関係更新
コミット頻度
✅ 機能完成ごと (1-2時間)
✅ 1日最低2コミット
✅ コミット前に git diff 確認
📅 Day-by-Day実装計画
Day 1-2: 環境整備・モデル実装
Copy# Git バックアップ
git add -A
git commit -m "[chore] Backup before Phase 1 implementation"
git branch backup-20260204

# 修正タスク
1. docker-compose.yml修正 (TimescaleDB削除)
2. frontend/package.json修正 (Deck.gl削除)
3. backend/models/ 作成 (municipality.py, score.py, user.py)
4. frontend/.env.local 作成
5. backend/db/init.sql修正

# 動作確認
docker compose down -v
docker compose build
docker compose up -d
docker compose logs -f

# Swagger UI確認
curl http://localhost:8000/docs
Day 2: データ投入スクリプト
Copy# scripts/data/import_municipalities.py
import pandas as pd
from sqlalchemy import create_engine

# 50自治体データ投入 (人口上位25 + DX先進25)
df = pd.read_csv('localgov_master_full.csv')
top_50 = df.nlargest(50, 'population')
# DB投入処理...
Day 2-3: 認証API実装
✅ /api/auth/login (POST)
✅ /api/auth/me (GET)
✅ JWT トークン発行 (12時間有効)
Day 3-4: 自治体・スコアAPI実装
✅ /api/municipalities (GET) ← 一覧
✅ /api/municipalities/{code} (GET) ← 詳細
✅ /api/scores/ranking (GET) ← ランキング
✅ /api/scores/{code} (GET) ← 個別スコア
Day 4: エラーハンドリング・統合テスト
✅ 全APIのエラーレスポンス統一
✅ ログ出力整備
✅ DB接続プール設定
Day 5-6: フロントエンド実装
✅ ログインフォーム
✅ Canvas2D日本地図 (47都道府県)
✅ 自治体詳細モーダル
✅ ZRAスコアカード
Day 7-8: テスト実装
✅ backend pytest (70%以上)
✅ frontend Jest (基本のみ)
Day 9: 統合テスト・デバッグ
✅ E2Eシナリオテスト
✅ パフォーマンステスト
Day 10: 本番デプロイ準備
✅ AWS Lightsail環境構築
✅ Cloudflare DNS設定
✅ HTTPS証明書設定
✅ 本番デプロイ
🤖 判断基準: Gensparkに質問すべきか?
自律判断OK (質問不要)
✅ バグ修正 (明らかなエラー)
✅ パフォーマンス最適化 (クエリ改善等)
✅ コードリファクタリング (可読性向上)
✅ テストケース追加
✅ ログ出力追加
✅ UI微調整 (色・余白等)
Gensparkに質問必須
❓ 設計変更 (APIエンドポイント追加等)
❓ 技術選定変更 (ライブラリ追加等)
❓ データモデル変更 (テーブル追加等)
❓ セキュリティ判断 (認証方式等)
❓ 要件解釈不明 (仕様不明確)
質問フォーマット
Copy### ❓ 質問: [タイトル]

**背景**:
現在Day Xの実装中、XXXの判断が必要です。

**問題**:
YYYの実装方法について、以下の選択肢があります。

**選択肢**:
A) 方法A (メリット: ..., デメリット: ...)
B) 方法B (メリット: ..., デメリット: ...)

**推奨**:
私はAを推奨します。理由は...

**質問**:
この判断で進めてよいですか?
📊 完了報告フォーマット
Day X 日次報告
Copy## Day X 完了報告 (YYYY-MM-DD)

### ✅ 完了タスク
- [x] タスク1 (所要時間: 2h)
- [x] タスク2 (所要時間: 3h)

### 🚧 進行中
- [ ] タスク3 (進捗: 50%)

### ⚠️ ブロッカー
- なし

### 📝 明日の予定
- タスク4実装
- タスク5実装

### 💾 コミット
- `abc1234` [feat] タスク1実装
- `def5678` [test] タスク2テスト追加

### ⏱️ 累積時間
Day X: 5h / 累計: 25h
Phase 1 最終報告
Copy## Phase 1 MVP 完了報告

### ✅ 達成項目
- [x] 動作要件: 全て達成
- [x] 環境要件: 全て達成
- [x] テストカバレッジ: 72%

### 📊 成果物
- アプリURL: https://zoom-dx-dev.example.com
- GitHub: https://github.com/xxx/zoom-dx-intelligence
- テストレポート: coverage-report.html

### 📈 統計
- 総コミット数: 48
- 総作業時間: 52h
- ファイル数: 67
- コード行数: 3,542行

### ⚠️ 既知の問題
- Issue #1: 地図の初期ロードが遅い (改善検討中)

### 🎯 次フェーズ提案
Phase 2で優先すべき機能:
1. Deck.gl導入 (200自治体対応)
2. PDF生成機能
3. NJSS API連携
🚨 緊急対応フロー
ブロッキング問題の定義
🔴 24時間以上作業停止の問題
🔴 設計書と矛盾する仕様
🔴 技術的に実装不可能な要件
🔴 セキュリティ脆弱性発見
緊急報告フォーマット
Copy## 🚨 ブロッキング問題

**発生日時**: YYYY-MM-DD HH:MM

**問題**: 
[問題の詳細]

**影響範囲**:
- Day X のタスクYが停止
- 納期への影響: Z日遅延見込み

**試した対処**:
1. 対処A → 結果: 失敗
2. 対処B → 結果: 失敗

**質問**:
この問題をどう解決すべきですか?

**添付**:
- エラーログ: error.log
- スクリーンショット: screenshot.png
📚 参照ドキュメント
プロジェクト内
✅ ARCHITECTURE.md (設計書) ← 最優先参照
✅ README.md (起動手順)
✅ 既存コード (backend/routers/*.py)
公式ドキュメント
✅ FastAPI Tutorial
✅ Next.js 14 Docs
✅ SQLAlchemy 2.0 Tutorial
✅ PostgreSQL 16 Docs
禁止参照
❌ Stack Overflow (品質不明)
❌ 個人ブログ (情報古い可能性)
❌ YouTube解説 (効率悪い)
✅ 最終チェックリスト
機能要件
 ログイン可能 (onodso2@gmail.com / Zoom123!)
 47都道府県地図表示 (Canvas2D)
 都道府県クリックで色変化
 50自治体の詳細データ表示
 ZRAスコアランキング表示
 エラーなし
非機能要件
 docker compose up 起動成功
 AWS Lightsailデプロイ可能
 テストカバレッジ 70%以上
 レスポンス 2秒以内
品質要件
 全ての関数に型ヒント
 全てのAPIにエラーハンドリング
 ログ出力整備
 Git履歴整理
デリバラブル
 動作URL提供
 README.md更新
 テストレポート
 最終報告書
🎯 成功定義
Phase 1は以下を満たしたら成功:

Gensparkが「これ、営業に見せられるね」と言う
プロジェクトオーナーが「OK、Phase 2行こう」と言う
10日以内に完成
📞 追加指示
あなた (Antigravity) はこのルールに従い、Phase 1を10日間で完成させてください。

質問は最大3回まで受け付けます。
それ以外は自律判断で実装を進めてください。

Good luck! 🚀

最終更新: 2026-02-04
作成者: Genspark AI
適用範囲: Workspace (zoom-up-pub-app プロジェクト限定)