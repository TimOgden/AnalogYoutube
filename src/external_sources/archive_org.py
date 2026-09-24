import json
import os
from pathlib import Path

import requests

from src.external_sources.models import DownloadableVideo
from internetarchive import download, get_item


class ArchiveOrgSource:
    METADATA_URL = 'http://archive.org/metadata/{identifier}'
    DETAILS_URL = 'https://archive.org/details/{identifier}/{video_name}'

    def get_item(self, identifier: str) -> dict:
        resp = requests.get(self.METADATA_URL\
                            .format(identifier=identifier))
        resp.raise_for_status()

        return json.loads(resp.content)
            
    
    def list_videos(self, identifier: str | None = None) -> list[DownloadableVideo]:
        metadata = self.get_item(identifier=identifier)

        videos = []
        for file in metadata['files']:
            if file.get('format') not in ['h.264', 'MPEG4']:
                continue

            video_name = file['name'].replace(' ', '+')
            videos.append(DownloadableVideo(
                video_id=file['sha1'],
                title=str(Path(file['name']).with_suffix('')),
                source='archive.org',
                download_url=None,
                thumbnail_url=None,
                playlist_id=identifier,
                external_url=self.DETAILS_URL.format(identifier=identifier, video_name=video_name)
            ))
        return videos

    def download_video(self, video: DownloadableVideo) -> Path:
        download(identifier=video.playlist_id, glob_pattern=f'{video.title}.mp4', destdir='media/videos/')
        return Path('media') / 'videos' / video.playlist_id / f'{video.title}.mp4'

