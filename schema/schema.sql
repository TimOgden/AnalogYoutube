CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                youtube_url TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                thumbnail_path TEXT,
                video_path TEXT,
                download_status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )