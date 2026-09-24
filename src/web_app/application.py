from contextlib import asynccontextmanager
import io
import json
import os
import pathlib
import tempfile
import zipfile

import logging

from pydantic import BaseModel
import uvicorn

from src import video_utils, youtube_utils, db_utils, local_files_utils

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from dotenv import load_dotenv

from src.external_sources.models import LibraryVideo
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
    ingestion_funcs = {
        'youtube': youtube_utils.ingest_video_by_id,
        'library': external_sources_utils.ingest_video,
        'local': local_files_utils.ingest_video_by_id,
    }
    source_submissions = {}
    for source in ingestion_funcs:
        source_submissions[source] = [video for video in request.videos if video.source == source]

    with db_utils.get_connection() as conn:
        zip_buffer = video_utils.process_multi_submissions(conn, source_submissions,
                                                           ingestion_funcs=ingestion_funcs)
    return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition":
                    'attachment; filename="local-qr-codes.zip"'
            },
        )


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

# chromium --kiosk --noerrdialogs --disable-infobars --no-first-run --disable-session-crached-bubble --autoplay-policy=no-user-gesture-required http://127.0.0.1:1234/player
# local: e8a2ed3b-90eb-4744-a873-de3b44e0b6ff
# library: 1b12fb00e0e6799fe9a3ae0147a5f631afd24b1b

def main() -> None:
    uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('PORT_NUMBER', 8000)))


if __name__ == '__main__':
    main()
