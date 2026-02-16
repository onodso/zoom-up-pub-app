# GIGAスクール構想データ収集 実装計画

## Goal Description
文部科学省「学校における教育の情報化の実態等に関する調査（令和5年度）」のデータを収集し、各自治体のGIGAスクール端末のOS種類（Chromebook, iPad, Windows等）やネットワーク整備状況をデータベース化する。

## User Review Required
> [!IMPORTANT]
> `education_info` テーブルを新規作成します。
> データソース: e-Stat [令和5年度 学校における教育の情報化の実態等に関する調査](https://www.e-stat.go.jp/stat-search/files?statInfId=000040221910&fileKind=0)

## Proposed Changes

### Database Schema
#### [NEW] Table: `education_info`
```sql
CREATE TABLE education_info (
    city_code VARCHAR(6) PRIMARY KEY REFERENCES municipalities(city_code),
    terminal_os_type VARCHAR(100), -- 'Chromebook', 'iOS', 'Windows', 'Mixed' など
    student_per_computer NUMERIC(4,2), -- コンピュータ1台当たりの児童生徒数
    network_speed VARCHAR(100), -- インターネット接続速度（最大値など）
    survey_year INTEGER, -- 調査年度 (2023)
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Backend Services
- **Purpose**: GIGAスクール構想データの収集（e-Stat）
- **Method**:
  - Browser Subagentで取得した47都道府県のExcelファイルURLリストを使用
  - `download_and_import_all` メソッドで順次ダウンロード・解析
  - テーブル (`education_info`) へ `ON CONFLICT` で保存
- **Data Source**: e-Stat "学校における教育の情報化の実態等に関する調査" (令和5年度)
- **Data Mapping**:
  - `municipality_name` (DB照合)
  - `terminal_os_type`: **取得不可のため 'Unknown' を設定** (元データにOS内訳なし)
  - `student_per_computer`: 「児童生徒数」と「学習者用PC総台数」から算出
  - `network_speed`: 「インターネット接続率」から推測またはNULL
- **Changes**:
  - ヘッダー検出ロジックを「OS種類」から「学習者用PC総台数」ベースに変更
  - OS判定ロジックは削除

## Verification Plan

### Automated Tests
- データインポート後、主要都市のOSタイプが正しいか確認
    - 例: `SELECT * FROM education_info WHERE city_code = '011002';` (札幌市)

### Manual Verification
- ダウンロードしたExcelファイルとDBの値を数件ランダムに照合
