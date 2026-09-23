CREATE TABLE IF NOT EXISTS videos (
    video_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    thumbnail_path TEXT NOT NULL,
    video_url TEXT,
    video_path TEXT,
    author_name TEXT
);

CREATE TABLE IF NOT EXISTS playback_sessions (
    id          TEXT PRIMARY KEY,
    video_id    TEXT NOT NULL,
    source      TEXT NOT NULL,

    created_at  DATETIME NOT NULL,
    started_at  DATETIME,
    ended_at    DATETIME
);

CREATE TABLE IF NOT EXISTS playback_usage (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL,
    recorded_at     DATETIME NOT NULL,
    watched_seconds REAL NOT NULL,

    FOREIGN KEY (session_id)
        REFERENCES playback_sessions(id)
);