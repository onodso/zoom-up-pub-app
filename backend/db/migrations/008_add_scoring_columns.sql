-- マイグレーション: Stage 1.5 スコアリング必須カラム追加
-- 日付: 2026-02-13
-- 目的: Decision Readiness Scorer v3.0 に必要なカラムを追加

-- 1. municipalities テーブルに統計カラム追加
ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS population_decline_rate FLOAT;
ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS elderly_ratio FLOAT;
ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS staff_reduction_rate FLOAT;
ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS dx_status JSONB;

COMMENT ON COLUMN municipalities.population_decline_rate IS '人口減少率（過去10年、0-1の値）';
COMMENT ON COLUMN municipalities.elderly_ratio IS '高齢化率（65歳以上、0-1の値）';
COMMENT ON COLUMN municipalities.staff_reduction_rate IS '職員削減率（過去5年、0-1の値）';
COMMENT ON COLUMN municipalities.dx_status IS 'DX組織体制情報（デジタル庁CSVからのJSONBデータ）';

-- 2. decision_readiness_scores テーブル作成（まだ存在しない場合）
CREATE TABLE IF NOT EXISTS decision_readiness_scores (
    id SERIAL PRIMARY KEY,
    city_code VARCHAR(6) NOT NULL,
    scored_at TIMESTAMP DEFAULT NOW(),

    -- 5 Pillars (Total 100)
    structural_pressure INTEGER CHECK (structural_pressure BETWEEN 0 AND 30),
    leadership_commitment INTEGER CHECK (leadership_commitment BETWEEN 0 AND 25),
    peer_pressure INTEGER CHECK (peer_pressure BETWEEN 0 AND 20),
    feasibility INTEGER CHECK (feasibility BETWEEN 0 AND 15),
    accountability INTEGER CHECK (accountability BETWEEN 0 AND 10),

    -- Generated Total
    total_score INTEGER GENERATED ALWAYS AS
        (structural_pressure + leadership_commitment + peer_pressure +
         feasibility + accountability) STORED,

    -- Metadata
    confidence_level VARCHAR(10) CHECK (confidence_level IN ('high', 'medium', 'low', 'unknown')),
    evidence_urls TEXT[], -- Array of source URLs
    signal_keywords TEXT[], -- Detected keywords

    UNIQUE(city_code, scored_at::DATE) -- One score per day per city
);

-- 3. municipalities への外部キー制約追加（参照整合性）
-- Note: city_code が municipalities.city_code を参照することを保証
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_decision_scores_city'
    ) THEN
        ALTER TABLE decision_readiness_scores
        ADD CONSTRAINT fk_decision_scores_city
        FOREIGN KEY (city_code) REFERENCES municipalities(code) ON DELETE CASCADE;
    END IF;
END$$;

-- 4. インデックス作成
CREATE INDEX IF NOT EXISTS idx_municipalities_decline ON municipalities(population_decline_rate DESC);
CREATE INDEX IF NOT EXISTS idx_municipalities_elderly ON municipalities(elderly_ratio DESC);
CREATE INDEX IF NOT EXISTS idx_scores_total ON decision_readiness_scores(total_score DESC);
CREATE INDEX IF NOT EXISTS idx_scores_city_date ON decision_readiness_scores(city_code, scored_at);

SELECT 'Migration 008 (Add Scoring Columns) completed successfully' AS status;
