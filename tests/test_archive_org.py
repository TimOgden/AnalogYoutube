from src.external_sources.archive_org import ArchiveOrgSource
from dotenv import load_dotenv

load_dotenv(override=True)


def test_get_metadata():
    source = ArchiveOrgSource()
    metadata = source.get_metadata('vintage_cartoons')
    assert metadata


def test_list_items():
    source = ArchiveOrgSource()
    items = source.list_items('ThePinkPanther-cartoons')
    assert items
