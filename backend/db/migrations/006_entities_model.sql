-- マイグレーション: Stage 0 修正 - Entities モデル新設
-- 日付: 2026-02-12
-- 目的: 1,835ノード統一管理（市区町村 + 都道府県 + 教育委員会）

-- entities テーブル作成
CREATE TABLE IF NOT EXISTS entities (
    entity_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    entity_type VARCHAR(20) NOT NULL,
    prefecture_code VARCHAR(2),
    latitude FLOAT,
    longitude FLOAT,
    population INTEGER,
    fiscal_index FLOAT,
    official_url TEXT,
    activity_index FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
    metadata_json TEXT
);

-- インデックス作成
CREATE INDEX idx_entities_type ON entities(entity_type);
CREATE INDEX idx_entities_prefecture ON entities(prefecture_code);
CREATE INDEX idx_entities_activity ON entities(activity_index);

-- コメント追加
COMMENT ON TABLE entities IS '統一エンティティモデル（市区町村・都道府県・教育委員会）';
COMMENT ON COLUMN entities.entity_id IS '主キー: M{code}/P{code}/E{code}';
COMMENT ON COLUMN entities.entity_type IS 'municipality / prefecture / education_board';
COMMENT ON COLUMN entities.activity_index IS 'DX Activity Index (0-100)';

SELECT 'Migration 006: Entities model created successfully' AS status;
