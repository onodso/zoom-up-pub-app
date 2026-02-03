-- Zoom UP Public App - PostgreSQL Schema
-- TimescaleDB extension enabled

-- 自治体マスタ
CREATE TABLE municipalities (
    id SERIAL PRIMARY KEY,
    code VARCHAR(6) UNIQUE NOT NULL,
    prefecture VARCHAR(10) NOT NULL,
    name VARCHAR(50) NOT NULL,
    region VARCHAR(10) NOT NULL,  -- 北海道/東北/関東/中部/近畿/中国/四国/九州
    population INTEGER DEFAULT 0,
    households INTEGER DEFAULT 0,
    mayor_name VARCHAR(50),
    official_url TEXT,
    contact_phone VARCHAR(20),
    contact_email VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_municipalities_region ON municipalities(region);
CREATE INDEX idx_municipalities_prefecture ON municipalities(prefecture);

-- スコアテーブル
CREATE TABLE scores (
    id SERIAL PRIMARY KEY,
    municipality_id INTEGER REFERENCES municipalities(id) ON DELETE CASCADE,
    score_total DECIMAL(5,2) DEFAULT 0,
    score_data_quality DECIMAL(5,2) DEFAULT 0,
    score_dx_maturity DECIMAL(5,2) DEFAULT 0,
    score_online_procedures DECIMAL(5,2) DEFAULT 0,
    score_budget_match DECIMAL(5,2) DEFAULT 0,
    score_news_sentiment DECIMAL(5,2) DEFAULT 0,
    calculated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB,
    UNIQUE(municipality_id, calculated_at)
);

CREATE INDEX idx_scores_municipality ON scores(municipality_id);
CREATE INDEX idx_scores_total ON scores(score_total DESC);
CREATE INDEX idx_scores_date ON scores(calculated_at DESC);

-- ニュース・首長発言
CREATE TABLE news_statements (
    id SERIAL PRIMARY KEY,
    municipality_id INTEGER REFERENCES municipalities(id) ON DELETE CASCADE,
    category VARCHAR(20) NOT NULL,  -- news/statement/media
    title TEXT NOT NULL,
    content TEXT,
    source_url TEXT NOT NULL,
    published_at TIMESTAMP,
    sentiment_score DECIMAL(3,2),  -- -1.0 ~ 1.0
    keywords TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_news_municipality ON news_statements(municipality_id);
CREATE INDEX idx_news_published ON news_statements(published_at DESC);
CREATE INDEX idx_news_sentiment ON news_statements(sentiment_score DESC);

-- 予算・補正予算
CREATE TABLE budgets (
    id SERIAL PRIMARY KEY,
    municipality_id INTEGER REFERENCES municipalities(id) ON DELETE CASCADE,
    fiscal_year INTEGER NOT NULL,
    budget_type VARCHAR(20) NOT NULL,  -- regular/supplementary/carried_over
    category VARCHAR(50) NOT NULL,  -- 働き方改革/窓口DX/BCP/防災/庁内ICT/遠隔授業
    amount_yen BIGINT NOT NULL,
    department VARCHAR(100),
    source_url TEXT NOT NULL,
    extracted_text TEXT,
    confidence DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_budgets_municipality ON budgets(municipality_id);
CREATE INDEX idx_budgets_category ON budgets(category);
CREATE INDEX idx_budgets_year ON budgets(fiscal_year DESC);

-- 入札情報
CREATE TABLE tenders (
    id SERIAL PRIMARY KEY,
    municipality_id INTEGER REFERENCES municipalities(id) ON DELETE CASCADE,
    tender_date DATE NOT NULL,
    title TEXT NOT NULL,
    winner VARCHAR(200),
    amount_yen BIGINT,
    category VARCHAR(50),
    source_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tenders_municipality ON tenders(municipality_id);
CREATE INDEX idx_tenders_date ON tenders(tender_date DESC);

-- AI分析結果
CREATE TABLE ai_analyses (
    id SERIAL PRIMARY KEY,
    municipality_id INTEGER REFERENCES municipalities(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL,  -- sentiment/needs_prediction/budget_classification
    result JSONB NOT NULL,
    confidence DECIMAL(3,2),
    model_used VARCHAR(50),
    analyzed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ai_municipality ON ai_analyses(municipality_id);
CREATE INDEX idx_ai_type ON ai_analyses(analysis_type);

-- Sales Playbook
CREATE TABLE playbooks (
    id SERIAL PRIMARY KEY,
    municipality_id INTEGER REFERENCES municipalities(id) ON DELETE CASCADE,
    priority INTEGER NOT NULL,  -- 1-5（ZP優先、ZP+ZRA等）
    product_combination TEXT[] NOT NULL,  -- ['ZP', 'AI Companion', 'ZRA']
    reasoning TEXT NOT NULL,
    target_department VARCHAR(100),
    next_actions TEXT[] NOT NULL,
    objection_handling JSONB,
    generated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_playbooks_municipality ON playbooks(municipality_id);
CREATE INDEX idx_playbooks_priority ON playbooks(priority);

-- バッチ実行ログ
CREATE TABLE batch_logs (
    id SERIAL PRIMARY KEY,
    batch_type VARCHAR(50) NOT NULL,  -- nightly_crawl/data_sync/ai_analysis
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    municipalities_processed INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL,  -- running/completed/failed
    error_log TEXT
);

CREATE INDEX idx_batch_started ON batch_logs(started_at DESC);

-- ユーザー（Zoom AE）
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- admin/ae
    assigned_regions TEXT[],  -- ['関東', '中部']
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- アクセスログ
CREATE TABLE access_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    ip_address INET,
    user_agent TEXT,
    accessed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_access_user ON access_logs(user_id);
CREATE INDEX idx_access_time ON access_logs(accessed_at DESC);

-- エラーログ
CREATE TABLE error_logs (
    id SERIAL PRIMARY KEY,
    error_type VARCHAR(50) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    endpoint VARCHAR(200),
    is_resolved BOOLEAN DEFAULT FALSE,
    occurred_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_error_type ON error_logs(error_type);
CREATE INDEX idx_error_resolved ON error_logs(is_resolved, occurred_at DESC);
