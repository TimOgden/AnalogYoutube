from dataclasses import dataclass, field
from enum import Enum

from pathlib import Path


SOURCE_CODES = {
    'local': 'LC',
    'youtube': 'YT',
    'library': 'LB',
    
    'LC': 'local',
    'YT': 'youtube',
    'LB': 'library',
}


class VideoSource(str, Enum):
    LOCAL = 'local'
    YOUTUBE = 'youtube'
    LIBRARY = 'library'


@dataclass(frozen=True)
class Video:
    video_id: str
    title: str
    source: VideoSource
    thumbnail_path: Path
    video_url: str | None = field(default=None)
    author_name: str | None = field(default=None)