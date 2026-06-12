CREATE TABLE IF NOT EXISTS {{tables.subscriptions}} (
    team_id TEXT PRIMARY KEY REFERENCES {{tables.teams}}(team_id) ON DELETE CASCADE,
    tier TEXT NOT NULL DEFAULT 'free' CHECK (tier IN ('free', 'active', 'past_due')),
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    current_period_end TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_event_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_atext_subscriptions_tier
    ON {{tables.subscriptions}}(tier);
