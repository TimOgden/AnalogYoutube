import collections
from pathlib import Path
import tempfile

from PIL import Image
import cv2
import yaml
from src.external_sources.archive_org import ArchiveOrgSource
from src.external_sources.models import LIBRARY, DownloadableVideo, Playlist
from src.video_models import Video, VideoSource


SOURCES = {
    'archive.org': ArchiveOrgSource(),
}


def _save_media(video: DownloadableVideo) -> Path:
    source_engine = SOURCES[video.source]
    path = source_engine.download_video(video)
    return path


def _get_thumbnail(filepath: Path) -> Image.Image:
    frame_capture = cv2.VideoCapture(filepath)

    frame_count = int(frame_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    target_frame = int(frame_count * 0.1)

    frame_capture.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

    ret, frame = frame_capture.read()
    frame_capture.release()

    if not ret:
        raise ValueError("Error getting frame.")

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(frame_rgb, mode="RGB")


def _save_thumbnail(thumbnail: Image.Image, video_id: str) -> Path:
    path = Path('media/thumbnails') / f'{video_id}.png'
    thumbnail.save(path)
    return path


def ingest_video(video: DownloadableVideo) -> Video:
    video_id = video.id
    filepath = _save_media(video)
    thumbnail = _get_thumbnail(filepath)
    thumbnail_path = _save_thumbnail(thumbnail, video_id)

    return Video(
        video_id=video_id,
        title=video.title,
        source=VideoSource.LIBRARY,
        thumbnail_path=thumbnail_path,
        video_url=video.external_url,
        author_name=video.source,
    )


def _load_config() -> dict:
    with open('config/curated_library.yaml', 'r') as f:
        return yaml.safe_load(f)


def _populate_library(config: dict) -> LIBRARY:
    library = collections.defaultdict(dict)
    for source_name, source in config['sources'].items():
        source_engine = SOURCES[source_name]
        for identifier, identifier_values in source['identifiers'].items():
            videos = source_engine.list_videos(identifier)

            playlist = Playlist(id=identifier, display_name=identifier_values.get('displayName', identifier),
                                videos=videos)
            library[source_name][identifier] = playlist
    return library


def get_curated_library() -> LIBRARY:
    config = _load_config()
    return _populate_library(config)
