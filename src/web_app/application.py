from contextlib import asynccontextmanager
import io
import json
import os
import pathlib
import subprocess
import tempfile
import zipfile

import logging

from pydantic import BaseModel
import requests
import uvicorn

from src import video_utils, youtube_utils, db_utils, local_files_utils
from src.external_sources.models import DownloadableVideo

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from packaging.version import InvalidVersion, Version
from dotenv import load_dotenv

from src.video_models import Video

load_dotenv(override=True)


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_utils.initialize_database()
    yield

app = FastAPI(
    title='Analog Youtube',
    lifespan=lifespan
)


class URLGenerateRequest(BaseModel):
    urls: list[str]


@app.post("/api/generate/urls")
async def generate(request: URLGenerateRequest) -> StreamingResponse:
    video_urls = request.urls

    with db_utils.get_connection() as con:
        zip_buffer = video_utils.process_submissions(con, video_urls,
                                                         ingestion_func=youtube_utils.ingest_video)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition":
                'attachment; filename="youtube-qr-codes.zip"'
        },
    )

@app.post("/api/generate/files")
async def generate_files(files: list[UploadFile] = File(...)) -> StreamingResponse:
    with db_utils.get_connection() as con:
        zip_buffer = video_utils.process_submissions(con, files,
                                                         ingestion_func=local_files_utils.ingest_video)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition":
                'attachment; filename="local-qr-codes.zip"'
        },
    )


class SelectionGenerateRequest(BaseModel):
    videos: list[DownloadableVideo]


@app.post('/api/generate/selections')
async def generate_external_source(request: SelectionGenerateRequest):
    with db_utils.get_connection() as con:
        zip_buffer = video_utils.process_submissions(con, request.videos,
                                                     ingestion_func=external_sources_utils.ingest_video)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition":
                'attachment; filename="local-qr-codes.zip"'
        },
    )


@app.post('/api/generate/multi')
async def generate_multi(
    library_selections: str = Form("[]"),
    youtube_urls: str = Form("[]"),
    files: list[UploadFile] | None = File(None),
):
    zip_buffer = io.BytesIO()
    selected_videos = json.loads(library_selections)
    submitted_urls = json.loads(youtube_urls)
    submitted_files = files or []
            
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = pathlib.Path(temp_dir)

        html_files = []
        with db_utils.get_connection() as conn:
            external_files = video_utils.process_new_submissions(conn, selected_videos,
                                                                 ingestion_func=external_sources_utils.ingest_video,
                                                                 output_dir=output_dir)
            local_files = video_utils.process_new_submissions(conn, submitted_files,
                                                              ingestion_func=local_files_utils.ingest_video,
                                                              output_dir=output_dir)
            youtube_files = video_utils.process_new_submissions(conn, submitted_urls,
                                                                ingestion_func=youtube_utils.ingest_video,
                                                                output_dir=output_dir)
            html_files.extend(external_files + local_files + youtube_files)

        with zipfile.ZipFile(
                zip_buffer,
                mode="w",
                compression=zipfile.ZIP_DEFLATED,
            ) as archive:
                for file_path in html_files:
                    archive.write(file_path, arcname=file_path.name)

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition":
                'attachment; filename="qr-codes.zip"'
        },
    )
        


class MultiRegenerateRequest(BaseModel):
    videos: list[Video]


@app.post('/api/regenerate/multi')
async def regenerate_multi(request: MultiRegenerateRequest):
    with db_utils.get_connection() as conn:
        zip_buffer = video_utils.process_regenerate_submissions(conn, request.videos)
    return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition":
                    'attachment; filename="local-qr-codes.zip"'
            },
        )


UPDATE_SCRIPT_PATH = pathlib.Path(
    os.getenv('UPDATE_SCRIPT_PATH', '/opt/analog-youtube/deploy/update.sh')
)
LATEST_RELEASE_URL = (
    "https://api.github.com/repos/TimOgden/AnalogYoutube/releases/latest"
)


@app.get("/api/checkUpdates")
def check_updates() -> dict[str, str | bool]:
    current_version = os.environ.get("APP_VERSION", "unknown")

    try:
        response = requests.get(
            LATEST_RELEASE_URL,
            headers={
                "Accept": "application/vnd.github+json",
            },
            timeout=10,
        )
        response.raise_for_status()

        release = response.json()
        latest_version = release["tag_name"]

    except (requests.RequestException, KeyError) as e:
        logger.exception("Failed to check GitHub for updates.")

        raise HTTPException(
            status_code=502,
            detail="Unable to check for updates.",
        ) from e

    try:
        update_available = (
            current_version == "unknown"
            or Version(latest_version.removeprefix("v"))
            > Version(current_version.removeprefix("v"))
        )
    except InvalidVersion:
        logger.warning(
            "Could not compare versions: current=%r latest=%r",
            current_version,
            latest_version,
        )
        update_available = False

    return {
        "current_version": current_version,
        "latest_version": latest_version,
        "update_available": update_available,
    }


UPDATE_REQUEST = pathlib.Path("/runtime/update-request")


@app.post("/api/update", status_code=202)
def update():
    UPDATE_REQUEST.touch()

    return {
        "status": "update_requested",
    }


from src.external_sources import external_sources_utils
from src.external_sources.models import DownloadableVideo
from src.web_app.player_routes import router as player_router
from src.web_app.tracking_routes import router as tracking_router
from src.web_app.library_routes import router as library_router
from src.web_app.video_routes import router as video_router
app.include_router(player_router)
app.include_router(tracking_router)
app.include_router(library_router)
app.include_router(video_router)
FRONTEND_DIST = pathlib.Path(
    os.getenv('FRONTEND_DIST', '/app/frontend-dist')
)
if FRONTEND_DIST.is_dir():
    app.mount(
        '/',
        StaticFiles(directory=FRONTEND_DIST, html=True),
        name='frontend',
    )

# chromium --kiosk --noerrdialogs --disable-infobars --no-first-run --disable-session-crached-bubble --autoplay-policy=no-user-gesture-required http://127.0.0.1:1234/player
# local: e8a2ed3b-90eb-4744-a873-de3b44e0b6ff
# library: 1b12fb00e0e6799fe9a3ae0147a5f631afd24b1b

def main() -> None:
    uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('PORT_NUMBER', 8000)))


if __name__ == '__main__':
    main()
