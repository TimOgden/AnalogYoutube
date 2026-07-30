from contextlib import contextmanager
import os
import pathlib
import sqlite3
import logging
from typing import Iterator

logger = logging.getLogger()

SCHEMA_PATH = pathlib.Path(os.environ['schema_path'], 'schema.sql')
DB_PATH = pathlib.Path(os.environ['database_path'])
db_initialized = False

def initialize_db() -> None:
    if db_initialized:
        return
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if not SCHEMA_PATH.exists():
            raise FileNotFoundError(f"Schema file not found at: {SCHEMA_PATH.resolve()}")
        
        with open(SCHEMA_PATH, 'r') as f:
            sql_script = f.read()

        # 3. Execute the entire script
        cursor.executescript(sql_script)
        logger.info("Database schema initialized successfully.")
        db_initialized = True
    except sqlite3.Error as e:
        logger.error(f"SQLite error during initialization: {e}")
        # Depending on severity, you might want to raise or handle this gracefully
        raise e 
    finally:
        if conn:
            conn.close()


def db_cursor() -> Iterator[sqlite3.Cursor]:
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        logger.error(e)
        if conn is not None:
             conn.rollback()
