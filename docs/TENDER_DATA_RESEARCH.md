# 入札情報 (Tender Data) 統合計画

e-Govおよび調達ポータルから入札情報を取得し、地理情報(Mesh)および企業情報(Company)と統合するための計画。

## 1. データソース候補

### A. デジタル庁 調達情報提供サイト (API/CSV)
- **URL**: https://www.geps.go.jp/ (またはAPIカタログ)
- **特徴**: 政府機関の統一的な調達情報。
- **データ種別**: 
  - **公示情報 (Announcements)**: これから行われる入札。営業リストとして重要。
  - **落札情報 (Results)**: 過去の入札結果。競合分析、市場規模推定に重要。
- **連携キー**: `法人番号` (Corporate Number) が含まれている可能性が高い。

### B. 中小企業庁 官公需情報ポータルサイト
- **URL**: https://www.kkj.go.jp/
- **特徴**: 中小企業向けの案件情報が集約されている。
- **API**: あり (検索API)。

## 2. 目標スキーマ (`tenders`)

```sql
CREATE TABLE tenders (
    id VARCHAR(255) PRIMARY KEY, -- 案件番号など
    title TEXT NOT NULL,
    agency_name VARCHAR(255), -- 発注機関 (e.g. 北海道開発局)
    municipality_id VARCHAR(10), -- 関連自治体コード (推定)
    
    category VARCHAR(100), -- 業種 (e.g. 情報処理)
    
    -- 日付
    published_date DATE, -- 公示日
    closing_date DATE,   -- 締切日
    awarded_date DATE,   -- 落札日
    
    -- 落札情報 (Resultsのみ)
    winner_name VARCHAR(255),
    winner_corporate_number VARCHAR(13), -- CompanyテーブルとのFK
    contract_amount BIGINT, -- 契約金額
    
    -- メタデータ
    source_url TEXT,
    api_source VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 3. 実装ステップ

1.  **サンプル取得**: `scripts/fetch_tender_sample.py` を作成し、APIまたはWebから最新データを取得してみる。
2.  **スキーマ確定**: 実際のデータ項目を見てテーブル定義を作成。
3.  **インポーター作成**: 定期実行可能なスクリプト (`scripts/import_tenders.py`)。
4.  **紐付け**: `winner_corporate_number` を使って `companies` テーブルとJOINし、地図上に「受注企業」を表示可能にする。

## 4. 調査項目 (Action Items)

- [x] デジタル庁「調達情報詳細API」の仕様確認 (APIなし、CSVのみ)
- [x] 官公需APIのカバレッジ確認 (地方自治体の公告は取得可能、落札結果は不可)
- [x] `法人番号` の含有率確認 (官公需APIには含まれず)

## 5. 最終決定 (Status: Pivot)
- **落札結果 (Results)**: 自動取得は困難であり、正確性を欠くため**実装を見送る**。
- **リード検知 (Announcements)**: 「これから出る案件」を検知し、特定のプロダクト（PBX, Zoom等）に関連する場合にユーザーへ通知する機能として実装する。

