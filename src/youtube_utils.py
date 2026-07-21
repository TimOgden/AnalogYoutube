import sqlite3
import enum
import io
import pathlib
import requests
from dataclasses import dataclass
from pytubefix import YouTube
from PIL import Image
import datetime
import secrets
import logging

from src import database, download_utils


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
    yt: YouTube


class DownloadStatus(enum.Enum):
    PENDING = 'pending'
    DOWNLOADING = 'downloading'
    READY = 'ready'
    FAILED = 'failed'


@dataclass
class YoutubeCard:
    video_id: str
    youtube_url: str
    title: str
    thumbnail_path: pathlib.Path | None
    video_path: pathlib.Path | None
    download_status: DownloadStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime


    @staticmethod
    def from_row(row: sqlite3.Row):
         return YoutubeCard(
            video_id=row["video_id"],
            youtube_url=row["youtube_url"],
            title=row["title"],
            thumbnail_path=(
                pathlib.Path(row["thumbnail_path"])
                if row["thumbnail_path"] is not None
                else None
            ),
            video_path=(
                pathlib.Path(row["video_path"])
                if row["video_path"] is not None
                else None
            ),
            download_status=DownloadStatus(row["download_status"]),
            created_at=datetime.datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.datetime.fromisoformat(row["updated_at"]),
        )


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
        yt=yt
    )


def _validate_youtube_card_download_status(card: YoutubeCard) -> None:
    if not card.thumbnail_path.exists() or not card.video_path.exists():
        card.download_status = DownloadStatus.PENDING

def get_youtube_card_by_id(video_id: str, conn: sqlite3.Connection) -> YoutubeCard | None:
    row = conn.execute("""SELECT * from videos where video_id=?""", (video_id,)).fetchone()
    if row is None:
        return None
    
    card = YoutubeCard.from_row(row)
    _validate_youtube_card_download_status(card)
    return card


def update_download_status(conn: sqlite3.Connection, video_id: str, download_status: DownloadStatus) -> None:
    conn.execute("""UPDATE videos SET download_status=? WHERE video_id = ?""", (download_status.value, video_id))


def create_or_update_youtube_card(conn: sqlite3.Connection,
                                  youtube_video: YoutubeVideo,
                                  video_path: pathlib.Path | None = None,
                                  thumbnail_path: pathlib.Path | None = None,
                                  download_status: DownloadStatus | None = None) -> YoutubeCard:
    current_dt = datetime.datetime.now()

    if download_status is None:
        download_status = DownloadStatus.PENDING
    
    conn.execute(
        """
        INSERT INTO videos (
            video_id,
            youtube_url,
            title,
            video_path,
            thumbnail_path,
            download_status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(video_id) DO UPDATE SET
            youtube_url = excluded.youtube_url,
            title = excluded.title,
            video_path = excluded.video_path,
            thumbnail_path = excluded.thumbnail_path,
            download_status = excluded.download_status,
            updated_at = excluded.updated_at
        """,
        (
            youtube_video.yt.video_id,
            youtube_video.url,
            youtube_video.title,
            str(video_path),
            str(thumbnail_path),
            download_status.value,
            current_dt.isoformat(),
            current_dt.isoformat(),
        ),
    )
    
    return get_youtube_card_by_id(youtube_video.yt.video_id, conn)


def download_youtube_video(video: YoutubeVideo) -> None:
    video_id = video.yt.video_id
    if video is None:
        raise ValueError(f'Unknown video: {video_id}')
    
    video_filepath = pathlib.Path('media') / 'videos' / f'youtube_{video_id}.mp4'
    video_filepath.parent.mkdir(parents=True, exist_ok=True)
    thumbnail_filepath = pathlib.Path('media') / 'thumbnails' / f'youtube_{video_id}.png'
    thumbnail_filepath.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f'Downloading youtube video "{video.title}"...')
    try:
        download_utils.download_youtube_video(video.url, video_filepath)
        logger.info(f'Successfully downloaded youtube video "{video.title}" to `{video_filepath}`.')
    except Exception as e:
        logger.error(e)
        logger.error(f'Failed to download from youtube: {video}')
    
    video.thumbnail.save(thumbnail_filepath)
    logger.info(f'Successfully saved thumbnail image for youtube video "{video.title}" to `{thumbnail_filepath}`.')


def download_video_worker(video: YoutubeVideo) -> None:
    try:
        with database.get_connection() as conn:
            video_id = video.yt.video_id
            video_card = get_youtube_card_by_id(
                video_id=video_id,
                conn=conn,
            )

            if video_card is None:
                return

            if video_card.download_status == DownloadStatus.READY:
                return
            
            update_download_status(
                conn=conn,
                video_id=video_id,
                download_status=DownloadStatus.DOWNLOADING,
            )
            download_youtube_video(video)
            update_download_status(
                conn=conn,
                video_id=video_id,
                download_status=DownloadStatus.READY
            )
    except Exception as e:
        logger.error(e)
        
        logger.error(f'Download failed for video {video_id}')
        with database.get_connection() as conn:
            update_download_status(
                conn=conn,
                video_id=video_id,
                download_status=DownloadStatus.FAILED,
            )
        raise e
