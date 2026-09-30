from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException
from fastapi import APIRouter

from src import db_utils, video_utils
from src.video_models import Video
from src.consts import MEDIA_PATH

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



@router.delete('/api/videos')
def delete_video(video_ids: list[str]) -> list[Video]:
    video_utils.delete_videos(video_ids)
    return get_videos()


@router.get("/api/videos/{video_id}/thumbnail")
def get_video_thumbnail(video_id: str) -> FileResponse:
    thumbnail_path = MEDIA_PATH / "thumbnails" / f"{video_id}.png"

    if not thumbnail_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Thumbnail not found for video {video_id}",
        )

    return FileResponse(thumbnail_path)
