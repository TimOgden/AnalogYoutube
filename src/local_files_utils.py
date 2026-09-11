import io
import uuid
from PIL import Image
import cv2
import tempfile

from src.video_utils import Video, VideoSource
from src import thumbnail_utils
from src.consts import MEDIA_PATH
from fastapi import UploadFile
from pathlib import Path


def _title_from_filename(filename: Path | str) -> str:
    if isinstance(filename, str):
        filename = Path(filename)
    
    while filename.suffix:
        filename = filename.with_suffix('')
    return filename.name


def get_thumbnail(file: UploadFile) -> Image.Image:
    with tempfile.TemporaryDirectory() as temp_dir:
        local_path = Path(temp_dir) / file.filename
        with open(local_path, 'wb') as f:
            f.write(file.file.read())

        frame_capture = cv2.VideoCapture(local_path)

        ret, frame = frame_capture.read() 
        frame_capture.release()

    if not ret:
        raise ValueError("Error getting frame.")
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(frame_rgb, mode='RGB')


def _save_media(file: UploadFile, video_id: str) -> Path:
    path = MEDIA_PATH / 'videos' / f'{video_id}.mp4'
    with open(path, 'wb') as f:
        f.write(file.read())
    return path


def ingest_video(file: UploadFile) -> Video:
    video_id = str(uuid.uuid4())

    thumbnail = get_thumbnail(file)
    thumbnail_path = thumbnail_utils.save_thumbnail(thumbnail, video_id)
    _save_media(file)

    return Video(
        video_id=video_id,
        title=_title_from_filename(file.filename),
        source=VideoSource.LOCAL,
        thumbnail_path=thumbnail_path,
        video_url=None,
        author_name=None,
    )
