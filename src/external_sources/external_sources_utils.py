import collections

import yaml
from src.external_sources.archive_org import ArchiveOrgSource
from src.external_sources.models import LIBRARY, Playlist


SOURCES = {
    'archive.org': ArchiveOrgSource(),
}


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
