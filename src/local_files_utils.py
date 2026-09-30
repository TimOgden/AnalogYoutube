import hashlib
import logging
import shutil
import tempfile

from src.consts import MEDIA_PATH
from src.video_utils import Video, VideoSource
from src import thumbnail_utils, video_download_utils
from fastapi import UploadFile
from pathlib import Path


logger = logging.getLogger(__name__)


def _title_from_filename(filename: Path | str) -> str:
    if isinstance(filename, str):
        filename = Path(filename)
    
    while filename.suffix:
        filename = filename.with_suffix('')
    return filename.name


def _get_file_hash(file: UploadFile) -> str:
    digest = hashlib.sha256()
    file.file.seek(0)

    for chunk in iter(lambda: file.file.read(1024 * 1024), b''):
        digest.update(chunk)

    file.file.seek(0)
    return digest.hexdigest()


def ingest_video(file: UploadFile) -> Video:
    video_id = _get_file_hash(file)

    path = MEDIA_PATH / 'videos'
    path.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=path) as temp_dir:
        tmp_path = video_download_utils.save_media(file, Path(temp_dir), video_id)

        if video_download_utils.video_is_playback_friendly(tmp_path):
            filepath = path / f'{video_id}.mp4'
            shutil.copy2(tmp_path, filepath)
        else:
            logger.info(f'Normalizing {file.filename} to mp4 and appropriate size...')
            filepath = video_download_utils.convert_to_mp4(tmp_path, output_dir=path, video_id=video_id)
    thumbnail = video_download_utils.get_thumbnail(filepath)
    logger.info(f'Saving thumbnail for file {file.filename}...')
    thumbnail_path = thumbnail_utils.save_thumbnail(thumbnail, video_id)

    return Video(
        video_id=video_id,
        title=_title_from_filename(file.filename),
        source=VideoSource.LOCAL,
        thumbnail_path=thumbnail_path,
        video_url=None,
        video_path=filepath,
        author_name=None,
    )
