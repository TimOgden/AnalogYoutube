import io
import hashlib
import logging
import shutil
import subprocess
from PIL import Image
import cv2
import tempfile

from src.video_utils import Video, VideoSource
from src import thumbnail_utils
from src.consts import MEDIA_PATH
from fastapi import UploadFile
from pathlib import Path


logger = logging.getLogger(__name__)


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


def _convert_to_mp4(file: UploadFile, output_path: Path) -> None:
    suffix = Path(file.filename or "").suffix or ".bin"

    with tempfile.NamedTemporaryFile(
        suffix=suffix,
        delete=False,
    ) as input_file:
        input_path = Path(input_file.name)

        file.file.seek(0)
        shutil.copyfileobj(file.file, input_file)

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(input_path),

                # Video
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "22",

                # Audio
                "-c:a",
                "aac",
                "-b:a",
                "128k",

                # Better for browser streaming
                "-movflags",
                "+faststart",

                str(output_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"ffmpeg conversion failed:\n{exc.stderr}"
        ) from exc

    finally:
        input_path.unlink(missing_ok=True)


def _save_media(file: UploadFile, video_id: str) -> Path:
    path = MEDIA_PATH / "videos" / f"{video_id}.mp4"
    path.parent.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "").suffix.lower()

    if suffix == ".mp4":
        file.file.seek(0)

        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)

    else:
        _convert_to_mp4(
            file=file,
            output_path=path,
        )

    return path


def _get_file_hash(file: UploadFile) -> str:
    digest = hashlib.sha256()
    file.file.seek(0)

    for chunk in iter(lambda: file.file.read(1024 * 1024), b''):
        digest.update(chunk)

    file.file.seek(0)
    return digest.hexdigest()


def ingest_video(file: UploadFile) -> Video:
    video_id = _get_file_hash(file)

    thumbnail = get_thumbnail(file)
    thumbnail_path = thumbnail_utils.save_thumbnail(thumbnail, video_id)
    filepath = _save_media(file, video_id)

    return Video(
        video_id=video_id,
        title=_title_from_filename(file.filename),
        source=VideoSource.LOCAL,
        thumbnail_path=thumbnail_path,
        video_url=None,
        video_path=filepath,
        author_name=None,
    )
