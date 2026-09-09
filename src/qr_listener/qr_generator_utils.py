import io
import re
import pathlib
from fastapi import File
import qrcode
import qrcode.image.svg
import base64
from src import youtube_utils
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

from src.qr_listener.qr_generator_models import CardData


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


def generate_qr_code(data: str) -> str:
    image = qrcode.make(
        data,
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


def populate_qr_code_template(card: CardData, output_path: pathlib.Path) -> pathlib.Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    thumbnail_url = image_to_data_uri(card.thumbnail)
    qr_code_url = generate_qr_code(card.video_id)

    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=True,
    )
    template = env.get_template('video_qr.html.j2')
    html = template.render(
        title=card.title,
        thumbnail=thumbnail_url,
        svg_url=qr_code_url,
    )

    with open(output_path, 'w') as f:
        f.write(html)
    return output_path


def create_card_from_youtube(video: youtube_utils.YoutubeVideo) -> CardData:
    return CardData(title=video.title, thumbnail=video.thumbnail, video_id=video.video_id)


async def create_card_from_file(file: File) -> CardData:
    filename = pathlib.Path(file.filename)
    content = await file.read()

    if not filename.suffix in ('.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.webm'):
        raise ValueError(f'Invalid file type: {filename.suffix}')
