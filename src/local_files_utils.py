import io
import uuid
from PIL import Image
import cv2

from src.video_utils import Video, VideoSource
from src import thumbnail_utils
from fastapi import UploadFile
from pathlib import Path


def _title_from_filename(filename: Path) -> str:
    while filename.suffix:
        filename = filename.with_suffix('')
    return filename.name


def get_thumbnail(bytes_content: bytes) -> Image.Image:
    video_stream = io.BytesIO(bytes_content)
    frame_capture = cv2.VideoCapture(video_stream)

    if not frame_capture.isOpened():
        raise ValueError("Error opening video stream.")

    ret, frame = frame_capture.read() 
    frame_capture.release()

    if not ret:
        raise ValueError("Error getting frame.")
    return Image.fromarray(frame, mode='RGB')


def ingest_video(file: UploadFile) -> Video:
    video_id = uuid.uuid4()

    thumbnail = get_thumbnail(file.file.read())
    thumbnail_path = thumbnail_utils.save_thumbnail(thumbnail, video_id)

    return Video(
        video_id=video_id,
        title=_title_from_filename(file.filename),
        source=VideoSource.LOCAL,
        thumbnail_path=thumbnail_path,
        video_url=None,
        author_name=None,
    )
