import collections

import yaml
from src.external_sources.archive_org import ArchiveOrgSource
from src.external_sources.models import LIBRARY


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
        for identifier in source['identifiers']:
            library[source_name][identifier] = source_engine.list_videos(identifier)
    return library


def get_curated_library() -> LIBRARY:
    config = _load_config()
    return _populate_library(config)
