from PIL.Image import Image
import os
import pathlib


MEDIA_PATH = pathlib.Path(os.environ['media_path'])


def save_thumbnail(thumbnail: Image, video_id: str) -> pathlib.Path:
    (MEDIA_PATH / 'thumbnails').mkdir(parents=True, exist_ok=True)
    file_path = MEDIA_PATH / 'thumbnails' / f'{video_id}.jpeg'
    thumbnail.save(file_path, format='JPEG')
    return file_path


def generate_thumbnail_from_video(video: bytearray) -> Image:
    ...
