import io
import pathlib
import tempfile
import zipfile


from fastapi.concurrency import asynccontextmanager
import logging
from src import youtube_utils, qr_generator_utils
from src import database

from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse

download_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='youtube-download')

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(
    title='Analog Youtube',
    lifespan=lifespan,
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


@app.post("/generate")
def generate(urls: str = Form(...)) -> StreamingResponse:
    video_urls = [
        line.strip()
        for line in urls.splitlines()
        if line.strip()
    ]

    zip_buffer = io.BytesIO()

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = pathlib.Path(temp_dir)

        with database.get_connection() as conn:
            html_files = []
            for url in video_urls:
                video = youtube_utils.get_youtube_video(url)
                video_card = youtube_utils.get_youtube_card_by_id(video.yt.video_id, conn)

                if video_card is None:
                    video_card = youtube_utils.create_or_update_youtube_card(conn, video, video_path=None, thumbnail_path=None,
                                                                             download_status=None)
                
                if video_card.download_status != youtube_utils.DownloadStatus.READY:
                    download_executor.submit(youtube_utils.download_video_worker, video)
                else:
                    logger.info(f'Skipping download of youtube video "{video.title}", already downloaded.')

                html_filepath = qr_generator_utils.populate_qr_code_template(video, output_dir=output_dir)
                html_files.append(html_filepath)

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
                'attachment; filename="youtube-qr-codes.zip"'
        },
    )


@app.get('/play/{video_id}', response_class=HTMLResponse)
def play_video(video_id: int) -> str:
    with database.get_connection() as conn:
        video = youtube_utils.get_youtube_card_by_id(video_id, conn)

    if video is None:
        raise HTTPException(
            status_code=404,
            detail=f'Unknown video card: {video_id}'
        )
    
    return f"""
    <!doctype html>
    <html>
        <body>
            <h1>{video["title"]}</h1>
            <p>Video found. Playback integration comes next.</p>
        </body>
    </html>
    """
