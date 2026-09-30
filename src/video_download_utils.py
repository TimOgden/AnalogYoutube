from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any
import logging

from PIL import Image
import cv2
from fastapi import UploadFile

from src.consts import MEDIA_PATH


logger = logging.getLogger()


def _probe_media(path: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries",
            "stream=codec_type,codec_name,width,height,pix_fmt,r_frame_rate",
            "-of", "json",
            "-preset", "veryfast",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return json.loads(result.stdout)


def video_is_playback_friendly(path: Path) -> bool:
    media = _probe_media(path)

    video = next(
        (
            stream
            for stream in media["streams"]
            if stream["codec_type"] == "video"
        ),
        None,
    )

    if video is None:
        return False

    audio = next(
        (
            stream
            for stream in media["streams"]
            if stream["codec_type"] == "audio"
        ),
        None,
    )

    if path.suffix.lower() != ".mp4":
        return False

    if video.get("codec_name") != "h264":
        return False

    if video.get("width", 0) > 1280:
        return False

    if video.get("height", 0) > 720:
        return False

    if video.get("pix_fmt") != "yuv420p":
        return False

    frame_rate = float(Fraction(video.get("r_frame_rate", "0/1")))

    if frame_rate > 60:
        return False

    if audio and audio.get("codec_name") != "aac":
        return False

    return True


def get_thumbnail(filepath: Path) -> Image.Image:
    frame_capture = cv2.VideoCapture(filepath)

    frame_count = int(frame_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    target_frame = int(frame_count * 0.1)

    frame_capture.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
    
    ret, frame = frame_capture.read() 
    frame_capture.release()

    if not ret:
        raise ValueError("Error getting frame.")
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(frame_rgb, mode='RGB')


def convert_to_mp4(path: Path, output_dir: Path, video_id: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{video_id}.mp4"

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i", str(path),
                "-vf",
                (
                    "scale='min(1280,iw)':'min(720,ih)'"
                    ":force_original_aspect_ratio=decrease"
                    ":force_divisible_by=2"
                ),
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "128k",
                "-movflags", "+faststart",
                str(output_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

    except subprocess.CalledProcessError as e:
        output_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"ffmpeg failed to convert {path}:\n{e.stderr}"
        ) from e

    return output_path


def save_media(file: UploadFile, videos_path: Path, video_id: str) -> Path:
    logger.info(f'Saving file {file.filename}...')
    path = videos_path / f'{video_id}.mp4'
    file.file.seek(0)
    logger.info(f'Writing file {file.filename} to disk...')
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return path
