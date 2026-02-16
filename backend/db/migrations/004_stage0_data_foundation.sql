-- マイグレーション: 段階0 データ基盤再構築
-- 日付: 2026-02-12
-- 目的: Municipality テーブルに地理/財政カラム追加 + DX進捗テーブル作成

-- 1. municipalities テーブルに新カラム追加
ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS latitude FLOAT;
ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS longitude FLOAT;
ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS fiscal_index FLOAT;

COMMENT ON COLUMN municipalities.latitude IS '緯度';
COMMENT ON COLUMN municipalities.longitude IS '経度';
COMMENT ON COLUMN municipalities.fiscal_index IS '財政力指数';

-- 2. DX進捗テーブル作成
CREATE TABLE IF NOT EXISTS dx_progress (
    id SERIAL PRIMARY KEY,
    municipality_code VARCHAR(6) NOT NULL,
    municipality_name VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    value FLOAT,
    value_text VARCHAR(100),
    source VARCHAR(100) DEFAULT 'gov_dx_dashboard',
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dx_progress_code ON dx_progress(municipality_code);
CREATE INDEX IF NOT EXISTS idx_dx_progress_category ON dx_progress(category);
CREATE INDEX IF NOT EXISTS idx_dx_progress_code_category ON dx_progress(municipality_code, category);

COMMENT ON TABLE dx_progress IS '自治体DX進捗データ（政府DXダッシュボードからの実データ）';

SELECT 'Migration Stage 0 completed successfully' AS status;
