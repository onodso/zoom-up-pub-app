-- 0. Rename 'code' to 'city_code' and 'name' to 'city_name' if exists (Standardization)
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'municipalities' AND column_name = 'code') THEN
        ALTER TABLE municipalities RENAME COLUMN code TO city_code;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'municipalities' AND column_name = 'name') THEN
        ALTER TABLE municipalities RENAME COLUMN name TO city_name;
    END IF;
END $$;

-- 1. Ensure new table exists (Idempotent)
CREATE TABLE IF NOT EXISTS decision_readiness_scores (
    id SERIAL PRIMARY KEY,
    city_code VARCHAR(6) REFERENCES municipalities(city_code) ON DELETE CASCADE,
    scored_at TIMESTAMP DEFAULT NOW(),
    
    structural_pressure INTEGER CHECK (structural_pressure BETWEEN 0 AND 30),
    leadership_commitment INTEGER CHECK (leadership_commitment BETWEEN 0 AND 25),
    peer_pressure INTEGER CHECK (peer_pressure BETWEEN 0 AND 20),
    feasibility INTEGER CHECK (feasibility BETWEEN 0 AND 15),
    accountability INTEGER CHECK (accountability BETWEEN 0 AND 10),
    
    confidence_level VARCHAR(10) CHECK (confidence_level IN ('high', 'medium', 'low', 'unknown')),
    evidence_urls TEXT[], 
    signal_keywords TEXT[]
);

-- Unique index for one score per city per day
CREATE UNIQUE INDEX IF NOT EXISTS idx_decision_readiness_scores_city_date 
    ON decision_readiness_scores (city_code, (scored_at::DATE));

-- 2. Add 'total_score' as GENERATED column if not exists
-- Only for Postgres 12+ 
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'decision_readiness_scores' AND column_name = 'total_score') THEN
        ALTER TABLE decision_readiness_scores 
        ADD COLUMN total_score INTEGER GENERATED ALWAYS AS 
            (structural_pressure + leadership_commitment + peer_pressure + feasibility + accountability) STORED;
    END IF;
END $$;

-- 3. Rename old 'scores' table to deprecated (if exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'scores') THEN
        ALTER TABLE scores RENAME TO scores_deprecated_v2;
    END IF;
END $$;

-- 4. Ensure 'municipalities' columns exist (Idempotent check)
ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS population_decline_rate FLOAT;
ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS elderly_ratio FLOAT;
ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS staff_reduction_rate FLOAT;
ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS fiscal_index FLOAT;
ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS dx_status JSONB;
ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS city_type VARCHAR(20);
ALTER TABLE municipalities ADD COLUMN IF NOT EXISTS mayor_speech_url TEXT;
