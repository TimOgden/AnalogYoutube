import datetime
import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
import pandas as pd

from src import db_utils
from src.web_app import player_utils
from src.web_app.tracking_models import TrackingResponse

router = APIRouter()


logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory='templates')


@router.get("/api/tracking")
async def get_tracking(duration: int) -> TrackingResponse:
    time_in_days = duration
    start_time = datetime.datetime.now() - datetime.timedelta(days=time_in_days)

    with db_utils.get_connection() as conn:
        df = player_utils.get_usage_since_per_video(conn=conn, start_time=start_time)
    df['watched_minutes'] = df['watched_seconds'] / 60

    total_watched_minutes = df['watched_minutes'].sum()
    return TrackingResponse(by_video_df=df.to_dict(orient='records'), total_watched_minutes=total_watched_minutes)
