ALTER TABLE {{tables.subscriptions}}
    ADD COLUMN IF NOT EXISTS last_event_created_at TIMESTAMPTZ;
