from typing import Protocol

from src.external_sources.models import DownloadableVideo


class ExternalSource(Protocol):
    def get_item(self, identifier: str) -> dict:
        ...

    def list_videos(self, identifier: str | None = None) -> list[DownloadableVideo]:
        ...

