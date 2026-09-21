from src.external_sources.external_sources_utils import _populate_library


def test_populate_library():
    identifiers = {
        'popeye-collection':
            {'displayName': 'Popeye the Sailor (1933)'},
        'ThePinkPanther-cartoons':
            {'displayName': 'The Pink Panther (1964)'},
    }
    config = {
        'sources': {
            'archive.org': {
                'identifiers': identifiers
            }
        }
    }

    library = _populate_library(config)
    assert 'archive.org' in library
    assert 'popeye-collection' in library['archive.org']
    assert library['archive.org']['popeye-collection'].display_name == 'Popeye the Sailor (1933)'

