-- LocalGov DX Intelligence v3.0 Schema

-- 1. Municipalities Master
CREATE TABLE IF NOT EXISTS municipalities (
    city_code VARCHAR(6) PRIMARY KEY, -- 団体コード (e.g. 011002)
    prefecture VARCHAR(10) NOT NULL,
    city_name VARCHAR(50) NOT NULL,
    city_type VARCHAR(10), -- 市, 区, 町, 村
    
    -- Geospatial
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    
    -- Basic Stats (from e-Stat)
    population INTEGER,
    
    -- Web Info
    official_url TEXT,
    mayor_speech_url TEXT, -- Hand-picked or Scraped
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Decision Readiness Scores (The 100-Point Logic)
CREATE TABLE IF NOT EXISTS decision_readiness_scores (
    id SERIAL PRIMARY KEY,
    city_code VARCHAR(6) REFERENCES municipalities(city_code) ON DELETE CASCADE,
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
    signal_keywords TEXT[], -- Detected keywords (e.g. "補正予算", "人口減少")
    
    UNIQUE(city_code, scored_at::DATE) -- One score per day per city
);

-- 3. Evidence Items (Traceability)
CREATE TABLE IF NOT EXISTS evidence_items (
    id SERIAL PRIMARY KEY,
    city_code VARCHAR(6) REFERENCES municipalities(city_code) ON DELETE CASCADE,
    score_id INTEGER REFERENCES decision_readiness_scores(id) ON DELETE SET NULL,
    
    evidence_type VARCHAR(30), -- 'mayor_speech', 'estat_census', 'digital_agency_csv'
    source_url TEXT,
    extracted_text TEXT,
    
    collected_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for Speed
CREATE INDEX IF NOT EXISTS idx_municipalities_prefecture ON municipalities(prefecture);
CREATE INDEX IF NOT EXISTS idx_scores_total ON decision_readiness_scores(total_score DESC);
CREATE INDEX IF NOT EXISTS idx_scores_city_date ON decision_readiness_scores(city_code, scored_at);
