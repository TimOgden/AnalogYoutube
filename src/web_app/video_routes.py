from pathlib import Path

from fastapi import APIRouter

from src import db_utils, video_utils
from src.video_models import Video, VideoSource

router = APIRouter()


@router.get('/api/videos')
def get_videos() -> list[Video]:
    with db_utils.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT * FROM videos;""")
        rows = cur.fetchall()


    videos = []
    for row in rows:
        videos.append(video_utils.row_to_video(row))
    return videos
