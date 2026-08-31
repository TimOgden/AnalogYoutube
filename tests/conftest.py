
from typing import Iterator

import pytest

from src import db_utils


@pytest.fixture
def test_conn() -> Iterator:
    with db_utils.get_connection(test=True) as conn:
        yield conn
