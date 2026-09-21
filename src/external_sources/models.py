from dataclasses import dataclass, field
from typing import Literal


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


@dataclass(frozen=True)
class DownloadableVideo:
    id: str
    title: str
    source: str
    download_url: str
    thumbnail_url: str | None = None
    external_url: str | None = None


LIBRARY = dict[str, dict[str, list[DownloadableVideo]]]
