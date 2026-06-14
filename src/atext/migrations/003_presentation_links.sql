CREATE TABLE IF NOT EXISTS {{tables.presentation_links}} (
    token TEXT PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES {{tables.documents}}(document_id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by_did_key TEXT NOT NULL,
    created_by_did_aw TEXT,
    created_by_alias TEXT NOT NULL,
    certificate_id TEXT NOT NULL,
    FOREIGN KEY (document_id, version_number) REFERENCES {{tables.document_versions}}(document_id, version_number) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_atext_presentation_links_document
    ON {{tables.presentation_links}}(document_id, version_number);
CREATE INDEX IF NOT EXISTS idx_atext_presentation_links_expires
    ON {{tables.presentation_links}}(expires_at);
