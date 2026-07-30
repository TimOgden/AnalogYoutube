CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                youtube_url TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL
            )

CREATE TABLE IF NOT EXISTS watchHistory (
    video_id TEXT PRIMARY KEY,
    device TEXT,
    watchDt DATETIME NOT NULL
)