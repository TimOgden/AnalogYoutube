import io
import os
import re
import pathlib
import qrcode
import qrcode.image.svg
import base64
from src import youtube_utils
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from urllib.parse import urlencode


PLAYER_BASE = 'AY'

def sanitize_filename(name: str) -> str:
    # Replace characters that are illegal on Windows/macOS/Linux
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    # Remove trailing dots/spaces
    return name.rstrip(". ")


def create_player_url(
    base: str,
    youtube_video_id: str,
) -> str:
    return f"{base}:{youtube_video_id}"


def generate_qr_svg_data_uri(url: str) -> str:
    image = qrcode.make(
        url,
        image_factory=qrcode.image.svg.SvgPathImage,
    )

    buffer = io.BytesIO()
    image.save(buffer)

    encoded_svg = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded_svg}"


def image_to_data_uri(image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")

    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def svg_to_markup(qr_svg) -> Markup:
    if isinstance(qr_svg, bytes):
        qr_svg = qr_svg.decode("utf-8")

    return Markup(qr_svg)


def populate_qr_code_template(video: youtube_utils.YoutubeVideo, output_dir: pathlib.Path | None = None) -> pathlib.Path:
    if output_dir is None:
        output_dir = pathlib.Path('tmp')
    
    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=True,
    )

    template = env.get_template("video.html.j2")

    thumbnail_data_uri = image_to_data_uri(video.thumbnail)
    svg_path = f'AY:{video.video_id}'
    html = template.render(
        title=video.title,
        thumbnail=thumbnail_data_uri,
        svg_url=generate_qr_svg_data_uri(svg_path),
    )

    filename = output_dir / f'{sanitize_filename(video.title)}.html'
    with open(filename, "w") as f:
        f.write(html)
    return filename
