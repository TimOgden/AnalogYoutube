from contextlib import contextmanager
import os
import pathlib
import sqlite3
import logging
from typing import Iterator

DATABASE_PATH = pathlib.Path(os.getenv('database_path', './data/analog-youtube.db'))
SCHEMA_PATH = pathlib.Path(os.getenv('schema_path', './schema/schema.sql'))

logger = logging.getLogger()

def initialize_database() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA journal_mode=WAL")

        with open(SCHEMA_PATH, 'r') as f:
            connection.executescript(f.read())

        connection.commit()


@contextmanager
def get_connection(test: bool = False) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        if test:
            connection.rollback()
        else:
            connection.close()
