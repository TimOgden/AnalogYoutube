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