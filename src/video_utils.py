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


def _process_submissions(conn: Connection, submissions: list, ingestion_func: Callable,
                         output_dir: Path) -> list[Path]:
    videos = []
    for submission in submissions:
        video = ingestion_func(submission)
        videos.append(video)

    _save_videos(conn, videos)
    return _to_html_files(videos, output_dir)


def process_submissions(con: Connection, submissions: list,
                        ingestion_func: Callable) -> io.BytesIO:
    zip_buffer = io.BytesIO()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = pathlib.Path(temp_dir)

        html_files = _process_submissions(con, submissions, ingestion_func, output_dir)
        
        with zipfile.ZipFile(
            zip_buffer,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as archive:
            for file_path in html_files:
                archive.write(file_path, arcname=file_path.name)

    zip_buffer.seek(0)
    return zip_buffer


def process_multi_submissions(conn: Connection, submissions: dict[str, list],
                              ingestion_funcs: dict[str, Callable]) -> io.BytesIO:
    zip_buffer = io.BytesIO()
        
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = pathlib.Path(temp_dir)

        html_files = []
        for source, ingestion_func in ingestion_funcs.items():
            source_submissions = submissions[source]
            html_files.append(_process_submissions(conn, source_submissions, ingestion_func, output_dir))
        
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


def row_to_video(row: dict) -> Video:
    video_path = Path(row['video_path']) if row['video_path'] else None
    thumbnail_path = Path(row['thumbnail_path']) if row['thumbnail_path'] else None
    thumbnail_url = f'/api/videos/{row['video_id']}/thumbnail'

    return Video(
        video_id=row['video_id'],
        title=row['title'],
        source=VideoSource(row['source']),
        thumbnail_path=thumbnail_path,
        thumbnail_url=thumbnail_url,
        video_url=row['video_url'],
        video_path=video_path,
        author_name=row['author_name'],
    )


def get_video(con: Connection, video_id: str) -> Video:
    cursor = con.cursor()
    cursor.execute("""SELECT * FROM videos where video_id=?""", (video_id,))
    result = cursor.fetchone()

    return row_to_video(result)
