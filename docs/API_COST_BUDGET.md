# API利用コスト管理
## 月額予算: 5,000円以内（Must制約）

**目標:** 全APIコストを月5,000円以内に収める

---

## 📊 **使用中のAPI一覧とコスト**

### **1. Google Custom Search API**

#### **料金体系:**
- **無料枠:** 100クエリ/日（3,000クエリ/月）
- **有料:** $5 / 1,000クエリ（約750円）
- **上限:** 10,000クエリ/日

#### **現在の使用量（2026-02-15更新）:**
```
福岡市テスト: 3クエリ使用（2/14実施）
- DX news: 1クエリ
- Zoom deployments: 1クエリ
- Kasuhara: 1クエリ

月間累計: 3クエリ / 3,000クエリ（無料枠）
残り: 2,997クエリ
```

#### **想定使用量（全1,916自治体）:**
```
1,916自治体 × 3クエリ = 5,748クエリ

無料枠内: 3,000クエリ
有料: 2,748クエリ → $13.74 (約2,061円)
```

#### **コスト削減策:**
1. **Top 500自治体のみ収集** → 1,500クエリ（無料枠内）✅
2. **週1回実行** → 月4回 × 500 = 2,000クエリ（無料枠内）✅
3. **優先度別収集:**
   - High: Top 100自治体（毎週）
   - Medium: Top 500（隔週）
   - Low: 残り（月1回）

**推奨: Top 500自治体のみ → コスト: 0円**

---

### **2. e-Stat 公開データ**

#### **実績（2026-02-15）:**
- ✅ **公開Excelダウンロード方式を採用**（API使用せず）
- ✅ 1,915自治体の人口データ収集完了
- ✅ データ完全性: 20.4% → 99.96%
- **料金:** 完全無料（公開データ）
- **コスト:** 0円

#### **使用量:**
```
全1,916自治体 × 5データ項目 = 9,580クエリ
コスト: 0円 ✅
```

---

### **3. 国土地理院API**

#### **料金:**
- **完全無料**
- 制限: なし

#### **コスト: 0円 ✅**

---

### **4. Ollama (Llama 3.2 3B)**

#### **料金:**
- **ローカル実行 → 完全無料**
- 電気代のみ（微量）

#### **コスト: 0円 ✅**

---

### **5. その他API（既存）**

| API | 料金 | 月額コスト |
|-----|------|-----------|
| **e-Stat** | 無料 | 0円 |
| **MLIT-DPF** | 無料（既にキー取得済み） | 0円 |
| **gBizINFO** | 無料（既にキー取得済み） | 0円 |
| **PLATEAU** | 無料 | 0円 |
| **Gemini API** | 無料枠あり（使用予定なし） | 0円 |

---

## 💰 **総コスト見積もり**

### **Case 1: 保守的運用（推奨）**

| 項目 | クエリ数/月 | コスト |
|------|-----------|--------|
| Google Search (Top 500のみ) | 1,500 | **0円**（無料枠内） |
| e-Stat API | 10,000 | 0円 |
| 国土地理院 | 500 | 0円 |
| Ollama（ローカル） | 無制限 | 0円 |
| **合計** | - | **0円/月** ✅ |

**予算内: 5,000円 - 0円 = 5,000円の余裕**

---

### **Case 2: 積極的運用（全自治体）**

| 項目 | クエリ数/月 | コスト |
|------|-----------|--------|
| Google Search (全1,916) | 5,748 | **2,061円** |
| e-Stat API | 10,000 | 0円 |
| 国土地理院 | 2,000 | 0円 |
| Ollama（ローカル） | 無制限 | 0円 |
| **合計** | - | **2,061円/月** ✅ |

**予算内: 5,000円 - 2,061円 = 2,939円の余裕**

---

### **Case 3: 最大限活用（AI提案強化）**

| 項目 | クエリ数/月 | コスト |
|------|-----------|--------|
| Google Search (全自治体×週1) | 23,000 | **14,250円** ❌ **予算超過** |
| OpenAI GPT-4 API（代替案） | - | 10,000円 ❌ **予算超過** |

**結論: 外部有料AIは使用不可**

---

## ✅ **推奨運用プラン（月0円）**

### **データ収集スケジュール:**

#### **Week 1: 基盤データ（一回のみ）**
```
Day 1: e-Stat API → 全1,916自治体の人口・財政（0円）
Day 2: 国土地理院 → 緯度経度精度向上（0円）
Day 3: 総務省DX調査Excel → ダウンロード（0円）
```

#### **Week 2-4: ニュース収集（Top 500のみ）**
```
Week 2: Top 100自治体 × 3クエリ = 300クエリ
Week 3: 101-300位 × 3クエリ = 600クエリ
Week 4: 301-500位 × 3クエリ = 600クエリ

月間合計: 1,500クエリ（無料枠3,000以内）✅
```

#### **月次メンテナンス:**
```
毎月1日: Top 100のニュース更新（300クエリ）
毎月15日: 101-300のニュース更新（600クエリ）

月間合計: 900クエリ（無料枠内）✅
```

---

## 🚨 **コスト超過防止策**

### **1. クエリ数監視スクリプト**

```python
# backend/services/api_cost_monitor.py

import os
from datetime import datetime

class APICostMonitor:
    """API使用量を監視し、予算超過を防止"""

    MONTHLY_BUDGET = 5000  # 円
    GOOGLE_SEARCH_FREE_LIMIT = 3000  # クエリ/月
    GOOGLE_SEARCH_COST_PER_1000 = 750  # 円

    def __init__(self):
        self.query_count = 0
        self.cost = 0

    def log_query(self, api_name: str):
        """APIクエリをログ"""
        self.query_count += 1

        # Google Searchのコスト計算
        if api_name == "google_search":
            if self.query_count > self.GOOGLE_SEARCH_FREE_LIMIT:
                overage = self.query_count - self.GOOGLE_SEARCH_FREE_LIMIT
                self.cost = (overage / 1000) * self.GOOGLE_SEARCH_COST_PER_1000

        # 予算チェック
        if self.cost >= self.MONTHLY_BUDGET:
            raise Exception(f"❌ BUDGET EXCEEDED: {self.cost}円 > {self.MONTHLY_BUDGET}円")

    def get_summary(self):
        return {
            'total_queries': self.query_count,
            'free_queries_used': min(self.query_count, self.GOOGLE_SEARCH_FREE_LIMIT),
            'paid_queries': max(0, self.query_count - self.GOOGLE_SEARCH_FREE_LIMIT),
            'cost_yen': self.cost,
            'budget_remaining': self.MONTHLY_BUDGET - self.cost
        }
```

### **2. 自動停止機能**

```python
# Google Search実行前にチェック
monitor = APICostMonitor()

if monitor.query_count >= 3000:
    print("⚠️  Free tier limit reached. Stopping to avoid charges.")
    exit(0)
```

---

## 📈 **データ完全性 vs コスト**

| データ範囲 | Google Search使用 | 月額コスト | データ完全性 |
|-----------|------------------|-----------|-------------|
| **Top 100** | 300クエリ | **0円** | 75% |
| **Top 500** | 1,500クエリ | **0円** | 85% |
| **Top 1,000** | 3,000クエリ | **0円** | 90% |
| **全1,916** | 5,748クエリ | **2,061円** | 95% |

**結論: Top 500で十分（85%完全性、0円）**

---

## ✅ **最終推奨プラン**

### **目標:**
- **月額コスト: 0円**
- **データ完全性: 85%**
- **対象: Top 500自治体**

### **実装:**
```python
# 優先度別収集
HIGH_PRIORITY = 100  # 毎週更新
MEDIUM_PRIORITY = 500  # 隔週更新
LOW_PRIORITY = 1916  # 月1回（ニュースなし）

# Google Search使用制限
MAX_GOOGLE_QUERIES_PER_MONTH = 2900  # 安全マージン100
```

### **期待効果:**
- ✅ 予算内: 0円 < 5,000円
- ✅ 高品質データ: Top 500で85%カバー
- ✅ パターン判定: 十分な精度

---

## 🎯 **次のアクション**

1. **e-Stat API実装** → 0円、全自治体対象
2. **Google Search (Top 500)** → 0円、無料枠内
3. **総務省Excel** → 0円、手動ダウンロード

**全て予算内で実施可能！** ✅

---

**月5,000円予算は完全に守られます。**
