from src.external_sources.external_sources_utils import _populate_library


def test_populate_library():
    identifiers = ['popeye-pubdomain', 'ThePinkPanther-cartoons']
    config = {
        'sources': {
            'archive.org': {
                'identifiers': identifiers
            }
        }
    }

    library = _populate_library(config)
    assert 'archive.org' in library
    assert identifiers[0] in library['archive.org']
    assert library['archive.org'][identifiers[0]][0].source == 'archive.org'

