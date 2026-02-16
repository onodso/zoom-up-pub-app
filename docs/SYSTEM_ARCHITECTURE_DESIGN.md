# High-Level Architecture: Municipality Management OS (自治体経営OS)

## 🏗️ Core Concept
**「Zoomがないと成立しない業務基盤」の構築**
単なる通話・会議ツール（Utility）ではなく、自治体の業務KPIを可視化・改善する**成果創出エンジン（OS）**として機能する。

### 🛡️ Value Proposition
1.  **AIC (Phase 1)**: 無償の「業務効率化」ツール（メモ削減）
2.  **ZRA (Phase 2)**: 有償の「行政資産化」基盤（意思決定支援）

## 🧩 Architecture Overview

```mermaid
graph TD
    %% Input Layer
    subgraph Input_Layer [Unstructured Data (非構造化データ)]
        Call[Zoom Phone (Voice)] -->|API| Ingest
        Meeting[Zoom Meeting (Video)] -->|API| Ingest
        Tender[Tenders/Budgets] -->|Context| Ingest
    end

    %% Processing Layer (The "OS" Core)
    subgraph OS_Core [Administrative OS (行政経営基盤)]
        Ingest --> Classifier[1. Auto-Classification Engine]
        Ingest --> Scorer[2. Risk & Quality Scorer]
        
        Classifier -->|Categorize| Tax[税務・相談]
        Classifier -->|Categorize| Welfare[福祉・介護]
        Classifier -->|Categorize| Edu[教育・GIGA]
        
        Scorer -->|Analyze| Risk[Risk/Claims]
        Scorer -->|Analyze| Sentiment[Citizen Sentiment]
    end

    %% Presentation Layer
    subgraph Output_Layer [KPI Dashboard (経営可視化)]
        Tax & Welfare & Edu --> Dashboard[3. Municipality KPI Dashboard]
        Risk & Sentiment --> Dashboard
        
        Dashboard -->|Insight| Decision["政策立案・予算根拠\n(EBPM)"]
    end
    
    %% Security Layer
    subgraph Security_Boundary [LGWAN Separation]
        AIC_Data[AIC Summary] -->|Local/Secure| LGWAN[LGWAN Area]
        ZRA_Data[Full Transcript] -.->|Cloud/Auth| Internet[Internet Area]
    end
```

## 🧠 Decision Logic (The "Brain"): From Script to Empathy
**「生成AIによる汎用スクリプト」は排除する。**
代わりに、自治体の「基礎データ（地勢・人口・産業）」に基づき、彼らが抱える固有の痛み（Pain）を先回りして言語化する **「共感ロジック」** を実装する。

### 0. 基礎データプロファイリング (Geographic/Demographic Logic)
RESAS/E-Statデータを活用し、自治体の「物理的・社会的制約」を定義する。

| 特性タグ | 定義ロジック | 抱える痛み (Pain) | 刺さる提案 (Empathy) |
|---------|------------|-----------------|--------------------|
| **中山間地域** | 可住地面積率<30% | 「移動が困難」「災害時の孤立」 | **Zoom Phone (BCP)**: 「災害時でも庁舎外から対策本部機能を持続できますか？」 |
| **島しょ部** | 島嶼指定地域 | 「専門医・専門教員の不在」「出張費過多」 | **ZM + ZRA (医療/教育)**: 「海を越えて、本土と同じ質の教育・医療を届けましょう」 |
| **広域自治体** | 面積>500km² | 「職員の移動時間ロス」「支所間連携の希薄化」 | **Zoom Rooms (常時接続)**: 「支所を『隣の部屋』にして、移動時間を住民サービスに当てませんか？」 |
| **人口減少** | 人口増減率<-1.0% | 「職員不足」「兼務過多で回らない」 | **AIC + ZRA (省力化)**: 「人が減る中でサービスを維持するには、AIによる『1人3役』化が必要です」 |


## 🧠 Core Functions (The "Engine")

### 1. 自動分類エンジン (Auto-Classification)
通話・会議の内容を、行政固有のコンテキストで自動振り分け。
- **住民相談**: 福祉、税務、道路などの種別判定。
- **リスク検知**: 「怒鳴り声」「長時間保留」「繰り返し電話」の検知。
- **議会対応**: 答弁作成のための類似過去発言の検索。

### 2. 行政KPIスコアリング (Gov KPI Scorer)
漠然とした「会話」を「数値」に変換し、行政評価の指標とする。
- **一次解決率 (FCR)**: 窓口で即答できたか、転送されたか。
- **ネガティブ推移**: 市民の感情が対話を通じてどう変化したか。
- **Instruction/Inquiry Ratio**: 授業における「講義」と「探究」の比率（教育委員会向け）。

### 3. 経営ダッシュボード (Management Dashboard)
首長・幹部が「組織の状態」を把握するためのコックピット。
- **部署別負荷ヒートマップ**: どの課に問い合わせが集中しているか。
- **カスハラ予兆マップ**: 特定の市民/特定の内容でのトラブル頻度。
- **トレンド分析**: 「給付金」「ワクチン」など急上昇ワードの検知。

## 🚀 Adoption Strategy (Two-Stage Rocket)

### Phase 1: AIC (Efficiency) - "まずは無償で楽をする"
- **Target**: 現場職員
- **Value**: 「メモを取らなくていい」「要約が勝手に残る」
- **Action**: Zoom Phone APIで要約を自動取得し、日報の下書きを生成。
- **KPI**: 削減時間（例: 月間20時間/人）

### Phase 2: ZRA (Transformation) - "データを資産に変える"
- **Target**: 企画課・財政課・教育委員会
- **Value**: 「住民の声が見える」「政策の根拠になる」
- **Action**: 全文文字起こし＋ZRA分析で、行政課題（カスハラ、不登校、業務過多）の原因を特定。
- **KPI**: 住民満足度、対応品質スコア、政策立案数
