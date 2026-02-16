# 徹底的なデータ収集計画
## Sales Playbook実現のための情報基盤構築

**目的:** 7つの提案パターンを適切に判断・実行できる情報基盤を構築する

---

## 📊 **現状の問題点**

### **Critical Gap分析:**

| セールスパターン | 必要な情報 | 現在の保有率 | 状態 |
|----------------|-----------|-------------|------|
| **1. ZP + AI Concierge (窓口DX)** | コールセンター有無、窓口数、市民相談件数 | 0% | 🚫 判断不可 |
| **2. ZP + AIC (働き方改革)** | 職員数、PBX有無、内線数、テレワーク率 | 0% | 🚫 判断不可 |
| **3. ZP + AIC + ZRA (カスハラ対策)** | 相談窓口、クレーム件数、録音義務 | 0% | 🚫 判断不可 |
| **4. ZM + ZR + ZRA (教育DX)** | 学校数、GIGAスクール進捗、遠隔授業 | 0% | 🚫 判断不可 |
| **5. All-in (完全DX)** | IT予算、Microsoft契約、庁内NW | 0% | 🚫 判断不可 |
| **6. ZM + AIC (会議効率化)** | 会議室数、Web会議ツール | 0% | 🚫 判断不可 |
| **7. ZCC + ZP + ZVA (奈良市モデル)** | 電話業務負荷、窓口待ち時間 | 0% | 🚫 判断不可 |

**結論:** 現在のデータでは**パターン判定が一切できない**状態

---

## 🎯 **必要なデータ項目（完全版）**

### **Category 1: 組織・職員情報**

| 項目 | 重要度 | 収集方法 | 用途 |
|------|--------|---------|------|
| 職員数（正規・非正規） | ★★★ | 自治体公式サイト/総務省統計 | Pattern 2, 5 |
| 部署数・組織図 | ★★☆ | 自治体公式サイト | Pattern 2, 5 |
| テレワーク実施率 | ★★★ | DX推進計画/プレスリリース | Pattern 2 |
| DX推進部署の有無 | ★★★ | 組織図 | Decision Readiness |
| 外部CIO・CDOの有無 | ★★☆ | プレスリリース | Decision Readiness |

### **Category 2: 市民サービス・窓口**

| 項目 | 重要度 | 収集方法 | 用途 |
|------|--------|---------|------|
| 窓口数（本庁・支所） | ★★★ | 公式サイト | Pattern 1, 7 |
| 年間来庁者数 | ★★☆ | 自治体統計 | Pattern 1, 7 |
| コールセンター有無 | ★★★ | 公式サイト | Pattern 1, 3 |
| 電話対応時間 | ★★☆ | 公式サイト | Pattern 7 |
| オンライン申請対応状況 | ★★★ | マイナポータル連携状況 | Pattern 5, 7 |
| 住民満足度調査結果 | ★☆☆ | 自治体公開資料 | Pattern 7 |

### **Category 3: IT基盤・インフラ**

| 項目 | 重要度 | 収集方法 | 用途 |
|------|--------|---------|------|
| 電話交換機（PBX）種類 | ★★★ | 入札情報/仕様書 | Pattern 2, 3 (重要!) |
| 内線数 | ★★★ | 入札情報 | Pattern 2 |
| Microsoft 365契約有無 | ★★★ | 入札情報 | 対Microsoft戦略 |
| Microsoft 365ライセンス種類（E3/E5） | ★★★ | 入札情報 | Blue Ocean判定 |
| Web会議ツール（Zoom/Teams/Webex） | ★★★ | 入札情報/プレスリリース | Pattern 6 |
| グループウェア種類 | ★★☆ | 入札情報 | Pattern 5 |
| 庁内ネットワーク更新時期 | ★★☆ | 入札情報 | Pattern 5 |
| クラウド利用方針 | ★★☆ | DX推進計画 | Pattern 5 |

### **Category 4: 教育委員会・学校**

| 項目 | 重要度 | 収集方法 | 用途 |
|------|--------|---------|------|
| 小学校数 | ★★★ | 教育委員会HP | Pattern 4 |
| 中学校数 | ★★★ | 教育委員会HP | Pattern 4 |
| GIGAスクール端末種類 | ★★★ | 教育委員会HP/プレスリリース | Pattern 4 |
| 遠隔授業実施状況 | ★★★ | 教育委員会HP | Pattern 4 (大分モデル) |
| 不登校児童数 | ★☆☆ | 文科省統計 | Pattern 4 |
| 学習支援ツール | ★★☆ | 教育委員会HP | Pattern 4 |

### **Category 5: 財政・予算**

| 項目 | 重要度 | 収集方法 | 用途 |
|------|--------|---------|------|
| 年間IT予算 | ★★★ | 予算書 | Feasibility |
| デジタル化予算 | ★★★ | DX推進計画/予算書 | Feasibility |
| 国庫補助金活用状況 | ★★☆ | 予算書 | Feasibility |
| 財政健全化指標 | ★★☆ | 総務省統計 | Feasibility |
| 主要ベンダー契約額 | ★☆☆ | 入札情報 | Pattern判定 |

### **Category 6: DX推進状況**

| 項目 | 重要度 | 収集方法 | 用途 |
|------|--------|---------|------|
| DX推進計画の有無 | ★★★ | 公式サイト | Leadership |
| スマートシティ構想 | ★★☆ | 公式サイト | Pattern 5 |
| デジタル田園都市国家構想採択 | ★★☆ | 内閣府公開情報 | Pattern 5 |
| オープンデータ公開状況 | ★☆☆ | data.go.jp | Pattern 5 |
| LINE公式アカウント運用 | ★★☆ | LINE検索 | Pattern 7 |
| AI・RPA導入状況 | ★★☆ | プレスリリース | Pattern 7 |

### **Category 7: 地域特性・課題**

| 項目 | 重要度 | 収集方法 | 用途 |
|------|--------|---------|------|
| 災害リスク（地震・台風・豪雨） | ★★☆ | 国土交通省ハザードマップ | Pattern 3 (BCP) |
| 過疎地域指定 | ★★☆ | 総務省 | Structural Pressure |
| 限界集落数 | ★☆☆ | 地域振興計画 | Pattern 5 |
| 観光入込客数 | ★☆☆ | 観光統計 | Pattern 5 |
| 産業構造（農業/製造/サービス比率） | ★☆☆ | 統計データ | - |

### **Category 8: 既存事例・先行導入**

| 項目 | 重要度 | 収集方法 | 用途 |
|------|--------|---------|------|
| Zoom導入実績（他自治体） | ★★★ | Webニュース検索 | Peer Pressure |
| 奈良市モデル認知度 | ★★☆ | - | Pattern 7 |
| 大分モデル認知度 | ★★☆ | - | Pattern 4 |
| カスハラ対策ニュース | ★★☆ | Webニュース検索 | Pattern 3 |

---

## 🔧 **データ収集手法**

### **Tier 1: 自動収集可能（優先度：最高）**

#### 1.1 総務省統計API
```python
# 収集可能データ:
- 人口・世帯数（実数値）
- 職員数
- 財政力指数
- 高齢化率
- 人口減少率
```

**実装:**
- e-Stat API連携（既に`ESTAT_APP_ID`設定済み）
- 毎月自動更新

---

#### 1.2 自治体公式サイトスクレイピング
```python
# 収集可能データ:
- 市長名・メッセージ
- 組織図（DX部署の有無）
- 窓口情報
- 教育委員会情報
- プレスリリース（DX関連）
```

**実装:**
- Beautiful Soup / Scrapy
- 週次更新

---

#### 1.3 入札情報サイト
```python
# 収集可能データ:
- IT関連契約（PBX、Microsoft 365、Web会議ツール）
- 契約金額
- ベンダー名
- 更新時期
```

**データソース:**
- 調達ポータル: https://www.chotatuportal.jp/
- 各自治体入札情報ページ

**実装:**
- 定期スクレイピング
- キーワード: "電話交換機", "PBX", "Microsoft", "Zoom", "Web会議"

---

#### 1.4 文部科学省 GIGAスクール関連
```python
# 収集可能データ:
- 学校数
- GIGA端末配布状況
- ネットワーク整備状況
```

**データソース:**
- 文科省公開データ
- 教育委員会HP

---

### **Tier 2: 半自動収集（優先度：高）**

#### 2.1 DX推進計画PDF解析
```python
# 収集可能データ:
- テレワーク目標・実績
- DX予算
- 重点施策
- KPI
```

**実装:**
- PDF自動ダウンロード
- OCR + GPT-4でデータ抽出

---

#### 2.2 ニュース・プレスリリース検索
```python
# 収集可能データ:
- Zoom導入事例
- カスハラニュース
- 先進事例（奈良市/大分モデル言及）
```

**実装:**
- Google News API
- 自治体名 + キーワード検索
- 自動要約・分類

---

### **Tier 3: 手動収集・推定（優先度：中）**

#### 3.1 電話ヒアリング（選択的）
- トップ100自治体のみ
- DX推進課への簡易調査
- 質問項目:
  - 現在のPBX種類
  - Microsoft 365契約有無
  - 最大の課題（窓口/テレワーク/教育）

---

## 📅 **データ収集スケジュール**

### **Phase 1: 基盤データ（1週間）**
- [ ] e-Stat API連携（人口・財政・職員数）
- [ ] 自治体公式サイトスクレイピング（市長・組織図）
- [ ] 教育委員会情報収集（学校数・GIGA）

### **Phase 2: IT基盤データ（2週間）**
- [ ] 入札情報スクレイピング（PBX・Microsoft 365）
- [ ] DX推進計画PDF収集・解析
- [ ] ニュース検索（Zoom導入事例）

### **Phase 3: 深堀りデータ（1週間）**
- [ ] 窓口・コールセンター情報
- [ ] 災害リスク・地域課題
- [ ] 先行事例マッピング

---

## 💾 **データベーススキーマ拡張**

### **新規テーブル: `it_infrastructure`**
```sql
CREATE TABLE it_infrastructure (
    city_code VARCHAR(6) PRIMARY KEY,
    pbx_vendor VARCHAR(100),          -- PBXベンダー (NEC/富士通/Cisco)
    pbx_extension_count INT,          -- 内線数
    microsoft_365_license VARCHAR(10), -- E3/E5/なし
    web_meeting_tool VARCHAR(50),     -- Zoom/Teams/Webex
    groupware VARCHAR(50),            -- サイボウズ/Microsoft/Google
    network_update_year INT,          -- 庁内NW更新年
    cloud_policy TEXT,                -- クラウド利用方針
    updated_at TIMESTAMP
);
```

### **新規テーブル: `education_info`**
```sql
CREATE TABLE education_info (
    city_code VARCHAR(6) PRIMARY KEY,
    elementary_schools INT,       -- 小学校数
    junior_high_schools INT,      -- 中学校数
    giga_device VARCHAR(50),      -- iPad/Chromebook/Windows
    remote_learning BOOLEAN,      -- 遠隔授業実施
    truancy_support BOOLEAN,      -- 不登校支援
    updated_at TIMESTAMP
);
```

### **新規テーブル: `citizen_service`**
```sql
CREATE TABLE citizen_service (
    city_code VARCHAR(6) PRIMARY KEY,
    office_count INT,                  -- 窓口数
    annual_visitors INT,               -- 年間来庁者数
    call_center BOOLEAN,               -- コールセンター有無
    online_application_rate FLOAT,     -- オンライン申請率
    line_official_account BOOLEAN,     -- LINE公式アカウント
    ai_chatbot BOOLEAN,               -- AIチャットボット
    updated_at TIMESTAMP
);
```

### **拡張: `municipalities.dx_status` (JSON)**
```json
{
    "dx_plan": true,
    "dx_budget_yen": 50000000,
    "telework_rate": 0.35,
    "smart_city": false,
    "digital_rural_city": true,
    "external_cio": "株式会社XXX",
    "major_challenges": ["窓口DX", "テレワーク"],
    "existing_zoom": false,
    "zoom_competitors": ["Teams"],
    "kasuhara_news": true
}
```

---

## 🚀 **実装優先順位**

### **Week 1: 即実装（パイロット改善）**
1. e-Stat API → 実人口データ取得
2. 市長名スクレイピング（全国）
3. DX推進計画PDF収集

### **Week 2-3: AI提案精度向上**
4. 入札情報スクレイピング → PBX/Microsoft判定
5. 教育委員会情報 → Pattern 4判定
6. ニュース検索 → Peer Pressure強化

### **Week 4: パターン自動判定実装**
7. データベース拡張
8. パターンマッチングロジック実装
9. AI提案プロンプト改善（パターン別）

---

## 📈 **期待される成果**

### **現在（データ完全性55%）:**
```
❌ パターン判定: 不可能
❌ 的確な提案: 不可能
⚠️  汎用提案のみ: 可能
```

### **Phase 1完了後（データ完全性75%）:**
```
⚠️  パターン判定: 部分的
✅ 基本的な提案: 可能
✅ スコア精度向上: 可能
```

### **Phase 2完了後（データ完全性90%）:**
```
✅ パターン判定: 高精度
✅ ピンポイント提案: 可能
✅ 対Microsoft戦略: 実行可能
```

---

## 🎯 **最終目標**

**各自治体について以下の判定が自動的にできる状態:**

1. **最適なZoom製品パターン（7種）**
2. **Microsoft対抗戦略（E3 Blue Ocean / E5 局所最適）**
3. **具体的な痛み点（窓口負荷/カスハラ/教育/BCP）**
4. **予算レンジ（小/中/大規模）**
5. **導入優先度（今すぐ/半年後/1年後）**

**これにより:**
- AI提案の質が劇的向上
- 営業効率が10倍に
- 成約率が3-5倍に

---

**次のステップ:** Week 1実装を開始しますか？
