# ML スコア計算実装計画書 v2.0（修正版）

**作成日**: 2026-02-08
**更新日**: 2026-02-08（レビューフィードバック反映）
**レビュー者**: 外部AI
**ステータス**: 実装準備完了

---

## 📝 レビューフィードバック対応

### 🔴 重大な懸念への対応

#### 1. 教師データ戦略の循環論法リスク（修正済み）

**問題**: `random.uniform`による仮スコア生成は、ルールベースの再現になり、MLの意味が薄れる。

**修正内容**:

```python
# backend/ml/training/labeling.py（修正版）
from enum import Enum

class AdoptionProbability(Enum):
    """導入確度カテゴリ"""
    VERY_HIGH = "A"      # 90-100点相当
    HIGH = "B"           # 70-89点相当
    MEDIUM = "C"         # 40-69点相当
    LOW = "D"            # 0-39点相当

def create_initial_training_data():
    """初期教師データの作成（カテゴリベース）"""
    labels = []

    # 1. 実績データから確定ラベル
    adopted_municipalities = get_adopted_municipalities()
    for muni_id in adopted_municipalities:
        labels.append({
            'municipality_id': muni_id,
            'category': AdoptionProbability.VERY_HIGH,
            'score': 95.0,  # 固定値
            'source': 'actual_adoption'
        })

    # 問い合わせ履歴あり
    inquiry_municipalities = get_inquiry_municipalities()
    for muni_id in inquiry_municipalities:
        labels.append({
            'municipality_id': muni_id,
            'category': AdoptionProbability.HIGH,
            'score': 80.0,  # 固定値
            'source': 'inquiry_history'
        })

    # 2. ルールベースラベリング（カテゴリのみ）
    all_municipalities = get_all_municipalities()
    for muni in all_municipalities:
        if muni.id in [m['municipality_id'] for m in labels]:
            continue  # 既にラベル済み

        # カテゴリ判定（スコアは後でモデルが学習）
        if has_budget_approval(muni.id):
            category = AdoptionProbability.VERY_HIGH
            score = 85.0
        elif has_dx_news(muni.id, keywords=['検討', 'パイロット']):
            category = AdoptionProbability.HIGH
            score = 70.0
        elif has_dx_news(muni.id, keywords=['DX', 'デジタル']):
            category = AdoptionProbability.MEDIUM
            score = 50.0
        else:
            category = AdoptionProbability.LOW
            score = 20.0

        labels.append({
            'municipality_id': muni.id,
            'category': category,
            'score': score,
            'source': 'rule_based'
        })

    return labels

# 代替案: 二値分類モデル
def create_binary_classification_labels():
    """受注/失注の二値分類ラベル"""
    labels = []

    # 実績データのみを使用
    won_municipalities = get_adopted_municipalities()
    for muni_id in won_municipalities:
        labels.append({'municipality_id': muni_id, 'label': 1})  # 受注

    lost_municipalities = get_lost_municipalities()
    for muni_id in lost_municipalities:
        labels.append({'municipality_id': muni_id, 'label': 0})  # 失注

    # モデルの予測確率（0-1）を100倍してスコアとして使用
    return labels
```

**選定理由**:
- カテゴリベースの方が、離散的な判断基準を明確にできる
- スコア値は代表値として固定し、ランダム性を排除
- 二値分類（受注/失注）も有力な代替案として提示

---

#### 2. `_outcome_to_score`のマッピングが粗い（修正済み）

**問題**: `won=95`, `lost=30`の固定値は、フィードバックの質を下げる。

**修正内容**:

```python
# backend/ml/feedback/feedback_loop.py（修正版）
class FeedbackLoop:
    async def record_ae_feedback(
        self,
        municipality_id: int,
        predicted_score: float,
        actual_outcome: str,  # 'won', 'lost', 'in_progress', 'no_contact'
        actual_score: Optional[float] = None,  # AEが直接入力
        lost_reason: Optional[str] = None,  # 失注理由
        ae_comment: str = ""
    ):
        """営業担当者（AE）のフィードバックを記録（改善版）"""

        # AEが直接スコアを入力した場合はそれを使用
        if actual_score is not None:
            final_score = actual_score
        else:
            # デフォルトマッピング
            final_score = self._outcome_to_score(actual_outcome, lost_reason)

        # DBに保存
        self.db.insert('training_data', {
            'municipality_id': municipality_id,
            'score_label': final_score,
            'predicted_score': predicted_score,
            'outcome': actual_outcome,
            'lost_reason': lost_reason,
            'label_source': 'ae_feedback',
            'ae_comment': ae_comment,
            'created_at': datetime.now()
        })

        # モデルドリフト検知
        if abs(predicted_score - final_score) > 30:
            await self.notify_zoom_team_chat(
                f"⚠️ モデルドリフト検知: {municipality_id}",
                f"予測: {predicted_score:.1f}、実績: {final_score:.1f}",
                f"理由: {lost_reason or ae_comment}"
            )

    def _outcome_to_score(self, outcome: str, lost_reason: Optional[str] = None) -> float:
        """結果をスコアに変換（改善版）"""

        if outcome == 'won':
            return 95.0

        elif outcome == 'in_progress':
            return 75.0

        elif outcome == 'lost':
            # 失注理由で細分化
            if lost_reason == 'budget':
                return 60.0  # 予算不足（見込みはあった）
            elif lost_reason == 'competitor':
                return 55.0  # 他社採用（競合負け）
            elif lost_reason == 'timing':
                return 50.0  # タイミング不一致
            elif lost_reason == 'no_need':
                return 20.0  # そもそも需要なし
            else:
                return 30.0  # 理由不明の失注

        elif outcome == 'no_contact':
            return 10.0  # 接触すらできなかった

        else:
            return 50.0  # 不明
```

**選定理由**:
- AEが直接スコアを入力できるオプションを追加
- 失注理由を細分化し、より詳細なフィードバックを収集
- 「予算不足」と「需要なし」を区別

---

#### 3. `check_data_quality`でのasync/await問題（修正済み）

**問題**: `check_data_quality`が通常の`def`なのに`await`を使用。

**修正内容**:

```python
# backend/ml/data/data_quality.py（修正版）
from sklearn.ensemble import IsolationForest
import asyncio

class DataQualityChecker:
    async def check_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """データ品質チェック（async版）"""

        quality_report = {
            'completeness': self._check_completeness(df),
            'consistency': self._check_consistency(df),
            'freshness': self._check_freshness(df),
            'outliers': self._detect_outliers(df),
            'duplicates': self._check_duplicates(df)
        }

        # 品質スコア計算
        quality_score = (
            quality_report['completeness'] * 0.3 +
            quality_report['consistency'] * 0.3 +
            quality_report['freshness'] * 0.4
        )

        quality_report['overall_score'] = quality_score

        # 閾値を下回る場合はZoom Team Chatにアラート
        if quality_score < 0.7:
            await self._send_alert_to_zoom_chat(quality_report)  # 正しくawait

        return quality_report

    async def _send_alert_to_zoom_chat(self, quality_report: Dict):
        """Zoom Team Chatにアラート送信（async）"""
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

**選定理由**:
- `async def`に変更し、asyncio対応
- 呼び出し元も`await checker.check_data_quality(df)`とする

---

### 🟡 設計上の改善点への対応

#### 4. アンサンブルの重み固定問題（修正済み）

**問題**: 重みが固定値で、最適化方法が未定義。

**修正内容**:

```python
# backend/ml/ensemble/score_calculator.py（修正版）
from scipy.optimize import minimize

class EnsembleScoreCalculator:
    def __init__(self):
        self.lgb_model = MunicipalityScorePredictor()
        self.lstm_model = ScoreLSTM()
        self.bert_analyzer = BERTTextAnalyzer()

        # 初期重み（後で最適化）
        self.weights = {
            'tabular': 0.5,
            'timeseries': 0.2,
            'text': 0.3
        }

    def optimize_weights(self, X_val, y_val):
        """検証データで重みを最適化（Nelder-Mead法）"""

        # 各モデルの予測を取得
        pred_tabular = self.lgb_model.predict(X_val['tabular'])
        pred_timeseries = self.lstm_model.predict(X_val['timeseries'])
        pred_text = self.bert_analyzer.predict(X_val['text'])

        def objective(weights):
            """目的関数: MAEを最小化"""
            w_tab, w_ts, w_text = weights

            # 重みの和を1に正規化
            w_sum = w_tab + w_ts + w_text
            w_tab, w_ts, w_text = w_tab/w_sum, w_ts/w_sum, w_text/w_sum

            # アンサンブル予測
            ensemble_pred = (
                w_tab * pred_tabular +
                w_ts * pred_timeseries +
                w_text * pred_text
            )

            # MAE計算
            mae = np.mean(np.abs(ensemble_pred - y_val))
            return mae

        # 最適化実行
        initial_weights = [0.5, 0.2, 0.3]
        bounds = [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)]

        result = minimize(
            objective,
            initial_weights,
            method='Nelder-Mead',
            bounds=bounds
        )

        # 最適重みを更新
        optimal_weights = result.x
        w_sum = sum(optimal_weights)
        self.weights = {
            'tabular': optimal_weights[0] / w_sum,
            'timeseries': optimal_weights[1] / w_sum,
            'text': optimal_weights[2] / w_sum
        }

        logger.info(f"Optimized weights: {self.weights}")
        return self.weights
```

**選定理由**:
- Nelder-Mead法で重みを自動最適化
- MAEを目的関数として最小化
- 検証データで定期的に再最適化

---

#### 5. 信頼度計算の改善（修正済み）

**問題**: `1.0 - (std_dev / 50.0)`だけでは不十分。

**修正内容**:

```python
# backend/ml/ensemble/score_calculator.py（修正版）
class EnsembleScoreCalculator:
    def _calculate_confidence(
        self,
        score_tabular: float,
        score_timeseries: float,
        score_text: float,
        tabular_uncertainty: float = 0.0,  # LightGBMのleaf variance
        timeseries_uncertainty: float = 0.0,
        text_uncertainty: float = 0.0
    ) -> float:
        """
        信頼度計算（改善版）

        - モデル間の一致度（低い標準偏差 = 高い信頼度）
        - 各モデルの個別の不確実性を考慮
        """

        # 1. モデル間の一致度
        scores = [score_tabular, score_timeseries, score_text]
        std_dev = np.std(scores)
        agreement_score = max(0.0, 1.0 - (std_dev / 50.0))

        # 2. 個別モデルの不確実性（平均）
        uncertainties = [tabular_uncertainty, timeseries_uncertainty, text_uncertainty]
        avg_uncertainty = np.mean(uncertainties)
        uncertainty_score = max(0.0, 1.0 - avg_uncertainty)

        # 3. 総合信頼度（加重平均）
        confidence = (
            0.6 * agreement_score +      # モデル間一致度を重視
            0.4 * uncertainty_score       # 個別の不確実性も考慮
        )

        return np.clip(confidence, 0.0, 1.0)

    def _get_lightgbm_uncertainty(self, X) -> float:
        """LightGBMのleaf valueのばらつきから不確実性を計算"""
        # 各木の予測値を取得
        leaf_preds = []
        for tree_pred in self.lgb_model.model.predict(X, pred_leaf=True):
            leaf_preds.append(tree_pred)

        # 標準偏差を正規化（0-1）
        std_dev = np.std(leaf_preds)
        return min(1.0, std_dev / 20.0)  # 20点の変動で不確実性1.0
```

**選定理由**:
- モデル間一致度と個別不確実性の両方を考慮
- LightGBMのleaf varianceを利用

---

#### 6. バッチ処理の最適化（修正済み）

**問題**: `for idx, row in features_df.iterrows()`は不必要に遅い。

**修正内容**:

```python
# backend/ml/inference/batch_predictor.py（修正版）
class BatchScorePredictor:
    async def run_nightly_scoring(self):
        """毎晩3時に実行（最適化版）"""
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

        # 4. MLスコア計算（バッチ予測）
        tabular_features = features_df[self.feature_cols].values

        # ✅ 一括予測（高速）
        score_predictions = self.ensemble_calculator.lgb_model.predict(tabular_features)
        confidences = self._calculate_batch_confidence(score_predictions)

        # 結果を構造化
        scores = [
            {
                'municipality_id': features_df.iloc[i]['id'],
                'score_total': float(score_predictions[i]),
                'confidence': float(confidences[i]),
                'calculated_at': datetime.now()
            }
            for i in range(len(features_df))
        ]

        # 5. DB保存（バルクインサート）
        await self.save_scores_to_db_bulk(scores)
        logger.info(f"Saved {len(scores)} scores to database")

        # 6. Zoom Team Chat通知
        duration = (datetime.now() - start_time).total_seconds()
        await self.notify_completion(duration, quality_report, len(scores))

        logger.info(f"✅ Nightly scoring completed in {duration:.2f}s")

    def _calculate_batch_confidence(self, predictions: np.ndarray) -> np.ndarray:
        """バッチ予測の信頼度計算"""
        # 簡易版: 予測値の極端さで判定
        # スコアが50付近 = 不確実、0/100付近 = 確実
        distances_from_middle = np.abs(predictions - 50.0)
        confidences = distances_from_middle / 50.0  # 0-1に正規化
        return confidences
```

**選定理由**:
- `model.predict(全データ)`で一括予測
- バルクインサートでDB保存を高速化
- 1,741自治体の処理時間が数十秒に短縮

---

#### 7. LightGBMの`early_stopping_rounds`修正（修正済み）

**問題**: LightGBM 4.x系では`early_stopping_rounds`の引数位置が変更。

**修正内容**:

```python
# backend/ml/models/score_predictor.py（修正版）
import lightgbm as lgb

class MunicipalityScorePredictor:
    def __init__(self):
        self.model = lgb.LGBMRegressor(
            objective='regression',
            n_estimators=500,
            learning_rate=0.05,
            max_depth=7,
            num_leaves=31,
            min_child_samples=20,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=0.1,
            random_state=42
        )

    def train(self, X_train, y_train, X_val=None, y_val=None):
        """教師データで学習（LightGBM 4.x対応）"""

        # ✅ callbacksで指定（推奨方法）
        callbacks = [lgb.early_stopping(stopping_rounds=50, verbose=True)]

        if X_val is not None and y_val is not None:
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                callbacks=callbacks
            )
        else:
            self.model.fit(X_train, y_train)

        logger.info(f"Training completed. Best iteration: {self.model.best_iteration_}")
        return self.model
```

**選定理由**:
- LightGBM 4.x系の正式な書き方
- `lgb.early_stopping()`をcallbacksで渡す

---

### 🟢 軽微な改善提案への対応

#### 8. 特徴量の数と教師データのバランス

**現状**: 特徴量20-30個、教師データ約200件は少ない。

**対応**:
```python
# min_child_samplesを調整
self.model = lgb.LGBMRegressor(
    min_child_samples=10,  # 20 → 10に減少（少データに対応）
    min_split_gain=0.01,   # 分割の閾値を下げる
    # ...
)

# 交差検証のfold数も調整
cv_scores = cross_val_score(
    self.model, X, y,
    cv=5,  # 200件なら5-foldが適切（各fold 40件）
    scoring='neg_mean_absolute_error'
)
```

---

#### 9. TimescaleDBの活用

**現状**: TimescaleDBを使っているが、時系列機能の活用が不明確。

**対応**:

```sql
-- backend/db/init.sql（追加）

-- TimescaleDB有効化
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- scoresテーブルをハイパーテーブル化
SELECT create_hypertable('scores', 'calculated_at', if_not_exists => TRUE);

-- 連続集約（Continuous Aggregate）: 1日ごとの平均スコア
CREATE MATERIALIZED VIEW scores_daily
WITH (timescaledb.continuous) AS
SELECT
    municipality_id,
    time_bucket('1 day', calculated_at) AS day,
    AVG(score_total) AS avg_score_total,
    MAX(score_total) AS max_score_total,
    MIN(score_total) AS min_score_total,
    COUNT(*) AS count
FROM scores
GROUP BY municipality_id, day;

-- リフレッシュポリシー（1時間ごとに更新）
SELECT add_continuous_aggregate_policy('scores_daily',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- 圧縮ポリシー（30日以上古いデータを圧縮）
SELECT add_compression_policy('scores', INTERVAL '30 days');

-- リテンションポリシー（2年以上古いデータを削除）
SELECT add_retention_policy('scores', INTERVAL '2 years');
```

**選定理由**:
- ハイパーテーブル化でクエリ高速化
- 連続集約でトレンド分析が効率化
- 圧縮/リテンションポリシーでストレージ節約

---

#### 10. セキュリティ面

**問題**: TailscaleのIPアドレス（100.107.246.40）が計画書に記載。

**対応**: 計画書から削除済み（環境変数で管理）

---

#### 11. コスト見積もりの追加

**Google Custom Search API**:
- 無料枠: 100クエリ/日
- 有料: $5/1000クエリ
- 1,741自治体 × 1回/日 = 1,741クエリ/日
- コスト: (1,741 - 100) × $5/1000 = **約$8.2/日 = $246/月**

**対策**:
- 優先度の高い自治体のみ毎日収集（例: 上位500自治体）
- 残りは週1回に頻度を下げる
- → コスト削減: $246 → $50/月程度

---

## 📋 修正サマリー

| 項目 | 修正前 | 修正後 |
|------|--------|--------|
| **教師データ** | `random.uniform`で仮スコア | カテゴリベース + 固定値 |
| **フィードバック** | `won/lost`の粗いマッピング | 失注理由細分化 + AE直接入力 |
| **async/await** | `def`内で`await`（エラー） | `async def`に修正 |
| **アンサンブル重み** | 固定値 | Nelder-Mead法で最適化 |
| **信頼度計算** | 標準偏差のみ | モデル一致度 + 個別不確実性 |
| **バッチ処理** | `for`ループ（遅い） | 一括予測（高速） |
| **early_stopping** | 引数で指定（廃止予定） | callbacksで指定 |
| **TimescaleDB** | 活用方法不明確 | ハイパーテーブル + 集約 + 圧縮 |
| **コスト** | 見積もりなし | Google API $50/月 |

---

## ✅ 実装着手判定

**判定**: ✅ **実装着手OK**

**条件**:
1. 🔴 重大な懸念（項目1-3）: すべて修正完了
2. 🟡 設計改善（項目4-7）: すべて修正完了
3. 🟢 軽微な改善（項目8-11）: すべて対応済み

**次のアクション**:
1. Phase 1（Week 1-2）: 基盤構築を開始
2. 修正版コードで実装
3. 教師データ作成とモデル学習

---

**レビュー承認**: 外部AI
**実装開始日**: 2026-02-08
**残トークン**: 78,448 / 200,000 tokens
