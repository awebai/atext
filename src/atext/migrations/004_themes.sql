CREATE TABLE IF NOT EXISTS {{tables.assets}} (
    asset_id UUID PRIMARY KEY,
    team_id TEXT NOT NULL REFERENCES {{tables.teams}}(team_id) ON DELETE CASCADE,
    bytes BYTEA NOT NULL,
    content_type TEXT NOT NULL CHECK (content_type IN ('image/png', 'image/jpeg', 'image/gif', 'image/webp')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_atext_assets_team_created
    ON {{tables.assets}}(team_id, created_at DESC);

CREATE TABLE IF NOT EXISTS {{tables.themes}} (
    team_id TEXT PRIMARY KEY REFERENCES {{tables.teams}}(team_id) ON DELETE CASCADE,
    tokens JSONB NOT NULL DEFAULT '{}'::jsonb,
    logo_asset_id UUID REFERENCES {{tables.assets}}(asset_id) ON DELETE SET NULL,
    header TEXT,
    footer TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
