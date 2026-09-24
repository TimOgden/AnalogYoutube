from dataclasses import dataclass, field
import datetime
import enum
import logging
from sqlite3 import Connection, Cursor
import time
import uuid

import pandas as pd

from src import db_utils
from src.db_utils import get_connection

logger = logging.getLogger(__name__)


MAX_HEARTBEAT_DELTA = 10
SAVE_INTERVAL = 30

active_sessions: dict[str, 'WatchSession'] = {}

class PlayingState(enum.Enum):
    INVALID = -1
    PLAYING = 1
    PAUSED = 2
    BUFFERING = 3
    ENDED = 0


@dataclass
class WatchSession:
    source: str
    video_id: str
    session_id: str

    pending_usage_seconds: float = 0
    is_playing: bool = False
    last_update: float = 0

    def _accumulate_watch_time(self) -> None:
        if not self.is_playing:
            return

        now = time.monotonic()

        if self.last_update is not None:
            elapsed = now - self.last_update

            self.pending_usage_seconds += min(
                elapsed,
                MAX_HEARTBEAT_DELTA,
            )

        self.last_update = now

    def handle_progress(self, actual_video_id: str) -> None:
        self.is_playing = True
        if actual_video_id != self.video_id:
            return

        self._accumulate_watch_time()
        self.maybe_save()

    def handle_state_change(self, state: int) -> None:
        self._accumulate_watch_time()

        self.is_playing = PlayingState(state) == PlayingState.PLAYING
        self.last_update = time.monotonic()

        self.save(end=PlayingState(state) == PlayingState.ENDED)

    def end(self) -> None:
        self._accumulate_watch_time()

        self.is_playing = False
        self.last_update = None

        self.save(end=True)
        logger.info(f'Ended watch session {self}.')

    def save(self, end: bool = False) -> None:
        now = datetime.datetime.now()
        with get_connection() as conn:
            logger.info(f'Saving {self.pending_usage_seconds:.2f} seconds to session {self}...')
            conn.execute(
                """
                INSERT INTO playback_usage
                (session_id, recorded_at, watched_seconds)
                VALUES (?, ?, ?)
                """,
                (
                    self.session_id,
                    now,
                    self.pending_usage_seconds,
                ),
            )
            self.pending_usage_seconds = 0

            if end:
                conn.execute(
                    """
                    UPDATE playback_sessions SET ended_at=? WHERE id=?
                    """,
                    (self.session_id, now)
                )
            
            conn.commit()

    def maybe_save(self) -> None:
        now = time.monotonic()

        if self.pending_usage_seconds >= SAVE_INTERVAL:
            self.save()
            self.last_update = now


def create_watch_session(source: str, video_id: str) -> WatchSession:
    session_id = str(uuid.uuid4())
    session = WatchSession(source=source, video_id=video_id, session_id=session_id)

    for existing_session in active_sessions.values():
        existing_session.end()
    active_sessions[session.session_id] = session

    logger.info(f'Created watch session {session_id} for video {video_id}.')
    return session


def get_session(session_id: str) -> WatchSession:
    session = active_sessions.get(session_id)

    if session is None:
        active_sessions.update(_reload_active_sessions())
        session = active_sessions.get(session_id)

    if session is None:
        raise KeyError(f"Unknown playback session: {session_id}")

    return session


def _reload_active_sessions() -> dict[str, WatchSession]:
    logger.info('Reloading sessions from db...')
    sessions = {}
    with db_utils.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT * FROM playback_sessions ORDER BY created_at DESC LIMIT 100""")
        rows = cur.fetchall()
        for row in rows:
            sessions[row['id']] = WatchSession(source=row['source'], 
                                               video_id=row['video_id'], 
                                               session_id=row['id'])
    return sessions


def get_usage_since(cur: Cursor, start_time: datetime.datetime) -> float:
    cur.execute("""SELECT COALESCE(SUM(watched_seconds), 0)
                FROM playback_usage
                WHERE recorded_at >= ?;""", parameters=(start_time))
    usage = float(cur.fetchone()[0])
    return usage


def get_usage_since_per_video(conn: Connection, start_time: datetime.datetime) -> pd.DataFrame:
    df = pd.read_sql("""
        SELECT
            v.video_id,
            v.title,
            v.author_name,
            v.source,
            v.thumbnail_path,
            ps.id as session_id,
            COALESCE(SUM(pu.watched_seconds), 0) AS watched_seconds
        FROM playback_usage pu
        JOIN playback_sessions ps
            ON ps.id = pu.session_id
        JOIN videos v
            ON v.video_id = ps.video_id
        WHERE pu.recorded_at >= ?
        GROUP BY v.video_id, v.title
        ORDER BY watched_seconds DESC
        """, params=(start_time,), con=conn)
    return df


def submit_new_session(session: WatchSession, conn: Connection) -> None:
    now = datetime.datetime.now()
    conn.execute("""INSERT INTO playback_sessions
                (id, source, video_id, created_at)
                VALUES (?, ?, ?, ?)""", (session.session_id, session.source, session.video_id, now))
