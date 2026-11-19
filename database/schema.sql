CREATE TABLE IF NOT EXISTS detections (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    image_id TEXT NOT NULL,
    category TEXT NOT NULL,
    candidate TEXT NOT NULL,
    confidence REAL NOT NULL,
    status TEXT NOT NULL,
    source TEXT NOT NULL,
    elapsed_ms REAL NOT NULL,
    model TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    threshold REAL NOT NULL,
    margin_threshold REAL NOT NULL,
    scores_json TEXT NOT NULL,
    is_test INTEGER NOT NULL DEFAULT 0
);
