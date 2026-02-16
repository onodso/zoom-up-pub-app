-- マイグレーション: Stage 0 修正 - dx_progress に時系列対応
-- 日付: 2026-02-12
-- 目的: survey_year カラム追加（変化率計算に必須）

-- survey_year カラム追加
ALTER TABLE dx_progress ADD COLUMN IF NOT EXISTS survey_year INTEGER;

-- 既存データに 2024 を設定（現在のデータは2024年度のもの）
UPDATE dx_progress SET survey_year = 2024 WHERE survey_year IS NULL;

-- NOT NULL 制約追加
ALTER TABLE dx_progress ALTER COLUMN survey_year SET NOT NULL;

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_dx_progress_survey_year ON dx_progress(survey_year);

-- 複合インデックス（municipality_code + survey_year + category）
CREATE INDEX IF NOT EXISTS idx_dx_progress_composite ON dx_progress(municipality_code, survey_year, category);

-- コメント追加
COMMENT ON COLUMN dx_progress.survey_year IS '調査年度（例: 2024）';

SELECT 'Migration 007: dx_progress time-series support added successfully' AS status;
