import datetime
import sqlite3
import traceback
from typing import Literal
from src.web_app import player_utils
from enum import Enum

from fastapi import APIRouter, HTTPException, WebSocket
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import logging

from src import db_utils, video_utils, youtube_utils
from src.consts import MEDIA_PATH, VIDEO_ID_PATTERN

logger = logging.getLogger(__name__)

router = APIRouter()

connected_players: set[WebSocket] = set()
templates = Jinja2Templates(directory='templates')


class PlayRequest(BaseModel):
    source: Literal['youtube'] | Literal['local'] | Literal['']
    video_id: str
    device_id: str


class PlayerCommand(str, Enum):
    PLAY = "play"
    PAUSE = "pause"
    PLAY_PAUSE = "play_pause"
    SEEK_FORWARD = "seek_forward"
    SEEK_BACKWARD = "seek_backward"
    SCRUB_FORWARD = "scrub_forward_start"
    SCRUB_BACKWARD = "scrub_backward_start"
    SCRUB_STOP = "scrub_stop"


class ControlRequest(BaseModel):
    command: PlayerCommand


async def broadcast(message: dict) -> None:
    disconnected = []

    for websocket in connected_players:
        try:
            await websocket.send_json(message)
        except Exception:
            disconnected.append(websocket)

    for websocket in disconnected:
        connected_players.discard(websocket)


@router.post("/api/control")
async def control_player(request: ControlRequest):
    logger.info(f'Sending command: {request} to player...')
    await broadcast({
        "type": "control",
        "command": request.command,
    })

    return {"status": "ok"}


@router.get("/player", response_class=HTMLResponse)
async def player(request: Request):
    return templates.TemplateResponse(
        request,
        "player.html.j2",
        {},
    )


@router.websocket('/ws/player')
async def player_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    connected_players.add(websocket)

    try:
        while True:
            message = await websocket.receive_json()

            message_type = message['type']
            actual_video_id = message['actual_video_id']
            session_id = message['session_id']

            session = player_utils.get_session(session_id)

            if session is None:
                logger.warning(
                    'Received message for unknown session %s',
                    session_id,
                )
                continue

            if message_type == 'playback_progress':
                logger.info(f'Received playback_progress socket message {message} for session {session}')
                session.handle_progress(actual_video_id=actual_video_id)
            elif message_type == 'player_state':
                logger.info(f'Received player state change socket message {message} for session {session}')
                session.handle_state_change(state=message['state'])
    except Exception as e:
        logger.error('Failed to receive text from connected websocket')
        raise e
    finally:
        connected_players.discard(websocket)


@router.get('/api/localVideos/{video_id}')
def get_local_video(video_id: str):
    path = MEDIA_PATH / 'videos' / f"{video_id}.mp4"

    if not path.exists():
        raise HTTPException(status_code=404)

    return FileResponse(
        path,
        media_type="video/mp4",
    )


@router.post('/api/play')
async def play_video(request: PlayRequest) -> dict[str, str]:
    session = player_utils.create_watch_session(request.source, request.video_id)
    with db_utils.get_connection() as cur:
        player_utils.submit_new_session(session, cur)

    disconnected: list[WebSocket] = []
    for websocket in connected_players:
        try:
            logger.info(f'Sending video id {request.video_id} to websocket {websocket}...')
            await broadcast({
                    'type': 'play',
                    'source': request.source,
                    'video_id': request.video_id,
                    'session_id': session.session_id
                }
            )

        except Exception as e:
            logger.error(f'Error sending video id {request.video_id} to websocket {websocket}')
            traceback.print_exc()
            disconnected.append(websocket)
    
    for websocket in disconnected:
        connected_players.discard(websocket)
    return {'status': 'playing', 'session_id': session.session_id}


def submit_video_to_db(cur: sqlite3.Cursor, play_request: PlayRequest) -> None:
    logger.info(f'Submitting watch to db: {play_request}')

    video = youtube_utils.video_from_id(play_request.video_id)
    youtube_utils.submit_videos_to_db(cur, [video])
