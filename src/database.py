import os
import pathlib
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

DATABASE_PATH = pathlib.Path(
    os.environ.get("DATABSE_PATH", './data/analog-youtube.db')
)

def init_db() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.executescript(
            pathlib.Path("schema/schema.sql").read_text()
        )
        connection.commit()


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()