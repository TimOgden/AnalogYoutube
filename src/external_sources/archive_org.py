import json
import os

import requests

from src.external_sources.base import ExternalItem, DownloadableVideo


class ArchiveOrgSource:
    METADATA_URL = 'http://archive.org/metadata/{identifier}'

    def get_metadata(self, identifier: str) -> dict:
        resp = requests.get(self.METADATA_URL\
                            .format(identifier=identifier))
        resp.raise_for_status()

        return json.loads(resp.content)

    def list_items(self, identifier: str | None = None) -> list[ExternalItem]:
        metadata = self.get_metadata(identifier)
        for key in metadata:
            ...
    
    def list_collection(self, item_id: str | None = None) -> list[DownloadableVideo]:
        ...
