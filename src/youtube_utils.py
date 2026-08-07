import io
import sqlite3
import requests
from dataclasses import dataclass
from pytubefix import YouTube
from PIL import Image
import logging



logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

YOUTUBE_OEMBED_URL = "https://www.youtube.com/oembed"

@dataclass(frozen=True)
class YoutubeVideo:
    title: str
    url: str
    thumbnail: Image
    video_id: str


def get_youtube_video(url: str) -> YoutubeVideo:
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
    return YoutubeVideo(
        url=url,
        title=data["title"],
        thumbnail=thumbnail,
        video_id=yt.video_id
    )


def submit_videos_to_db(cur: sqlite3.Cursor, videos: list[YoutubeVideo]) -> None:
    logger.debug(f'Saving videos to db: {videos}')
    sql = """INSERT INTO videos (video_id, youtube_url, title) VALUES (?, ?, ?);"""

    param_list = []
    for video in videos:
        param_list.append((video.video_id, video.url, video.title))
    cur.executemany(sql, param_list)
