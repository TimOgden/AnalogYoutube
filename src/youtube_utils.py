import io
import sqlite3
import requests
from dataclasses import dataclass
from pytubefix import YouTube
from src import thumbnail_utils
from PIL.Image import Image
from src.qr_listener.qr_generator_models import CardData
import pathlib
import logging

from src.video_models import Video, VideoSource



logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

YOUTUBE_OEMBED_URL = "https://www.youtube.com/oembed"


def submit_videos_to_db(
    cur: sqlite3.Cursor,
    videos: list[Video],
) -> None:
    logger.info("Saving videos to db: %s", videos)
    sql = """
        INSERT INTO videos (
            video_id,
            title,
            source,
            thumbnail_path,
        )
        VALUES (?, ?, ?)
        ON CONFLICT(video_id) DO UPDATE SET
            title = excluded.title;

        INSERT INTO youtubeVideos (
            video_id,
            youtube_url,
            author_name
        )
        VALUES (?, ?, ?)
        ON CONFLICT(video_id) DO UPDATE SET
            youtube_url = excluded.youtube_url,
            author_name = excluded.author_name;
    """

    params = [
        (video.video_id, video.title, 'youtube', video.video_id, video.url, video.author_name)
        for video in videos
    ]

    cur.executemany(sql, params)


def get_metadata(url: str) -> dict:
    response = requests.get(
        YOUTUBE_OEMBED_URL,
        params={
            "url": url,
            "format": "json",
        },
        timeout=15,
    )
    response.raise_for_status()

    data = response.json()

    thumbnail_response = requests.get(data["thumbnail_url"], timeout=15)
    thumbnail_response.raise_for_status()

    thumbnail = Image.open(io.BytesIO(thumbnail_response.content))
    yt = YouTube(url, 'WEB')
    return {
        'video_id': yt.video_id,
        'title': yt.title,
        'author_name': yt.author,
        'thumbnail': thumbnail
    }


def ingest_video(url: str) -> Video:
    metadata = get_metadata(url)
    thumbnail_path = thumbnail_utils.save_thumbnail(metadata['thumbnail'], 
                                                    metadata['video_id'])
    return Video(
        video_id=metadata['video_id'],
        title=metadata['title'],
        source=VideoSource.YOUTUBE,
        thumbnail_path=thumbnail_path,
        video_url=url,
        author_name=metadata['author_name'],
    )
