from fastapi import APIRouter, HTTPException, WebSocket
from pydantic import BaseModel
import logging

from src.consts import VIDEO_ID_PATTERN

logger = logging.getLogger(__name__)

router = APIRouter()

connected_players: set[WebSocket] = set()


class PlayRequest(BaseModel):
    video_id: str


@router.websocket('/ws/player')
async def player_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    connected_players.add(websocket)

    try:
        while True:
            await websocket.receive_text()
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
            await websocket.send_json(
                {
                    'type': 'play',
                    'video_id': request.video_id
                }
            )
        except Exception as e:
            logger.error(f'Error sending video id {request.video_id} to websocket {websocket}')
            disconnected.append(websocket)
    
    for websocket in disconnected:
        connected_players.discard(websocket)
    return {'status': 'playing'}
