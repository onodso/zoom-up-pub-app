-- マイグレーション: 段階1 スコアテーブル改修
-- 日付: 2026-02-12
-- 目的: 4カテゴリ構成に合わせてスコアカラムをリネーム・変更

-- 1. カラムのリネームと意味の変更
-- Budget Match -> Organization (組織・体制)
ALTER TABLE scores RENAME COLUMN score_budget_match TO score_organization;
COMMENT ON COLUMN scores.score_organization IS '組織・体制スコア (25点満点)';

-- Online Procedures -> Citizen Services (住民サービス)
ALTER TABLE scores RENAME COLUMN score_online_procedures TO score_citizen_services;
COMMENT ON COLUMN scores.score_citizen_services IS '住民サービススコア (25点満点)';

-- Data Quality -> Data Completeness (データ充実度)
ALTER TABLE scores RENAME COLUMN score_data_quality TO score_data_completeness;
COMMENT ON COLUMN scores.score_data_completeness IS 'データ充実度スコア (10点満点)';

-- News Sentiment -> Signals (シグナル活性)
ALTER TABLE scores RENAME COLUMN score_news_sentiment TO score_signals;
COMMENT ON COLUMN scores.score_signals IS 'シグナル活性スコア (40点満点)';

-- DX Maturity -> 廃止 (Signalsに統合)
ALTER TABLE scores DROP COLUMN IF EXISTS score_dx_maturity;

-- 2. municipalities テーブルのキャッシュカラムも同様に変更
-- score_total はそのまま
-- 個別スコアキャッシュがあれば変更（現状は score_total のみ管理されているようだが念のため確認）

-- 3. 検証用ビュー作成（オプション）
-- CREATE OR REPLACE VIEW v_municipality_scores AS ...

SELECT 'Migration Stage 1 (Score Table) completed successfully' AS status;
