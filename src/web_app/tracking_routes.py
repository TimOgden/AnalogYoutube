import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
import pandas as pd

from src import db_utils

router = APIRouter()


logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory='templates')


@router.get("/tracking")
async def get_tracking(request: Request) -> HTMLResponse:
    sql = """
        SELECT h.device, h.watchDt,
        h.video_id, v.youtube_url as url, v.title
        FROM watchHistory h
        LEFT JOIN videos v on h.video_id=v.video_id;
    """
    with db_utils.get_connection() as conn:
        df = pd.read_sql(sql, conn)

    try:
        return templates.TemplateResponse(
                request,
                "tracker.html.j2",
                {'tracking_data': df},
            )
    except Exception as e:
        logger.error(e)
        return HTMLResponse("<h1>Tracking Error</h1><p>Could not load viewing history.</p>", status_code=500)
