import io
import pathlib
import tempfile
import zipfile

import logging

from fastapi.templating import Jinja2Templates
from src.qr_listener import qr_generator_utils
from src import youtube_utils

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from dotenv import load_dotenv

templates = Jinja2Templates(directory='templates')
load_dotenv(override=True)


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


app = FastAPI(
    title='Analog Youtube',
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

        html_files = []
        for url in video_urls:
            video = youtube_utils.get_youtube_video(url)
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
