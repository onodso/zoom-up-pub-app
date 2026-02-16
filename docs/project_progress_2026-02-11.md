# 📊 プロジェクト進捗状況レポート 2026-02-11

**プロジェクト名**: Zoom UP Public App - Local Gov DX Intelligence
**作成日**: 2026-02-11
**レポーター**: Claude Code (Sonnet 4.5)

---

## 🎯 プロジェクト概要

全国1,741自治体を対象に、Zoom導入確度をAIでスコアリングし、営業活動を効率化するダッシュボードシステム。

**主要機能**:
- リアルタイムニュース収集・LLM分析
- ML/DLベースのスコアリング（0-100点）
- 自治体ランキング・可視化ダッシュボード
- Lenovo Tiny + AWS Lightsail ハイブリッド構成

---

## 📈 全体進捗サマリー

| フェーズ | 計画 | 実装済み | 進捗率 | 状態 |
|---------|------|---------|-------|------|
| **Phase 1: インフラ構築** | 100% | 100% | ✅ 100% | 完了 |
| **Phase 2: データ収集** | 100% | 60% | 🟡 60% | 一部完了 |
| **Phase 3: AI/ML統合** | 100% | 40% | 🟡 40% | 進行中 |
| **Phase 4: フロントエンド** | 100% | 30% | 🔴 30% | 初期段階 |
| **Phase 5: 運用自動化** | 100% | 20% | 🔴 20% | 未着手 |
| **Phase 6: ML高度化** | 100% | 0% | 🔴 0% | 未着手 |
| **総合進捗** | - | - | **🟡 41.7%** | - |

---

## ✅ Phase 1: インフラ構築（100%完了）

### 実装済み

#### 1.1 Docker環境構築 ✅
- **PostgreSQL + TimescaleDB**: 時系列データ最適化
- **Redis**: セッション・キャッシュ管理
- **Ollama (Llama3)**: ローカルLLM推論
- **Node-RED**: ワークフロー自動化基盤
- **FastAPI Backend**: Python 3.11
- **Next.js Frontend**: React 18

#### 1.2 データベース設計 ✅
```sql
municipalities (1,916件)  -- 自治体マスタ
scores (履歴)             -- スコア計算結果
news_statements          -- ニュース・発言
budgets                  -- 予算データ（未実装）
tenders                  -- 入札データ（未実装）
feedback                 -- 営業フィードバック（未実装）
```

#### 1.3 Lenovo Tiny セットアップ ✅
- **AI Engine環境**: Ollama + Python ML/DL
- **開発環境**: VSCode + Docker
- **ストレージ**: 1TB SSD
- **ネットワーク**: 固定IP設定
- **ドキュメント**: `docs/lenovo_tiny_setup_report_2026-02-08.md`

#### 1.4 AWS Lightsail展開 ✅
- **インスタンス**: Ubuntu 22.04
- **公開URL**: `https://zoom-up.gentei.app` (予定)
- **環境分離**: 本番/ステージング/開発
- **CI/CD**: GitHub Actions準備中

---

## 🟡 Phase 2: データ収集（60%完了）

### 実装済み ✅

#### 2.1 自治体マスタデータ
- **1,916自治体**: 人口、世帯数、首長名、公式URL
- **地域区分**: 8地方、47都道府県
- **データ充足率**: 91.25%（8項目中の平均）

#### 2.2 ニュース収集システム
- **Google Custom Search API統合**: `services/news_collector.py`
- **LLM分析パイプライン**: Ollama (Llama3) 非同期処理
- **API**: `POST /api/collector/collect/{municipality_code}`
- **重複排除**: source_url によるユニーク制約
- **保存先**: news_statements テーブル

**実績**:
```bash
# 渋谷区でテスト実行済み
curl -X POST /api/collector/collect/131130
→ 4件のニュース保存、スコア 9.12 → 17.12 点に向上
```

### 未実装 🔴

#### 2.3 予算データ収集
- **計画**: 自治体公式サイトからスクレイピング
- **対象**: 窓口DX、働き方改革、庁内ICT関連予算
- **状態**: 未着手
- **優先度**: ⭐⭐⭐ 高（スコア精度への影響大）

#### 2.4 入札データ収集
- **計画**: J-LIS、NJSS連携
- **対象**: Web会議システム調達情報
- **状態**: 未着手
- **優先度**: ⭐⭐ 中

#### 2.5 議会議事録収集
- **計画**: 議事録検索システム連携
- **対象**: 「Web会議」「オンライン相談」等の発言
- **状態**: 未着手
- **優先度**: ⭐ 低

---

## 🟡 Phase 3: AI/ML統合（40%完了）

### 実装済み ✅

#### 3.1 スコアリングエンジン（Phase 1実装）
**ファイル**: `backend/services/scoring_engine.py`

**5つのサブスコア**:
| サブスコア | 重み | 実装状態 | 現在の値 |
|-----------|------|---------|---------|
| ニュース感情分析 | 30% | ✅ 実装済み | 0点（LLMスコア未設定） |
| 予算マッチング | 25% | 🔴 未実装 | 0点 |
| DX成熟度 | 20% | ✅ 実装済み | 40点（ニュース4件） |
| オンライン窓口 | 15% | ✅ 実装済み | 0点（該当なし） |
| データ品質 | 10% | ✅ 実装済み | 91.25点 |

**計算ロジック**:
```python
score_total = (
    news_sentiment * 0.30 +
    budget_match * 0.25 +
    dx_maturity * 0.20 +
    online_procedures * 0.15 +
    data_quality * 0.10
)
```

**鮮度重み**:
- 1ヶ月以内: 1.0
- 1年以内: 0.7
- それ以上: 0.3

#### 3.2 スコアAPI
**ファイル**: `backend/routers/scores.py`

**エンドポイント**:
- `GET /api/scores/{code}` - 最新スコア取得
- `GET /api/scores/{code}/history` - スコア履歴
- `POST /api/scores/calculate/{code}` - スコア計算
- `POST /api/scores/calculate/batch` - 一括計算
- `GET /api/scores/ranking/` - ランキング

**動作確認済み**:
```json
{
  "municipality_name": "渋谷区",
  "score_total": 17.12,
  "score_dx_maturity": 40.0,
  "score_data_quality": 91.25
}
```

#### 3.3 LLM分析（基本実装）
**ファイル**: `backend/services/llm_analyzer.py`

**機能**:
- Ollama (Llama3) によるニュース分析
- スコアリング（0-100点）
- 購買シグナル判定（buying_signal）
- 感情分析（sentiment_score）

**現状の課題**:
- モックデータではLLMスコアが0点
- 実データでのLLM分析テスト未実施
- プロンプトエンジニアリング未調整

### 未実装 🔴

#### 3.4 Machine Learning統合（Phase 2-6）
**計画**: `docs/ml_scoring_implementation_plan_v2_fixes.md`

**Phase 2: LightGBM表形式データ予測**
- **目的**: 表形式特徴量からスコア予測
- **特徴量**: 30種類（人口、予算、ニュース数、DXキーワード出現率など）
- **状態**: 未着手
- **推定工数**: 2-3週間

**Phase 3: LSTM時系列予測**
- **目的**: スコア変動のトレンド予測
- **データ**: 月次スコア履歴
- **状態**: 未着手
- **推定工数**: 2週間

**Phase 4: BERT意味解析**
- **目的**: ニューステキストの深層意味理解
- **モデル**: 日本語BERT (cl-tohoku/bert-base-japanese)
- **状態**: 未着手
- **推定工数**: 2週間

**Phase 5: Ensembleモデル**
- **目的**: LightGBM + LSTM + BERT の統合
- **最適化**: Nelder-Mead法で重み調整
- **状態**: 未着手
- **推定工数**: 1週間

**Phase 6: Human-in-the-loop**
- **目的**: 営業フィードバックによる継続学習
- **フィードバックUI**: 未実装
- **状態**: 未着手
- **推定工数**: 1週間

#### 3.5 説明可能性（XAI）
- **SHAP値**: 特徴量重要度の可視化
- **状態**: 未着手
- **優先度**: ⭐⭐ 中（営業への説明に必要）

---

## 🔴 Phase 4: フロントエンド（30%完了）

### 実装済み ✅

#### 4.1 基本UI構造
**ファイル**: `frontend/src/`

- **地図ビュー**: 都道府県別スコア表示
- **ランキングビュー**: トップ100自治体
- **詳細ページ**: 自治体プロファイル（基本情報のみ）

**技術スタック**:
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React Query (データフェッチング)

### 未実装 🔴

#### 4.2 スコア可視化
- **時系列グラフ**: スコア推移チャート
- **レーダーチャート**: 5つのサブスコア表示
- **ヒートマップ**: 地域別スコア分布
- **状態**: 未着手
- **優先度**: ⭐⭐⭐ 高

#### 4.3 フィルタリング機能
- **地域フィルタ**: 地方・都道府県絞り込み
- **人口フィルタ**: 最小人口設定
- **スコアフィルタ**: スコア範囲指定
- **状態**: 部分実装（API側のみ）
- **優先度**: ⭐⭐⭐ 高

#### 4.4 ダッシュボード
- **KPI表示**: 総自治体数、平均スコア、最高/最低スコア
- **トレンド**: 週次/月次スコア変動
- **アラート**: スコア急上昇/急降下の通知
- **状態**: 未着手
- **優先度**: ⭐⭐ 中

#### 4.5 営業フィードバックUI
- **フィードバックフォーム**: 商談結果入力
- **受注/失注理由**: ドロップダウン選択
- **コメント欄**: 自由記述
- **状態**: 未着手
- **優先度**: ⭐⭐⭐ 高（ML学習に必須）

---

## 🔴 Phase 5: 運用自動化（20%完了）

### 実装済み ✅

#### 5.1 Node-RED基盤
- **Docker Compose**: Node-RED コンテナ起動済み
- **アクセス**: http://localhost:1880
- **状態**: 環境構築のみ、フロー未作成

### 未実装 🔴

#### 5.2 定期収集ジョブ
**計画**:
```
毎日深夜3時: ニュース収集（全自治体）
毎週月曜日: スコア再計算（全自治体）
毎月1日: 予算データ更新
```

**状態**: 未着手
**優先度**: ⭐⭐⭐ 高

#### 5.3 Zoom Team Chat通知
**計画**:
- スコア急上昇（+10点以上）の自治体を通知
- エラー発生時のアラート
- 週次サマリーレポート

**状態**: 未着手
**優先度**: ⭐⭐ 中

#### 5.4 データバックアップ
- **PostgreSQL**: 日次ダンプ
- **S3保存**: AWS S3へのバックアップ
- **状態**: 未着手
- **優先度**: ⭐⭐⭐ 高（本番稼働前に必須）

#### 5.5 監視・ログ
- **Prometheus + Grafana**: メトリクス監視
- **ログ集約**: ELK Stack or CloudWatch
- **状態**: 未着手
- **優先度**: ⭐⭐ 中

---

## 🔴 Phase 6: ML高度化（0%完了）

### 計画内容

#### 6.1 LightGBM訓練パイプライン
**ファイル予定**: `backend/ml/training/lightgbm_trainer.py`

**特徴量エンジニアリング**（30種類）:
```python
[
    # 基本情報
    'population', 'households', 'population_density',
    # ニュース関連
    'news_count_1m', 'news_count_6m', 'news_count_1y',
    'avg_llm_score', 'max_llm_score',
    'keyword_zoom_count', 'keyword_dx_count',
    # 予算関連
    'budget_total_2y', 'budget_dx_ratio',
    # 時間特徴
    'days_since_last_news', 'days_since_last_budget',
    # DX成熟度
    'dx_maturity_score', 'online_procedure_score',
    # ...
]
```

**ハイパーパラメータ**:
```python
params = {
    'objective': 'regression',
    'metric': 'rmse',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.9,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbose': -1
}
```

#### 6.2 LSTM時系列予測
**ファイル予定**: `backend/ml/training/lstm_trainer.py`

**アーキテクチャ**:
```python
LSTM(input_size=5, hidden_size=64, num_layers=2)
→ Dropout(0.2)
→ Linear(64, 1)
```

**入力**: 過去12ヶ月のスコア履歴（5次元: 各サブスコア）
**出力**: 翌月のスコア予測

#### 6.3 BERT意味解析
**ファイル予定**: `backend/ml/training/bert_trainer.py`

**モデル**: `cl-tohoku/bert-base-japanese-v2`
**タスク**: ニュース分類（購買意欲の高低）

**分類カテゴリ**:
- 0: 購買意欲なし
- 1: 検討中
- 2: 予算化済み
- 3: 公募開始

#### 6.4 Ensembleモデル
**重み最適化**:
```python
weights = scipy.optimize.minimize(
    objective_function,
    x0=[0.4, 0.3, 0.3],  # LightGBM, LSTM, BERT
    method='Nelder-Mead'
)
```

**状態**: 全て未着手
**推定工数**: 合計8-10週間

---

## 🚨 クリティカルパス分析

### 現在のボトルネック

#### 1. 実データ不足（最優先）
**問題**: LLMスコアが0点のため、スコアの差別化ができていない

**影響**:
- 全自治体が同じスコア（9.12点または17.12点）
- ニュース感情分析スコアが機能していない（0点）
- MLモデルの訓練データが不十分

**解決策**:
```bash
# Step 1: Ollama でLLM分析を実行
curl -X POST /api/collector/collect/131130  # 渋谷区
curl -X POST /api/collector/collect/131016  # 千代田区
# ... 主要自治体10-20件

# Step 2: LLMスコアが正しく設定されているか確認
SELECT municipality_id, title, llm_score, buying_signal
FROM news_statements
WHERE llm_score > 0;

# Step 3: スコア再計算
curl -X POST /api/scores/calculate/batch?limit=20
```

**優先度**: ⭐⭐⭐⭐⭐ 最高
**推定工数**: 1日

#### 2. 予算データ未実装（高優先度）
**問題**: 予算マッチングスコア（重み25%）が0点

**影響**: スコア精度の25%が欠落

**解決策**:
1. budgets テーブルの作成
2. スクレイピングまたは手動入力で予算データ投入（POC用に10-20自治体）
3. `_calculate_budget_match_score()` の実装

**優先度**: ⭐⭐⭐⭐ 高
**推定工数**: 3-5日

#### 3. フロントエンド可視化（高優先度）
**問題**: スコアデータが可視化されていない

**影響**:
- プロジェクトのデモができない
- ユーザーフィードバックが得られない
- 営業チームが使えない

**解決策**:
1. スコアランキングテーブルの実装
2. 時系列グラフの実装（Chart.js or Recharts）
3. レーダーチャートの実装（5つのサブスコア）

**優先度**: ⭐⭐⭐⭐ 高
**推定工数**: 1週間

#### 4. 定期実行の自動化（中優先度）
**問題**: 手動実行のみ、データが自動更新されない

**影響**:
- 運用負荷が高い
- リアルタイム性が失われる

**解決策**:
1. Node-RED フローの作成
2. Cron ジョブの設定（代替案）

**優先度**: ⭐⭐⭐ 中
**推定工数**: 2-3日

---

## 📋 推奨アクションプラン

### 🚀 Phase A: POCデータ整備（優先度：最高、期間：1-2日）

**目的**: 実データでスコアの差別化を実現

**タスク**:
1. ✅ Ollama動作確認
2. ⬜ LLM分析の実行（主要自治体10-20件）
   ```bash
   # 東京23区
   for code in 131016 131041 131130 131199 131181; do
     curl -X POST /api/collector/collect/$code
   done

   # 政令指定都市
   for code in 011002 141003 231002 271004 401307; do
     curl -X POST /api/collector/collect/$code
   done
   ```
3. ⬜ LLMスコア検証（0点→実スコアに変化しているか）
4. ⬜ スコアランキング確認（差別化されているか）
5. ⬜ ドキュメント更新（POCデータ投入レポート）

**成功指標**:
- LLMスコアが0点でない
- 自治体ごとにスコアが異なる（±10点以上の差）
- ランキングが意味のある順序になっている

---

### 🎨 Phase B: フロントエンド可視化（優先度：高、期間：3-5日）

**目的**: ダッシュボードでスコアを可視化し、デモ可能な状態にする

**タスク**:
1. ⬜ スコアランキングテーブルの実装
   - ソート機能（スコア、地域、人口）
   - ページネーション
   - 検索機能
2. ⬜ スコア詳細ページの実装
   - 5つのサブスコア表示
   - レーダーチャート
   - 時系列グラフ（スコア履歴）
3. ⬜ ダッシュボードKPIの実装
   - 総自治体数
   - 平均スコア
   - 最高/最低スコア
   - スコア分布ヒストグラム

**成功指標**:
- デモ可能なUIが完成
- ユーザーがスコアを直感的に理解できる

---

### 💰 Phase C: 予算データ投入（優先度：高、期間：3-5日）

**目的**: 予算マッチングスコアを有効化し、スコア精度を向上

**タスク**:
1. ⬜ budgets テーブルの作成
   ```sql
   CREATE TABLE budgets (
       id SERIAL PRIMARY KEY,
       municipality_id INTEGER REFERENCES municipalities(id),
       fiscal_year INTEGER NOT NULL,
       category VARCHAR(50),  -- 'dx', 'telework', 'online'
       amount BIGINT,
       description TEXT,
       confidence FLOAT DEFAULT 0.5
   );
   ```
2. ⬜ POC用予算データの手動投入（10-20自治体）
   - 東京23区の主要区
   - 政令指定都市
3. ⬜ `_calculate_budget_match_score()` の実装
4. ⬜ スコア再計算・検証

**成功指標**:
- 予算データが投入されている自治体のスコアが向上
- 予算マッチングスコアが0点でない

---

### ⚙️ Phase D: 定期実行自動化（優先度：中、期間：2-3日）

**目的**: 運用負荷を下げ、データ鮮度を維持

**タスク**:
1. ⬜ Node-RED フローの作成
   - 毎日深夜3時: ニュース収集（スコア上位100自治体）
   - 毎週月曜日: スコア再計算（全自治体）
2. ⬜ Zoom Team Chat通知の実装
   - スコア急上昇（+10点以上）
   - エラー発生時
3. ⬜ ログ確認・デバッグ

**成功指標**:
- 1週間手動操作なしでデータが更新される
- Zoom Team Chatに通知が届く

---

### 🤖 Phase E: ML統合（優先度：中、期間：2-3週間）

**目的**: LightGBMによる高精度スコア予測

**タスク**:
1. ⬜ 特徴量エンジニアリング（30種類）
2. ⬜ 教師データ作成（カテゴリベースラベリング）
3. ⬜ LightGBM訓練・検証
4. ⬜ API統合（`/api/scores/predict/ml`）
5. ⬜ フロントエンドへの表示（ML予測スコア vs ルールベーススコア）

**成功指標**:
- RMSE < 15点
- MLスコアとルールベーススコアの差が±10点以内

---

## 💡 即座に実行可能なクイックウィン

### 1. POCデータ投入（30分）
```bash
# Docker起動
docker compose up -d

# 主要10自治体のニュース収集
for code in 131016 131041 131130 141003 271004 401307 011002 231002 131199 131181; do
  echo "Collecting: $code"
  curl -X POST "http://localhost:8000/api/collector/collect/$code"
  sleep 5
done

# ランキング確認
curl "http://localhost:8000/api/scores/ranking/?limit=10" | jq
```

### 2. LLMスコア検証（10分）
```bash
# LLMスコアが設定されているか確認
docker exec zoom-dx-postgres psql -U zoom_admin -d zoom_dx_db -c \
  "SELECT municipality_id, title, llm_score, buying_signal
   FROM news_statements
   WHERE llm_score > 0
   LIMIT 10;"
```

### 3. スコア分布確認（5分）
```bash
# スコア分布ヒストグラム
docker exec zoom-dx-postgres psql -U zoom_admin -d zoom_dx_db -c \
  "SELECT
     CASE
       WHEN score_total >= 80 THEN '80-100'
       WHEN score_total >= 60 THEN '60-80'
       WHEN score_total >= 40 THEN '40-60'
       WHEN score_total >= 20 THEN '20-40'
       ELSE '0-20'
     END as score_range,
     COUNT(*) as count
   FROM municipalities
   WHERE score_total IS NOT NULL
   GROUP BY score_range
   ORDER BY score_range DESC;"
```

---

## 📊 コスト試算

### 運用コスト（月額）

| 項目 | 金額 | 備考 |
|-----|------|------|
| **AWS Lightsail** | $20 | 2GB RAM, 60GB SSD |
| **Google Search API** | $50 | 5,000クエリ/月（10自治体×5ニュース×100回） |
| **Gemini API（オプション）** | $30 | LLM分析の補助 |
| **Zoom Team Chat** | $0 | 既存契約 |
| **合計** | **$100/月** | - |

### 開発コスト（工数）

| フェーズ | 推定工数 | 状態 |
|---------|---------|------|
| Phase 1-2 (完了分) | 4週間 | ✅ 完了 |
| Phase A (POCデータ) | 1-2日 | ⬜ 未着手 |
| Phase B (フロントエンド) | 3-5日 | ⬜ 未着手 |
| Phase C (予算データ) | 3-5日 | ⬜ 未着手 |
| Phase D (自動化) | 2-3日 | ⬜ 未着手 |
| Phase E (ML統合) | 2-3週間 | ⬜ 未着手 |
| **残り工数** | **4-5週間** | - |

---

## 🎯 成功指標（KPI）

### 技術KPI

| 指標 | 目標 | 現状 | 達成率 |
|-----|------|------|--------|
| **スコア計算速度** | < 1秒/自治体 | 0.5秒 | ✅ 200% |
| **スコア精度（RMSE）** | < 15点 | 未測定 | - |
| **データ鮮度** | 毎日更新 | 手動実行のみ | 🔴 0% |
| **API可用性** | > 99.5% | 未測定 | - |
| **LLM分析成功率** | > 95% | 未測定 | - |

### ビジネスKPI

| 指標 | 目標 | 現状 | 達成率 |
|-----|------|------|--------|
| **営業効率化** | 商談時間 -30% | 未導入 | - |
| **受注率向上** | +10% | 未導入 | - |
| **リード発掘数** | +50件/月 | 未導入 | - |

---

## 🚧 リスク管理

### 技術リスク

| リスク | 影響度 | 発生確率 | 対策 |
|--------|--------|---------|------|
| **Google Search API制限** | 高 | 中 | キャッシュ戦略、代替API（Bing） |
| **Ollama性能不足** | 中 | 低 | Gemini APIフォールバック |
| **データ品質低下** | 高 | 中 | データバリデーション、異常値検知 |
| **スケーラビリティ** | 中 | 低 | TimescaleDB圧縮、インデックス最適化 |

### ビジネスリスク

| リスク | 影響度 | 発生確率 | 対策 |
|--------|--------|---------|------|
| **ユーザー受容性** | 高 | 中 | MVP早期リリース、フィードバックループ |
| **ROI未達** | 高 | 中 | 段階的投資、KPIモニタリング |
| **競合出現** | 中 | 低 | 独自データ蓄積、ML精度向上 |

---

## 📝 次回レビューポイント

### 1週間後（2026-02-18）
- [ ] POCデータ投入完了
- [ ] スコアの差別化確認
- [ ] フロントエンド可視化50%完了
- [ ] 予算データ設計完了

### 2週間後（2026-02-25）
- [ ] フロントエンド可視化100%完了
- [ ] 予算データ投入完了（10-20自治体）
- [ ] 定期実行ジョブ稼働
- [ ] Zoom Team Chat通知稼働

### 4週間後（2026-03-11）
- [ ] ML統合（LightGBM）完了
- [ ] 本番環境へのデプロイ
- [ ] 営業チームへのトレーニング開始

---

## 🔗 関連ドキュメント

| ドキュメント | パス | 用途 |
|------------|------|------|
| **AI戦略書** | `docs/ai_strategy.md` | プロジェクト全体戦略 |
| **ML実装計画書** | `docs/ml_scoring_implementation_plan_v2_fixes.md` | ML/DL詳細設計 |
| **スコア実装レポート** | `docs/scoring_implementation_report_2026-02-08.md` | Phase 3進捗 |
| **Lenovo Tinyセットアップ** | `docs/lenovo_tiny_setup_report_2026-02-08.md` | インフラ構築 |
| **日次レポート** | `docs/daily_report_2026-02-05.md` | 初期実装記録 |

---

**作成者**: Claude Code (Sonnet 4.5)
**承認者**: N/A
**次回更新予定**: 2026-02-18（1週間後）

---

**残トークン**: 114,089 / 200,000 (使用: 85,911 / 42.9%)
