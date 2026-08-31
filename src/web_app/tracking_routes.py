import datetime
import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
import pandas as pd

from src import db_utils
from src.web_app import player_utils

router = APIRouter()


logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory='templates')


@router.get("/tracking")
async def get_tracking(request: Request) -> HTMLResponse:
    time_in_days = 14
    start_time = datetime.datetime.now() - datetime.timedelta(days=time_in_days)

    with db_utils.get_connection() as conn:
        df = player_utils.get_usage_since_per_video(conn=conn, start_time=start_time)
    df['watched_minutes'] = df['watched_seconds'] / 60

    try:
        return templates.TemplateResponse(
                request,
                "tracker.html.j2",
                {'tracking_data': df},
            )
    except Exception as e:
        logger.error(e)
        return HTMLResponse("<h1>Tracking Error</h1><p>Could not load viewing history.</p>", status_code=500)
