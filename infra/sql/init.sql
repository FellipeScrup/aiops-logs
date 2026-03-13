CREATE TABLE IF NOT EXISTS silver_logs (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMPTZ,
    stacktrace TEXT,
    raw_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS diagnostics (
    id BIGSERIAL PRIMARY KEY,
    silver_log_id BIGINT REFERENCES silver_logs(id),
    model TEXT NOT NULL,
    response_time_ms INTEGER NOT NULL,
    diagnosis JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
