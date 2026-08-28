CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                youtube_url TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL
            );

CREATE TABLE IF NOT EXISTS watchHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT,
    device TEXT,
    watchDt DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS playback_sessions (
    id          TEXT PRIMARY KEY,
    video_id    TEXT NOT NULL,

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