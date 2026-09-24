from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel


ExternalItemType = Literal["collection", "playlist", "video"]


@dataclass(frozen=True)
class ExternalItem:
    id: str
    title: str
    type: ExternalItemType
    source: str
    parent_id: str | None = None
    thumbnail_url: str | None = None
    videos: list[DownloadableVideo] = field(default_factory=list)


@dataclass
class DownloadableVideo:
    video_id: str
    title: str
    source: str
    playlist_id: str | None
    download_url: str | None
    thumbnail_url: str | None = None
    external_url: str | None = None


@dataclass(frozen=True)
class Playlist:
    id: str
    display_name: str | None
    videos: list[DownloadableVideo]


class LibraryVideo(BaseModel):
    id: str
    title: str
    source: str
    download_url: str | None
    thumbnail_url: str | None
    external_url: str | None
    playlist_id: str | None


LIBRARY = dict[str, dict[str, Playlist]]
