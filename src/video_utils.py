from dataclasses import dataclass, field
from enum import Enum
import io
from pathlib import Path
import pathlib
from typing import Callable
from sqlite3 import Connection
import tempfile
import zipfile
from src.qr_listener.qr_generator_utils import populate_qr_code_template
from src.video_models import Video, VideoSource


def process_submissions(con: Connection, submissions: list,
                        ingestion_func: Callable) -> io.BytesIO:
    zip_buffer = io.BytesIO()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = pathlib.Path(temp_dir)

        videos = []
        for submission in submissions:
            video = ingestion_func(submission)
            videos.append(video)

        html_files = _save_videos(con, videos)
        html_files = _to_html_files(videos, output_dir)
        
        with zipfile.ZipFile(
            zip_buffer,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as archive:
            for file_path in html_files:
                archive.write(file_path, arcname=file_path.name)

    zip_buffer.seek(0)
    return zip_buffer


def _save_videos(con: Connection, videos: list[Video]) -> None:
    sql = """INSERT INTO videos (
        video_id,
        title,
        source,
        thumbnail_path,
        video_url,
        video_path,
        author_name
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(video_id) DO UPDATE SET
        title = excluded.title,
        source = excluded.source,
        thumbnail_path = excluded.thumbnail_path,
        video_url = excluded.video_url,
        video_path = excluded.video_path,
        author_name = excluded.author_name;
    """

    param_list = []
    for video in videos:
        video_path = str(video.video_path) if video.video_path is not None else None
        param_list.append((video.video_id, video.title, video.source.value,
                           str(video.thumbnail_path), video.video_url, video_path, video.author_name))
    con.executemany(sql, param_list)


def _to_html_files(videos: list[Video], output_dir: Path) -> list[Path]:
    filepaths = []
    for video in videos:
        path = populate_qr_code_template(video, 
                                         output_dir / f'{video.title.replace('/', '_')}.html')
        filepaths.append(path)
    return filepaths


def get_video(con: Connection, video_id: str) -> Video:
    cursor = con.cursor()
    cursor.execute("""SELECT * FROM videos where video_id=?""", (video_id,))
    result = cursor.fetchone()

    return Video(
        video_id=result['video_id'],
        title=result['title'],
        source=VideoSource(result['source']),
        thumbnail_path=Path(result['thumbnail_path']),
        video_url=result['video_url'],
        video_path=Path(result['video_path']) if result['video_path'] else None,
        author_name=result['author_name'],
    )
