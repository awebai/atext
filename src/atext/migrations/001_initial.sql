CREATE TABLE IF NOT EXISTS {{tables.teams}} (
    team_id TEXT PRIMARY KEY,
    team_did_key TEXT NOT NULL,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {{tables.agents}} (
    team_id TEXT NOT NULL REFERENCES {{tables.teams}}(team_id) ON DELETE CASCADE,
    did_key TEXT NOT NULL,
    did_aw TEXT,
    address TEXT,
    alias TEXT NOT NULL,
    latest_certificate_id TEXT NOT NULL,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (team_id, did_key, alias)
);

CREATE INDEX IF NOT EXISTS idx_atext_agents_team_alias
    ON {{tables.agents}}(team_id, alias);

CREATE TABLE IF NOT EXISTS {{tables.documents}} (
    document_id UUID PRIMARY KEY,
    team_id TEXT NOT NULL REFERENCES {{tables.teams}}(team_id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    created_by_did_key TEXT NOT NULL,
    created_by_did_aw TEXT,
    created_by_alias TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (team_id, slug)
);

CREATE INDEX IF NOT EXISTS idx_atext_documents_team_updated
    ON {{tables.documents}}(team_id, updated_at DESC);

CREATE TABLE IF NOT EXISTS {{tables.document_versions}} (
    version_id UUID PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES {{tables.documents}}(document_id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    body TEXT NOT NULL,
    created_by_did_key TEXT NOT NULL,
    created_by_did_aw TEXT,
    created_by_address TEXT,
    created_by_alias TEXT NOT NULL,
    certificate_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (document_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_atext_versions_document_number
    ON {{tables.document_versions}}(document_id, version_number DESC);
