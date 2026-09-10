from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from sqlite3 import Connection
from src.qr_listener.qr_generator_utils import populate_qr_code_template


class VideoSource(str, Enum):
    LOCAL = 'local'
    YOUTUBE = 'youtube'
    LIBRARY = 'library'


@dataclass(frozen=True)
class Video:
    video_id: str
    title: str
    source: VideoSource
    thumbnail_path: Path
    video_url: str | None = field(default=None)
    author_name: str | None = field(default=None)


def save_videos(con: Connection, videos: list[Video]) -> None:
    sql = """INSERT INTO videos (
        video_id,
        title,
        source,
        thumbnail_path,
        video_url,
        author_name,
    ) VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(video_id) DO UPDATE SET
        title = excluded.title,
        source = excluded.source,
        thumbnail_path = excluded.thumbnail_path,
        video_url = excluded.video_url,
        author_name = excluded.author_name;
    """

    param_list = []
    for video in videos:
        param_list.append((video.video_id, video.title, video.source.value,
                           video.thumbnail_path, video.video_url, video.author_name))
    con.executemany(sql, param_list)


def to_html_files(videos: list[Video], output_dir: Path) -> list[Path]:
    filepaths = []
    for video in videos:
        path = populate_qr_code_template(video, 
                                         output_dir / f'{video.title}.html')
        filepaths.append(path)
    return filepaths
