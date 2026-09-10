from contextlib import asynccontextmanager
import io
import os
import pathlib
import tempfile
import zipfile

import logging

from pydantic import BaseModel
import uvicorn

from src import video_ingestion, youtube_utils, db_utils, local_files_utils

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from dotenv import load_dotenv

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


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
    <!doctype html>
    <html>
      <body>
        <h1>YouTube QR Code Generator</h1>

        <form method="post" action="/generate">
          <label for="urls">YouTube links, one per line:</label><br>
          <textarea
            id="urls"
            name="urls"
            rows="12"
            cols="70"
            required
          ></textarea><br><br>

          <button type="submit">Generate QR codes</button>
        </form>
      </body>
    </html>
    """


class URLGenerateRequest(BaseModel):
    urls: list[str]


@app.post("/api/generate/urls")
async def generate(request: URLGenerateRequest) -> StreamingResponse:
    video_urls = request.urls

    with db_utils.get_connection() as con:
        zip_buffer = video_ingestion.process_submissions(con, video_urls,
                                                         ingestion_func=youtube_utils.ingest_video)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition":
                'attachment; filename="youtube-qr-codes.zip"'
        },
    )

@app.post("/generate/files")
async def generate_files(files: list[UploadFile] = File(...)) -> StreamingResponse:
    with db_utils.get_connection() as con:
        zip_buffer = video_ingestion.process_submissions(con, files,
                                                         ingestion_func=local_files_utils.ingest_video)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition":
                'attachment; filename="local-qr-codes.zip"'
        },
    )


from src.web_app.player_routes import router as player_router
from src.web_app.tracking_routes import router as tracking_router
app.include_router(player_router)
app.include_router(tracking_router)

# chromium --kiosk --noerrdialogs --disable-infobars --no-first-run --disable-session-crached-bubble --autoplay-policy=no-user-gesture-required http://127.0.0.1:8000/player


def main() -> None:
    uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('PORT_NUMBER', 8000)))


if __name__ == '__main__':
    main()
