from typing import Any, Literal, Protocol
from dataclasses import dataclass

ExternalItemType = Literal["collection", "playlist", "video"]


@dataclass(frozen=True)
class ExternalItem:
    id: str
    title: str
    type: ExternalItemType
    source: str
    parent_id: str | None = None
    thumbnail_url: str | None = None


@dataclass(frozen=True)
class DownloadableVideo:
    id: str
    title: str
    source: str
    download_url: str
    thumbnail_url: str | None = None


class ExternalSource(Protocol):
    def get_item(self, identifier: Any) -> ExternalItem:
        ...
    
    def list_items(self, identifier: Any | None = None) -> list[ExternalItem]:
        ...

    def list_videos(self, identifier: Any | None = None) -> list[DownloadableVideo]:
        ...

