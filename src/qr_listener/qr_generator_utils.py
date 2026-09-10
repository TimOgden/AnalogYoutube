import io
import re
import pathlib
from fastapi import File
import qrcode
import qrcode.image.svg
import base64
from src import youtube_utils, db_utils, thumbnail_utils
from jinja2 import Environment, FileSystemLoader
from sqlite3 import Connection
from PIL.Image import Image
from markupsafe import Markup
import uuid

from src.qr_listener.qr_generator_models import CardData
from src.video_utils import Video


SOURCE_CODES = {
    'local': 'LC',
    'youtube': 'YT',
    'library': 'LB'
}


def generate_qr_code(data: str, source: str) -> Image:
    if source not in SOURCE_CODES:
        raise ValueError(f'Unknown source: {source}, \
                         must be one of {list(SOURCE_CODES.keys())}')
    data = f'{SOURCE_CODES[source]}:{data}'
    image = qrcode.make(
        data,
        image_factory=qrcode.image.svg.SvgPathImage,
    )
    return image


def image_to_data_uri(image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")

    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def svg_to_markup(qr_svg) -> Markup:
    if isinstance(qr_svg, bytes):
        qr_svg = qr_svg.decode("utf-8")

    return Markup(qr_svg)


def populate_qr_code_template(video: Video, output_path: pathlib.Path) -> pathlib.Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    qr_code_url = generate_qr_code(video.video_id, video.source.value)

    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=True,
    )
    template = env.get_template('video_qr.html.j2')
    html = template.render(
        title=video.title,
        thumbnail=video.thumbnail_path,
        svg_url=qr_code_url,
    )

    with open(output_path, 'w') as f:
        f.write(html)
    return output_path
