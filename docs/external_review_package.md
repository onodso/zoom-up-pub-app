# 外部レビュー用資料: 自治体データ収集基盤 実装報告書

## 1. 概要
本プロジェクトでは、自治体DX推進に資するデータ収集基盤の構築を行いました。主要な成果として、以下の3つのデータパイプラインを実装・稼働させています。

1. **デジタル庁/総務省 DX調査データ収集**: 自治体のDX推進状況（マイナンバーカード普及率、手続きオンライン化等）を自動収集。
2. **自治体ニュース収集 (Top 500)**: Google Custom Search APIを利用し、主要500自治体の最新ニュースを日次で収集。
3. **GIGAスクール構想データ収集**: 文部科学省e-Statより、全国の公立学校における端末整備状況データを収集。

## 2. 実装詳細

### 2.1 DX調査データ収集
- **目的**: 自治ごとのDX推進レベルを定量化するための基礎データ収集。
- **データソース**: デジタル庁「自治体DX推進状況」ダッシュボード公開データ。
- **実装コード**: [download_dx_survey.py](file:///Users/sonodera/zoom-up-pub-app/backend/services/download_dx_survey.py)
- **処理概要**:
    - 公開ZIPファイルをメモリ上で展開・パース。
    - 自治体名をキーにマッピングし、`municipalities` テーブルの `dx_status` カラム（JSONB）に格納。
- **検証結果**:
    - 取得対象: 全1,741市区町村 + 都道府県
    - データ保持率: 92.1% (2,216自治体でデータあり)
    - 項目例: 「全体方針策定状況」「マイナンバーカード保有枚数率」など

### 2.2 自治体ニュース収集
- **目的**: 自治体の最新動向やホットトピックを把握する。
- **データソース**: Google Custom Search API (Web検索)。
- **実装コード**: [collect_news_top500.py](file:///Users/sonodera/zoom-up-pub-app/backend/services/collect_news_top500.py)
- **処理概要**:
    - 人口上位500自治体をターゲットリスト化。
    - 日次でローテーション（30〜50自治体/日）し、API制限内で効率的に検索。
    - 検索クエリ: `{自治体名} DX | AI | 働き方改革 -求人`
- **検証結果**:
    - 初回実行で30自治体のデータを収集完了。
    - 記事タイトル、リンク、スニペット、画像URLをDBに保存。

### 2.3 GIGAスクール構想データ収集
- **目的**: 教育現場のICT環境整備状況の把握。
- **データソース**: e-Stat「学校における教育の情報化の実態等に関する調査（令和5年度）」。
- **実装コード**: [download_giga_data.py](file:///Users/sonodera/zoom-up-pub-app/backend/services/download_giga_data.py)
- **処理概要**:
    - 47都道府県ごとのExcelファイルを自動ダウンロード。
    - 表記揺れやフォーマット差異を吸収し、市区町村コードとマッピング。
    - 「学習者用端末の整備台数」「児童生徒数」から「1人あたりの端末台数」を算出。
    - **Note**: OS内訳（Windows/Chrome/iPad）は元データに含まれていないため、取得対象外としました。
- **検証結果**:
    - インポート件数: **1,738** 自治体
    - 平均端末整備率: 1.16台/人 (PC総台数 / 児童生徒数)
      - ※ 1.0以上で「1人1台」達成

## 3. データベース構造
新たに追加・更新された主なテーブル定義は以下の通りです。

```sql
-- 自治体マスター (DXデータ追加)
ALTER TABLE municipalities ADD COLUMN dx_status JSONB;

-- GIGAスクールデータ (新規)
CREATE TABLE education_info (
    city_code VARCHAR(6) PRIMARY KEY REFERENCES municipalities(city_code),
    terminal_os_type VARCHAR(100), -- 今回は 'Unknown'
    computer_per_student NUMERIC(4,2), -- 修正: PC台数 / 生徒数
    network_speed VARCHAR(100),
    survey_year INTEGER,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 4. 今後の課題・展望
- **可視化**: 収集したデータを地図上やグラフで可視化するダッシュボードの実装。
- **データ活用**: ニュースデータと基本指標（人口・財政）を組み合わせた、自治体ごとの「DX推奨度スコア」の算出。
- **自動化**: AirflowやCronによる完全自動定期実行のスケジュール設定。

## 5. 関連ドキュメント
- [Task Checklist](task.md)
- [Walkthrough / Result Report](walkthrough.md)
- [Implementation Plan](implementation_plan.md)
- [Data Validation List](data_validation_list.md)
