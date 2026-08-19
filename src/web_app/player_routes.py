import datetime
import sqlite3
import traceback

from fastapi import APIRouter, HTTPException, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import logging

from src import db_utils, youtube_utils
from src.consts import VIDEO_ID_PATTERN

logger = logging.getLogger(__name__)

router = APIRouter()

connected_players: set[WebSocket] = set()
templates = Jinja2Templates(directory='templates')


class PlayRequest(BaseModel):
    video_id: str
    device_id: str


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
            await websocket.receive_text()
    except Exception as e:
        logger.error('Failed to receive text from connected websocket')
        raise e
    finally:
        connected_players.discard(websocket)


@router.post('/api/play')
async def play_video(request: PlayRequest) -> dict[str, str]:
    if not VIDEO_ID_PATTERN.fullmatch(request.video_id):
        raise HTTPException(
            status_code=400,
            detail='Invalid Youtube video id'
        )

    disconnected: list[WebSocket] = []
    for websocket in connected_players:
        try:
            logger.info(f'Sending video id {request.video_id} to websocket {websocket}...')
            await websocket.send_json(
                {
                    'type': 'play',
                    'video_id': request.video_id
                }
            )
            with db_utils.get_connection() as cur:
                submit_watch_to_db(cur, play_request=request)
        except Exception as e:
            logger.error(f'Error sending video id {request.video_id} to websocket {websocket}')
            traceback.print_exc()
            disconnected.append(websocket)
    
    for websocket in disconnected:
        connected_players.discard(websocket)
    return {'status': 'playing'}


def submit_watch_to_db(cur: sqlite3.Cursor, play_request: PlayRequest) -> None:
    logger.info(f'Submitting watch to db: {play_request}')
    
    video = youtube_utils.video_from_id(play_request.video_id)
    youtube_utils.submit_videos_to_db(cur, [video])
    
    sql = """INSERT INTO watchHistory (video_id, device, watchDt) VALUES (?, ?, ?);"""
    now_dt = datetime.datetime.now()
    cur.execute(sql, (play_request.video_id, play_request.device_id, now_dt))
