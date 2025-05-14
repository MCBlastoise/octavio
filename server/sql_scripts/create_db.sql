CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    instrument_id TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    last_updated TEXT DEFAULT (datetime('now')),
    song_mode TEXT,
    song_key TEXT,
    UNIQUE(session_id, instrument_id)
);
