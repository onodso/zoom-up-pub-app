# データサイエンス・機械学習を活用したスコア計算ロジック実装計画書

**作成日**: 2026-02-08
**作成者**: Claude Code (Sonnet 4.5)
**レビュー対象者**: 他のAI、プロジェクトマネージャー、データサイエンティスト
**プロジェクト**: Zoom UP Public App - Local Gov DX Intelligence

---

## 📋 Executive Summary（エグゼクティブサマリー）

### プロジェクトの目的
全国1,741自治体の「Zoom導入確度」を機械学習で予測し、営業活動の効率を最大化する。

### 実装のモットー
**"Garbage in, Garbage out"** - 質の高いデータ収集と分析を徹底し、信頼できる予測モデルを構築する。

### 技術スタック
- **Machine Learning**: Light GBM (主力モデル)
- **Deep Learning**: BERT（テキスト分析）、LSTM（時系列予測）
- **Feature Engineering**: pandas, numpy, scikit-learn
- **Explainability**: SHAP
- **Infrastructure**: Lenovo Tiny (AI Engine) + AWS Lightsail (Frontend)
- **Notification**: Zoom Team Chat

### 実装規模
- **フェーズ1-4（必須）**: 約1,000-1,500行、所要時間 6-8週間
- **フェーズ5（オプション）**: Deep Learning統合、追加2-3週間

---

## 🎯 Context（背景）

### 現状分析

#### ✅ 既に実装されている機能
1. **ニュース収集システム**
   - Google Custom Search APIによる自治体ドメイン（lg.jp, go.jp）限定検索
   - 実装場所: `backend/services/news_collector.py`

2. **LLM分析機能**
   - Ollama (Llama3) によるニュース個別スコアリング（0-100点）
   - 実装場所: `backend/services/llm_analyzer.py`
   - スコア基準:
     - 80-100: 予算承認、入札公告、Zoom導入言及
     - 60-79: 検討開始、パイロット、DX推進計画策定
     - 40-59: 一般的なDXトピック
     - 0-39: 無関係

3. **データベース構造**
   - PostgreSQL (TimescaleDB) - 時系列データ対応
   - 11テーブル（municipalities, scores, news_statements, budgets, tenders等）
   - 実装場所: `backend/db/init.sql`

#### ❌ 未実装の機能（今回実装する）
1. **自治体全体のスコア計算ロジック**
   - 現状: `municipalities.score_total`は仮データのみ
   - 目標: 複数のシグナル（ニュース、予算、入札）を統合したスコア

2. **特徴量エンジニアリング**
   - 非構造化データ（テキスト）から構造化データへの変換

3. **データ品質チェック機構**
   - "Garbage in, Garbage out"対策

4. **機械学習モデルの学習・推論パイプライン**

5. **Human-in-the-loopによる継続学習**

### AI戦略との対応（docs/ai_strategy.md）

| フェーズ | 内容 | 実装状況 |
|---------|------|---------|
| **Phase 1** | キーワード粗選別 | ✅ 実装済み |
| **Phase 2** | LLMスコアリング | ✅ 実装済み（個別ニュースのみ）|
| **Phase 3** | 構造化データへの変換 | ⚠️ **今回実装** |

### インフラ構成

```
┌─────────────────────────────────┐
│   AWS Lightsail (Tokyo Region)   │
│   - Next.js Frontend              │
│   - Cost: $10/month               │
└─────────────────────────────────┘
            ↕ Tailscale VPN
┌─────────────────────────────────┐
│   Lenovo Tiny (Home, 24/7)       │
│   - Ollama (Llama3)               │
│   - PostgreSQL (TimescaleDB)      │
│   - Redis Cache                   │
│   - FastAPI (Full)                │
│   - Node-RED                      │
│   - Cost: 電気代 ~$3/month         │
└─────────────────────────────────┘
```

---

## 🏗️ Architecture Design（アーキテクチャ設計）

### 多層MLスコアリングシステム

```
┌──────────────────────────────────────────────────────────────┐
│          Layer 1: Data Collection & Quality Check             │
│  Raw Data → Feature Engineering → "Garbage Out" Filter       │
│                                                               │
│  - 自治体Web、予算、入札、ニュースを収集                        │
│  - 欠損値チェック、鮮度チェック、異常値検出                      │
│  - 品質スコア < 0.7 の場合はアラート                           │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│          Layer 2: Feature Store (構造化データ)                 │
│                                                               │
│  ① Tabular Features（表形式特徴量）                            │
│     - population_log, population_density                     │
│     - dx_budget_trend, budget_allocation_ratio               │
│     - tender_count_1y, has_zoom_related_tender               │
│                                                               │
│  ② Text Features（テキスト特徴量）                             │
│     - sentiment_score_avg, positive_news_ratio               │
│     - news_embedding_768d (BERT)                             │
│                                                               │
│  ③ Time-Series Features（時系列特徴量）                        │
│     - score_trend_30d, news_frequency_30d                    │
│                                                               │
│  ④ Quality Features（品質特徴量）                              │
│     - data_completeness, data_freshness                      │
│     - source_reliability                                     │
│                                                               │
│  ⑤ Cost Estimations                                            │
│     - Google Custom Search API: 1日100件無料, 以降$5/1000req   │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│          Layer 3: ML/DL Models（3つのモデル）                  │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ① LightGBM（メインモデル）                            │   │
│  │    - 表形式データから導入確度を予測                    │   │
│  │    - 重み: 50%                                        │   │
│  │    - 特徴量重要度で説明可能性を担保                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ② LSTM（PyTorch）【Phase 5】                          │   │
│  │    - 時系列データから将来のスコア推移を予測            │   │
│  │    - 重み: 20%                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ③ BERT（テキスト分析）【Phase 5】                     │   │
│  │    - ニュース・予算書の意味的分析                      │   │
│  │    - 重み: 30%                                        │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│          Layer 4: Ensemble & Explainability                   │
│                                                               │
│  - 加重平均でスコアを統合                                      │
│  - 信頼度計算（モデル間の一致度）                              │
│  - SHAP values で説明生成                                     │
│  - 閾値超えでZoom Team Chat通知                               │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│          Layer 5: Score Output（0-100点）                     │
│                                                               │
│  {                                                            │
│    "score_total": 85.3,                                       │
│    "score_tabular": 82.0,                                     │
│    "score_timeseries": 88.0,                                  │
│    "score_text": 87.5,                                        │
│    "confidence": 0.92,                                        │
│    "feature_importance": {                                    │
│      "dx_budget_trend": 0.25,                                 │
│      "sentiment_score_recent": 0.18,                          │
│      ...                                                      │
│    },                                                         │
│    "explanation": "DX予算の増加トレンドとポジティブなニュース..." │
│  }                                                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 📊 Feature Engineering（特徴量エンジニアリング）

### 1. 構造化特徴量（Tabular Features）

#### A. 自治体基本情報（`municipalities`テーブル）

```python
# 人口・規模系（正規化必要）
population_log = log(population)  # 人口の対数変換（正規分布に近づける）
population_density = population / area_km2  # 人口密度
households_per_capita = households / population  # 世帯比率

# エリア特性（One-Hot Encoding）
region_encoded = [北海道=1/0, 東北=1/0, ..., 九州=1/0]  # 地方ダミー変数
prefecture_encoded = 47都道府県のカテゴリ変数（Target Encoding推奨）
```

**根拠**:
- 大規模自治体（東京23区、政令指定都市）は導入確度が高い傾向
- 地方によってデジタル化の進捗に差がある

#### B. 予算データ（`budgets`テーブル）

```python
# 直近3年間の予算推移
dx_budget_trend = (budget_2024 - budget_2022) / budget_2022  # DX予算の増減率
total_dx_budget_3y = sum([budget_2022, budget_2023, budget_2024])  # 累計予算
budget_allocation_ratio = dx_budget / total_budget  # DX予算比率
has_supplementary_budget = 1 if supplementary_budget > 0 else 0  # 補正予算フラグ

# カテゴリ別予算
budget_by_category = {
    '働き方改革': amount,
    '窓口DX': amount,
    'BCP': amount,
    '防災': amount,
    '庁内ICT': amount,
    '遠隔授業': amount
}

# 鮮度スコア
budget_recency_score = {
    1ヶ月以内: 1.0,
    1年以内: 0.5,
    それ以上: 0.2
}
```

**根拠**:
- 予算増額トレンドは導入意欲の強いシグナル
- 補正予算は緊急性・優先度が高い

#### C. 入札データ（`tenders`テーブル）

```python
# 入札実績
tender_count_1y = count(tenders WHERE date >= now() - 365 days)
tender_amount_total = sum(amount_yen)
days_since_last_tender = (today - max(tender_date))
has_zoom_related_tender = 1 if 'Zoom' in tender_title else 0
webconf_tender_count = count(tenders WHERE category='Web会議')
```

**根拠**:
- 入札活動の多さ = 積極的なDX推進
- Zoom関連の入札履歴は強い導入シグナル

#### D. 時系列特徴量（`scores`テーブル + TimescaleDB）

```python
# スコア推移
score_trend_30d = linear_regression_slope(scores[-30days])  # 30日間のトレンド
score_volatility = std_dev(scores[-30days])  # スコアの不安定性
score_momentum = score_today - score_7days_ago  # 勢い

# 活動頻度
news_frequency_30d = count(news_statements WHERE published_at >= now() - 30 days)
budget_update_frequency = count(budget_updates[-1year])
```

**根拠**:
- スコアが上昇トレンドの自治体は検討フェーズに入っている可能性
- ニュース言及頻度の高さは関心の高さを示す

### 2. テキスト特徴量（Text Features）

#### A. ニュース・発言（`news_statements`テーブル）

```python
# 既存LLM分析結果を活用
sentiment_score_avg = mean(sentiment_score WHERE published_at >= now() - 90 days)
sentiment_score_recent = mean(sentiment_score WHERE published_at >= now() - 30 days)
positive_news_ratio = count(sentiment > 0) / count(news)

# キーワード出現頻度（TF-IDF）
dx_keyword_score = tfidf_weighted_score([
    "DX", "デジタル化", "Web会議", "オンライン", "テレワーク",
    "Zoom", "遠隔", "リモート", "ビデオ会議"
])

# BERT embedding（Phase 5で実装）
news_embedding_768d = BERT.encode(concatenate(news_titles))
```

**根拠**:
- センチメントスコアがポジティブ = 導入に前向き
- キーワードの多様性と出現頻度は関心の深さを示す

#### B. 予算書・入札書類のテキスト（`extracted_text`フィールド）

```python
# LLMによる意図分類（Phase 2で実装）
budget_intent = LLM.classify(budget_text) → {検討中, 予算計上, 入札公告, 導入済み}
```

### 3. データ品質特徴量（Quality Features）

```python
# "Garbage in, Garbage out"対策
data_completeness = 1 - (null_count / total_fields)  # 欠損値の割合
data_freshness = {
    Sランク（1ヶ月以内）: 1.0,
    Aランク（1年以内）: 0.7,
    それ以下: 0.3
}
source_reliability = {
    自治体公式サイト: 1.0,
    J-LIS: 0.9,
    ニュースサイト: 0.7
}
```

**根拠**:
- データが古い・欠損が多い場合は予測精度が下がる
- 品質スコアを特徴量として含めることで、モデルが不確実性を考慮できる

---

## 🤖 Machine Learning Models（機械学習モデル）

### Model 1: LightGBM（メインモデル、Phase 1-4で実装）

#### 選定理由
1. **表形式データに最適**: 自治体の構造化データ（人口、予算、入札）に強い
2. **欠損値に強い**: データ不完全でも学習可能
3. **高速推論**: Lenovo TinyのCPUで十分高速（1,741自治体 < 1秒）
4. **説明可能性**: 特徴量重要度が明確 → 営業部門への説明が容易
5. **実績**: Kaggleコンペで多数の優勝実績

#### 実装詳細

```python
# backend/ml/models/score_predictor.py
import lightgbm as lgb
from sklearn.model_selection import train_test_split, cross_val_score

class MunicipalityScorePredictor:
    def __init__(self):
        self.model = lgb.LGBMRegressor(
            objective='regression',  # 回帰問題（0-100点）
            n_estimators=500,        # 決定木の数
            learning_rate=0.05,      # 学習率
            max_depth=7,             # 木の深さ（過学習防止）
            num_leaves=31,           # リーフ数
            min_child_samples=20,    # 最小サンプル数
            subsample=0.8,           # サンプリング比率
            colsample_bytree=0.8,    # 特徴量サンプリング
            reg_alpha=0.1,           # L1正則化
            reg_lambda=0.1,          # L2正則化
            random_state=42
        )

    def train(self, X_train, y_train, X_val=None, y_val=None):
        """教師データで学習"""
        # LightGBM 4.x対応: callbacksを使用
        callbacks = [
            lgb.early_stopping(stopping_rounds=50, verbose=100),
            lgb.log_evaluation(100)
        ]
        
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)] if X_val is not None else None,
            callbacks=callbacks
        )
        logger.info(f"Training completed. Feature importance saved.")

    def predict(self, X) -> np.ndarray:
        """スコア予測（0-100）"""
        raw_predictions = self.model.predict(X)
        return np.clip(raw_predictions, 0, 100)  # 0-100に制限

    def get_feature_importance(self) -> Dict[str, float]:
        """特徴量重要度の取得"""
        importances = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        # 降順ソート
        return dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
```

#### 学習データ作成戦略

**Phase 1: 初期教師データ（Cold Start）**

```python
# backend/ml/training/labeling.py
def create_initial_training_data():
    """初期教師データの作成"""

    # 1. 実績データから逆算
    labels = []

    # Zoom導入済み自治体（過去の営業記録から）
    adopted_municipalities = get_adopted_municipalities()
    for muni_id in adopted_municipalities:
        labels.append({'municipality_id': muni_id, 'score': random.uniform(90, 100)})

    # 問い合わせ履歴あり
    inquiry_municipalities = get_inquiry_municipalities()
    for muni_id in inquiry_municipalities:
        labels.append({'municipality_id': muni_id, 'score': random.uniform(70, 85)})

    # 2. ルールベースラベリング（離散的なランク付け）
    all_municipalities = get_all_municipalities()
    for muni in all_municipalities:
        if has_budget_approval(muni.id):
            # Sランク: 予算・入札あり
            labels.append({'municipality_id': muni.id, 'score_class': 'S', 'score_value': 95.0})
        elif has_dx_news(muni.id, keywords=['検討', 'パイロット']):
            # Aランク: 具体的検討
            labels.append({'municipality_id': muni.id, 'score_class': 'A', 'score_value': 75.0})
        elif has_dx_news(muni.id, keywords=['DX', 'デジタル']):
            # Bランク: 一般的関心
            labels.append({'municipality_id': muni.id, 'score_class': 'B', 'score_value': 50.0})
        else:
            # Cランク: 低関心
            labels.append({'municipality_id': muni.id, 'score_class': 'C', 'score_value': 20.0})

    return labels
```

**Phase 2: Human-in-the-loop（継続学習）**

```python
# backend/ml/feedback/feedback_loop.py
class FeedbackLoop:
    def record_ae_feedback(
        self,
        municipality_id: int,
        predicted_score: float,
        actual_outcome: str,  # 'won', 'lost', 'in_progress'
        ae_rating: int,       # 1-5段階評価（新たに追加）
        ae_comment: str
    ):
        """営業担当者（AE）のフィードバックを記録"""
        
        # AE評価をスコアに変換 (1=20, 2=40, 3=60, 4=80, 5=100)
        actual_score = ae_rating * 20.0

        # DBに保存（新しい教師データとして）
        self.db.insert('training_data', {
            'municipality_id': municipality_id,
            'score_label': actual_score,
            'predicted_score': predicted_score,
            'label_source': 'ae_feedback_v2',  # ソース区別
            'ae_comment': ae_comment,
            'created_at': datetime.now()
        })
        
        # ... (通知ロジックは継続)
```

### Model 2: LSTM（Phase 5で実装、オプション）

#### 用途
スコアの**将来予測**（7日後、30日後の見込み）

```python
# backend/ml/models/timeseries_predictor.py
import torch
import torch.nn as nn

class ScoreLSTM(nn.Module):
    def __init__(self, input_size=10, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=0.2
        )
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        # x: (batch, seq_len, features) - 例: (batch, 30日分, 10特徴量)
        lstm_out, _ = self.lstm(x)
        last_output = lstm_out[:, -1, :]  # 最後のタイムステップ
        score = self.fc(last_output)
        return torch.sigmoid(score) * 100  # 0-100にスケール
```

### Model 3: BERT（Phase 5で実装、オプション）

#### 用途
ニュース・予算書の**意味的分析**

```python
# backend/ml/models/text_analyzer.py
from transformers import AutoTokenizer, AutoModel

class BERTTextAnalyzer:
    def __init__(self, model_name="cl-tohoku/bert-base-japanese-v3"):
        """日本語BERTモデルの初期化"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()  # 推論モード

    def encode_text(self, text: str) -> np.ndarray:
        """テキストを768次元ベクトルに変換"""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            # [CLS]トークンの埋め込みを使用
            embedding = outputs.last_hidden_state[:, 0, :].numpy()

        return embedding.flatten()  # (768,)

    def semantic_similarity(self, text1: str, text2: str) -> float:
        """2つのテキストの意味的類似度（コサイン類似度）"""
        emb1 = self.encode_text(text1)
        emb2 = self.encode_text(text2)
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
```

---

## 🔗 Ensemble Strategy（アンサンブル戦略）

### アンサンブル計算

```python
# backend/ml/ensemble/score_calculator.py
class EnsembleScoreCalculator:
    def __init__(self):
        self.lgb_model = MunicipalityScorePredictor()
        self.lstm_model = ScoreLSTM()  # Phase 5
        self.bert_analyzer = BERTTextAnalyzer()  # Phase 5

        # 重み付け（初期値）
        # 将来的には Bayesian Optimization 等で最適化
        self.weights = {
            'tabular': 0.5,      # LightGBM
            'timeseries': 0.2,   # LSTM
            'text': 0.3          # BERT
        }

    def calculate_final_score(
        self,
        tabular_features: np.ndarray,
        timeseries_features: np.ndarray = None,
        text_features: List[str] = None
    ) -> Dict[str, Any]:
        """最終スコア計算"""

        # 各モデルの予測
        score_tabular = self.lgb_model.predict(tabular_features)[0]

        # Phase 1-4ではLightGBMのみ
        if timeseries_features is None or text_features is None:
            return {
                'score_total': float(score_tabular),
                'score_tabular': float(score_tabular),
                'confidence': 1.0,
                'model_weights': {'tabular': 1.0},
                'feature_importance': self.lgb_model.get_feature_importance()
            }

        # Phase 5: 全モデル統合
        score_timeseries = self.lstm_model(timeseries_features).item()
        score_text = self._calculate_text_score(text_features)

        # 加重平均
        final_score = (
            self.weights['tabular'] * score_tabular +
            self.weights['timeseries'] * score_timeseries +
            self.weights['text'] * score_text
        )

        # 信頼度計算（モデル間の一致度）
        confidence = self._calculate_confidence(
            score_tabular, score_timeseries, score_text
        )

        return {
            'score_total': float(final_score),
            'score_tabular': float(score_tabular),
            'score_timeseries': float(score_timeseries),
            'score_text': float(score_text),
            'confidence': float(confidence),
            'model_weights': self.weights,
            'feature_importance': self.lgb_model.get_feature_importance()
        }

    def _calculate_confidence(self, *scores) -> float:
        """モデル間の一致度と各モデルの不確実性から信頼度を計算"""
        std_dev = np.std(scores)
        
        # モデルごとの分散も考慮すべきだが、まずは簡易実装
        # 分散が大きい = モデル間で意見が割れている = 信頼度低
        base_confidence = max(0.0, 1.0 - (std_dev / 25.0)) # 厳しめに設定
        
        return base_confidence
```

---

## 🧪 Data Quality Check（"Garbage in, Garbage out"対策）

### データ品質チェック機構

```python
# backend/ml/data/data_quality.py
from sklearn.ensemble import IsolationForest

class DataQualityChecker:
    async def check_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """データ品質チェック (Async)"""

        quality_report = {
            'completeness': self._check_completeness(df),
            'consistency': self._check_consistency(df),
            'freshness': self._check_freshness(df),
            'outliers': self._detect_outliers(df),
            'duplicates': self._check_duplicates(df)
        }

        # 品質スコア計算（0.0-1.0）
        quality_score = (
            quality_report['completeness'] * 0.3 +
            quality_report['consistency'] * 0.3 +
            quality_report['freshness'] * 0.4
        )

        quality_report['overall_score'] = quality_score

        # 閾値を下回る場合はZoom Team Chatにアラート
        if quality_score < 0.7:
            await self._send_alert_to_zoom_chat(quality_report)

        return quality_report

    def _check_completeness(self, df: pd.DataFrame) -> float:
        """欠損値チェック"""
        total_values = df.shape[0] * df.shape[1]
        missing_values = df.isnull().sum().sum()
        return 1 - (missing_values / total_values)

    def _check_freshness(self, df: pd.DataFrame) -> float:
        """データ鮮度チェック（Sランク/Aランク）"""
        if 'updated_at' not in df.columns:
            return 0.5

        now = datetime.now()
        df['days_old'] = (now - pd.to_datetime(df['updated_at'])).dt.days

        # 鮮度スコア計算
        freshness_scores = df['days_old'].apply(lambda d:
            1.0 if d <= 30 else  # Sランク（1ヶ月以内）
            0.7 if d <= 365 else  # Aランク（1年以内）
            0.3  # それ以下
        )

        return freshness_scores.mean()

    def _detect_outliers(self, df: pd.DataFrame) -> List[Dict]:
        """異常値検出（Isolation Forest）"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) == 0:
            return []

        clf = IsolationForest(contamination=0.1, random_state=42)
        outliers = clf.fit_predict(df[numeric_cols].fillna(0))

        outlier_indices = df[outliers == -1].index.tolist()

        return [{
            'index': idx,
            'municipality_id': df.loc[idx, 'id'],
            'reason': '統計的異常値'
        } for idx in outlier_indices]

    async def _send_alert_to_zoom_chat(self, quality_report: Dict):
        """Zoom Team Chatにアラート送信"""
        message = f"""
⚠️ **データ品質アラート**

総合品質スコア: {quality_report['overall_score']:.2f}
- 完全性: {quality_report['completeness']:.2f}
- 一貫性: {quality_report['consistency']:.2f}
- 鮮度: {quality_report['freshness']:.2f}

異常値検出: {len(quality_report['outliers'])}件

対応が必要です。
        """
        await send_to_zoom_team_chat(message)
```

---

## 🚀 API Implementation（API実装）

### バッチ推論システム

```python
# backend/ml/inference/batch_predictor.py
class BatchScorePredictor:
    """全1,741自治体のスコアを夜間バッチで計算"""

    async def run_nightly_scoring(self):
        """毎晩3時に実行（Cron設定）"""
        start_time = datetime.now()
        logger.info("🌙 Nightly ML scoring started")

        # 1. データ収集
        municipalities = await self.fetch_all_municipalities()
        logger.info(f"Fetched {len(municipalities)} municipalities")

        # 2. 特徴量生成（並列処理）
        features_df = await self.generate_features_parallel(municipalities)
        logger.info(f"Generated features: {features_df.shape}")

        # 3. データ品質チェック
        quality_report = await self.quality_checker.check_data_quality(features_df)
        logger.info(f"Data quality score: {quality_report['overall_score']:.2f}")

        # 品質が低い場合は警告
        if quality_report['overall_score'] < 0.7:
            logger.warning("⚠️ Data quality below threshold!")

        # 4. MLスコア計算 (バッチ推論)
        # DataFrameごと渡して高速化
        tabular_matrix = features_df[self.feature_cols].values
        raw_scores = self.ensemble_calculator.lgb_model.predict(tabular_matrix)
        
        scores = []
        for idx, (muni_id, score_val) in enumerate(zip(features_df['id'], raw_scores)):
             scores.append({
                'municipality_id': muni_id,
                'score_total': float(score_val),
                'confidence': 1.0, # Phase 1-4
                'feature_importance': {} # 個別重要度は重いので省略または代表値のみ
            })

        # 5. DB保存
        await self.save_scores_to_db(scores)
        logger.info(f"Saved {len(scores)} scores to database")

        # 6. Zoom Team Chat通知
        duration = (datetime.now() - start_time).total_seconds()
        await self.notify_completion(duration, quality_report, len(scores))

        logger.info(f"✅ Nightly scoring completed in {duration:.2f}s")
```

### MLスコアAPI

```python
# backend/routers/ml_scores.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix='/api/ml-scores', tags=['ML Scoring'])

@router.get("/{municipality_id}")
async def get_ml_score(municipality_id: int, db: Session = Depends(get_db)):
    """MLモデルでスコアを計算（リアルタイム）"""

    # Redisキャッシュチェック
    cached = await redis.get(f"ml_score:{municipality_id}")
    if cached:
        logger.info(f"Cache hit for municipality {municipality_id}")
        return json.loads(cached)

    # 再計算
    service = MLScoreService()
    score = await service.calculate_score_realtime(municipality_id)

    # キャッシュ保存（1時間）
    await redis.setex(
        f"ml_score:{municipality_id}",
        3600,
        json.dumps(score)
    )

    return score

@router.post("/calculate/batch")
async def batch_calculate(
    region: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """全1,741自治体のスコアを一括計算（夜間バッチ用）"""

    service = MLScoreService()
    results = await service.batch_calculate_all_municipalities(region=region)

    # Zoom Team Chatへ通知
    await notify_zoom_team_chat({
        'total_processed': len(results),
        'average_score': np.mean([r['score_total'] for r in results]),
        'high_score_count': len([r for r in results if r['score_total'] > 70])
    })

    return {"status": "success", "processed": len(results)}

@router.get("/data-quality")
async def get_data_quality_report(db: Session = Depends(get_db)):
    """データ品質レポートを取得"""
    checker = DataQualityChecker()
    municipalities_df = await load_municipalities_with_features(db)
    report = checker.check_data_quality(municipalities_df)
    return report

@router.get("/feature-importance")
async def get_feature_importance():
    """特徴量重要度を取得（営業部門への説明用）"""
    predictor = MunicipalityScorePredictor()
    predictor.load_model()  # 最新モデルを読み込み
    importance = predictor.get_feature_importance()
    return importance
```

---

## 📅 Implementation Schedule（実装スケジュール）

| Week | Phase | タスク | 成果物 |
|------|-------|--------|--------|
| **1-2** | **Phase 1: 基盤構築** | - ディレクトリ構成作成<br>- データローダー実装<br>- 特徴量エンジニアリング（表形式のみ）<br>- データ品質チェック機構<br>- LightGBMベースラインモデル | - `backend/ml/` 全体<br>- データ品質レポート<br>- 初期モデル（accuracy未検証） |
| **3** | **Phase 2: 教師データ作成** | - 実績データからラベル生成<br>- ルールベースラベリング<br>- AEによる初期ラベリング（50自治体）<br>- 教師データDBテーブル作成 | - `training_data`テーブル<br>- 初期教師データ（~200件） |
| **4-5** | **Phase 3: MLモデル開発** | - LightGBM学習・評価<br>- ハイパーパラメータチューニング<br>- 交差検証<br>- 評価指標実装 | - 学習済みモデル（.pkl）<br>- 評価レポート（MAE, R2等） |
| **6** | **Phase 4: API・バッチ推論** | - MLスコアAPIエンドポイント<br>- バッチ推論システム<br>- Redisキャッシュ統合<br>- Zoom Team Chat通知 | - `/api/ml-scores` API<br>- Cron設定ファイル<br>- 夜間バッチ動作確認 |
| **7-8** | **Phase 5（オプション）** | - BERT統合<br>- LSTM時系列予測<br>- アンサンブル計算<br>- SHAP統合（説明可能性） | - 3モデルアンサンブル<br>- SHAP可視化 |

---

## 📦 Dependencies（依存ライブラリ）

### `backend/requirements.txt`（追加）

```txt
# === Machine Learning ===
scikit-learn>=1.3.0      # 特徴量エンジニアリング、評価指標
lightgbm>=4.1.0          # メインモデル（Gradient Boosting）

# === Deep Learning（Phase 5で必要） ===
torch>=2.1.0             # LSTM実装
transformers>=4.35.0     # BERT（日本語）
sentencepiece>=0.1.99    # BERT用トークナイザー

# === Data Science ===
pandas>=2.1.0            # データ処理
numpy>=1.24.0            # 数値計算

# === Model Interpretability（Phase 5で必要） ===
shap>=0.43.0             # SHAP values（説明可能性）

# === Utilities ===
joblib>=1.3.0            # モデルのシリアライズ
```

---

## ✅ Success Criteria（成功指標）

### KPI設定

| 指標 | 目標値 | 測定方法 | 重要度 |
|------|--------|---------|--------|
| **モデル精度（MAE）** | < 10点 | テストデータで評価 | 🔴 High |
| **上位20社の精度** | > 85% | 実際の問い合わせ率と比較 | 🔴 High |
| **データ品質スコア** | > 0.8 | "Garbage in, Garbage out"チェック | 🔴 High |
| **バッチ処理時間** | < 5分 | 1,741自治体の一括計算 | 🟡 Medium |
| **リアルタイム推論時間** | < 1秒 | 単一自治体スコア計算 | 🟡 Medium |
| **AE満足度** | > 4.0/5.0 | フィードバックアンケート | 🟢 Low |

### 検証手順

#### 1. ユニットテスト

```bash
# 特徴量エンジニアリングのテスト
pytest backend/ml/tests/test_feature_engineer.py

# LightGBMモデルのテスト
pytest backend/ml/tests/test_score_predictor.py

# データ品質チェックのテスト
pytest backend/ml/tests/test_data_quality.py
```

#### 2. 統合テスト

```bash
# 単一自治体のスコア計算
curl -X POST http://localhost:8000/api/ml-scores/calculate/131130

# バッチ計算
curl -X POST http://localhost:8000/api/ml-scores/calculate/batch

# データ品質レポート
curl http://localhost:8000/api/ml-scores/data-quality
```

#### 3. 本番環境テスト（Lenovo Tiny）

```bash
# SSH接続
ssh ubuntu@100.107.246.40  # Tailscale経由

# Dockerコンテナ確認
docker compose ps

# ログ確認
docker compose logs -f api

# 夜間バッチ手動実行
curl -X POST http://localhost:8000/api/ml-scores/calculate/batch
```

---

## ⚠️ Risks & Mitigation（リスクと対策）

| リスク | 影響度 | 対策 |
|--------|--------|------|
| **教師データ不足** | 🔴 High | - ルールベースラベリングで初期データ作成<br>- Human-in-the-loopで継続的に増やす<br>- 類似自治体からの転移学習 |
| **モデルの過学習** | 🟡 Medium | - 交差検証で汎化性能を確認<br>- Early Stopping + L2正則化<br>- テストデータで定期評価 |
| **Lenovo TinyのCPU不足** | 🟡 Medium | - LightGBM優先（軽量）<br>- BERTは必要時のみ使用<br>- バッチ処理は夜間実行 |
| **リアルタイム推論が遅い** | 🟢 Low | - Redisキャッシュ活用<br>- 夜間バッチで事前計算 |
| **データ品質の劣化** | 🔴 High | - 定期的な品質チェック<br>- 閾値下回り時にZoom Team Chatアラート<br>- 異常値自動検出（Isolation Forest） |
| **モデルドリフト** | 🟡 Medium | - AEフィードバックで検知<br>- 予測と実績の差分を監視<br>- 定期的な再学習 |

---

## 📌 Critical Files（重要ファイル一覧）

### 新規作成ファイル

| ファイルパス | 役割 | 行数（推定） |
|-------------|------|-------------|
| `backend/ml/data/data_quality.py` | データ品質チェック | ~200行 |
| `backend/ml/features/feature_engineer.py` | 特徴量エンジニアリング | ~300行 |
| `backend/ml/models/score_predictor.py` | LightGBMモデル | ~150行 |
| `backend/ml/training/trainer.py` | モデル学習 | ~200行 |
| `backend/ml/training/evaluator.py` | モデル評価 | ~100行 |
| `backend/ml/training/labeling.py` | 教師データ作成 | ~200行 |
| `backend/ml/ensemble/score_calculator.py` | アンサンブル計算 | ~150行 |
| `backend/ml/feedback/feedback_loop.py` | Human-in-the-loop | ~100行 |
| `backend/ml/inference/batch_predictor.py` | バッチ推論 | ~150行 |
| `backend/routers/ml_scores.py` | MLスコアAPI | ~150行 |
| **合計** | | **~1,700行** |

### 修正ファイル

| ファイルパス | 修正内容 | 行数（推定） |
|-------------|---------|-------------|
| `backend/requirements.txt` | ML/DLライブラリ追加 | +10行 |
| `backend/main.py` | MLスコアルーター追加 | +5行 |
| `backend/db/init.sql` | `training_data`テーブル追加 | +20行 |

### 参照ファイル（修正不要）

- `backend/services/llm_analyzer.py` - 既存LLM分析との統合点
- `backend/models/municipality.py` - 自治体データモデル
- `docs/ai_strategy.md` - AI戦略文書

---

## 📝 Summary（まとめ）

### 実装の目的

データサイエンス・機械学習・ディープラーニングを活用し、「Garbage in, Garbage out」の原則に基づいた質の高い自治体スコアリングを実現します。

### 技術的特徴

1. **LightGBMをメインモデル**とし、表形式データに最適化
2. **特徴量エンジニアリング**で非構造化データを構造化
3. **データ品質チェック**で低品質データを除外
4. **Human-in-the-loop**で継続的に改善
5. **Zoom Team Chat通知**でアラート・レポート配信

### 実装規模

- **Phase 1-4（必須）**: 約1,700行、所要時間 6週間
- **Phase 5（オプション）**: Deep Learning統合、追加2-3週間

### 期待される効果

1. **営業活動の効率化**: 上位20社の精度 > 85%
2. **データドリブンな意思決定**: 特徴量重要度で説明可能
3. **継続的な改善**: AEフィードバックで精度向上

---

## 🔍 Review Checklist（レビューチェックリスト）

このドキュメントをレビューする際は、以下の観点で評価してください。

### Technical Feasibility（技術的実現可能性）
- [ ] LightGBMは本当に最適なモデルか？他のアルゴリズム（XGBoost、CatBoost）も検討したか？
- [ ] Lenovo TinyのCPU/RAMで1,741自治体のバッチ処理は現実的か？
- [ ] BERT/LSTMの統合は本当に必要か？コスト対効果は？

### Data Quality（データ品質）
- [ ] "Garbage in, Garbage out"対策は十分か？
- [ ] 異常値検出の手法（Isolation Forest）は適切か？
- [ ] 鮮度スコアの閾値（1ヶ月、1年）は妥当か？

### Labeling Strategy（ラベリング戦略）
- [ ] 初期教師データの作成方法は現実的か？
- [ ] ルールベースラベリングの基準は適切か？
- [ ] Human-in-the-loopのフィードバックループは機能するか？

### Evaluation Metrics（評価指標）
- [ ] MAE < 10点は達成可能か？厳しすぎないか？
- [ ] 上位20社の精度 > 85%はビジネス要件に合っているか？
- [ ] 他に追加すべき評価指標はないか？

### Implementation Schedule（実装スケジュール）
- [ ] 6-8週間のスケジュールは現実的か？
- [ ] Phase 1-4で本当に必要十分か？Phase 5は本当にオプションか？
- [ ] リスクバッファは考慮されているか？

### Cost & Infrastructure（コスト・インフラ）
- [ ] Lenovo Tinyで十分なパフォーマンスが出るか？
- [ ] Zoom Team Chat通知の頻度は適切か（スパムにならないか）？
- [ ] モデルのバージョン管理戦略は？

---

**レビュー依頼先**: 他のAI、プロジェクトマネージャー、データサイエンティスト
**レビュー期限**: 2026-02-15まで
**次回アクション**: レビューフィードバックを反映後、Phase 1実装開始

**残トークン**: 95,494 / 200,000 tokens
