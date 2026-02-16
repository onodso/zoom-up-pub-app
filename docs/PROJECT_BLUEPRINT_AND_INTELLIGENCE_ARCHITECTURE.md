# Comprehensive Project Blueprint & Intelligence Architecture
**(自治体経営OS構築計画：全体像とデータサイエンス戦略)**

## 1. 🏗️ Grand Vision: Administrative Management OS
**「Zoomがないと成立しない行政基盤」の構築**

本システムは単なるSaaSの営業リスト作成ツールではなく、自治体が抱える「人口減少」「財政難」「業務過多」という構造的課題を、Zoom製品群（特にZRAによるデータ資産化）を通じて解決するための**「行政経営OS（オペレーティング・システム）」**です。

### 🧩 System Philosophy
- **From Selling to Standard**: 「Zoomを売る」のではなく「Zoomを行政インフラにする」。
- **From Script to Empathy**: 画一的なトークではなく、基礎データに基づく「共感」を提供する。
- **From Efficiency to Assetization**: 業務効率化(AIC)を入場券に、データ資産化(ZRA)を本丸とする。

---

## 2. 🗺️ High-Level Architecture (全体像)

```mermaid
graph TD
    subgraph Data_Layer [基盤データ層]
        Geo[地理・人口データ] -->|RESAS/E-Stat| Warehouse
        Tender[入札・調達データ] -->|KKJ API| Warehouse
        Budget[予算書・議事録] -->|PDF/Text| Warehouse
        Map[3D都市モデル] -->|PLATEAU| Warehouse
    end

    subgraph Intelligence_Layer [インテリジェンス層 (AI/ML Models)]
        Warehouse --> Profiler[1. Context Profiler<br>(Empathy Engine)]
        Warehouse --> Detector[2. Opportunity Detector<br>(Usage Classification)]
        Warehouse --> Predictor[3. Propensity Scorer<br>(Win Probability)]
    end

    subgraph Application_Layer [アプリケーション層]
        Profiler --> Strategy[戦略立案]
        Detector --> Strategy
        Predictor --> Strategy
        
        Strategy --> Dashboard[経営可視化ダッシュボード]
        Strategy --> MapView[3D都市空間可視化]
        Strategy --> Story[提案ストーリー生成]
    end
```

---

## 3. 🧠 Intelligence Architecture & Data Science Strategy
(コード・実装詳細ではなく、モデル選定・前処理・精度向上のロジックに特化して記述)

### 3.1. Context Profiler (Empathy Engine)
**目的**: 自治体の「痛み（Pain）」を地理的・社会的制約から推定し、共感の土台を作る。

- **Input Data**:
    - **RESAS**: 人口動態、産業構造、観光客数
    - **E-Stat**: 財政力指数、可住地面積、職員数、高齢化率
- **Methodology**: Rule-Based & Clustering (K-Means)
    - **前処理 (Preprocessing)**:
        - `StandardScaler` による特徴量の正規化（人口規模の影響を排除）。
        - 欠損値の補完（近隣自治体平均または回帰補完）。
    - **クラスタリングモデル**:
        - 自治体を「中山間・過疎」「島しょ部」「都市部・ドーナツ化」「観光依存」等のクラスターに分類。
    - **精度向上策**:
        - **Feature Engineering**: 「可住地面積あたりの職員数（激務度）」「人口1人あたりの民生費（福祉負担度）」など、**「痛み」に直結する派生変数**を作成。

### 3.2. Opportunity Detector (Usage Classification)
**目的**: 膨大な入札・予算情報から、具体的な「用途（Sales Playbook Patterns）」を特定する。

- **Input Data**:
    - 入札件名、仕様書（PDF）、議事録、補正予算書
- **Methodology**: NLP (Natural Language Processing)
    - **モデル選定**: 
        - **BERT (Japanese Pre-trained)**: 文脈理解が必要な「議事録」「予算書の意図」解析用。
        - **TF-IDF + LightGBM**: 高速な「入札件名」分類用。
    - **前処理 (Preprocessing)**:
        - **形態素解析 (MeCab/Sudachi)**: 自治体特有の単語（「プロポーザル」「債務負担行為」）を辞書登録。
        - **Stopwords除去**: 「業務」「委託」「等」などのノイズ除去。
    - **精度向上策**:
        - **Domain Adaptation**: 自治体特有の言い回し（例：「GIGAスクール」＝「端末整備」、「不登校」＝「適応指導」）を学習させるファインチューニング。
        - **Ensemble**: ルールベース（キーワード）とMLモデル（BERT）のハイブリッド判定で適合率重視（Precision-Recall Balance）。

### 3.3. Propensity Scorer (Win Probability)
**目的**: 「どの自治体がZoomを導入しやすいか」を受注確率（0.0-1.0）でスコアリングする。

- **Input Data**:
    - 過去の導入実績、Tech Stack（競合利用状況）、財政力、DX推進度
- **Methodology**: Predictive Modeling (Tableau Data)
    - **モデル選定**: **XGBoost / LightGBM / CatBoost**
        - 構造化データにおける最強の決定木ベースモデルを採用。
        - 欠損値の扱いがうまく、解釈可能性（Feature Importance）も高い。
    - **前処理**:
        - **Target Encoding**: 「都道府県」「政令指定都市」などのカテゴリ変数を数値化。
        - **Imbalanced Data対策**: 受注データは少ないため、**SMOTE**等でのオーバーサンプリング、または`scale_pos_weight`調整。
    - **精度向上策**:
        - **Cross-Validation**: 時系列を考慮したTimeSplit交差検証（過去データで学習し未来を予測）。
        - **SHAP値の活用**: 「なぜスコアが高いのか（例：財政力が高いから）」を営業担当に説明可能にする（Explainable AI）。

---

## 4. 🗺️ Visualization Strategy (PLATEAU Integration)
**目的**: 推論された「痛み」と「機会」を、視覚的・直感的に伝える。

- **3D City Model (LOD1/LOD2)**:
    - **地形の可視化**: 「山に囲まれている（＝電波困難）」「島である（＝移動困難）」を直感させる。
    - **施設の可視化**: 庁舎、支所、学校の位置関係を3D表示し、「移動の無駄」を可視化。
- **Heatmap Layer**:
    - 上記AIモデルで算出した「推奨度」や「リスクスコア」を建物・エリアに投影。

---

## 5. 🛡️ Adoption Roadmap (Sales Strategy)
「OS」としての導入を促す2段階戦略。

| Phase | Product | Value Proposition (Target) | Data Purpose |
|-------|---------|---------------------------|--------------|
| **Phase 1** | **AIC** (Free) | **Efficiency** (現場職員)<br>「メモ作成ゼロ」「残業削減」 | **Collection**<br>通話データの蓄積・構造化の開始 |
| **Phase 2** | **ZRA** (Paid) | **Transformation** (経営層)<br>「行政経営の可視化」「証拠に基づく政策」 | **Assetization**<br>蓄積データの分析・インサイト化 |

---

## 6. ✅ Next Steps
この全体像（Blueprint）に基づき、以下の順序で実装を進めます。

1.  **Phase 3: PLATEAU統合**:
    - 「Context Profiler」の地理的側面を3D地図上に実装。
    - 「中山間」「島しょ」の視覚的証明。
2.  **Phase 4: Intelligence Engine実装**:
    - ScorerおよびNLPモデルの構築。
    - 提案ロジックのAPI化。
