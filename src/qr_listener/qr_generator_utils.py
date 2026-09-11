import io
import mimetypes
import pathlib
import qrcode
import qrcode.image.svg
import base64
from jinja2 import Environment, FileSystemLoader
from PIL.Image import Image
from markupsafe import Markup

from src.video_models import Video



SOURCE_CODES = {
    'local': 'LC',
    'youtube': 'YT',
    'library': 'LB'
}


def generate_qr_code(data: str, source: str) -> qrcode.image.svg.SvgPathImage:
    if source not in SOURCE_CODES:
        raise ValueError(f'Unknown source: {source}, \
                         must be one of {list(SOURCE_CODES.keys())}')
    data = f'{SOURCE_CODES[source]}:{data}'
    image = qrcode.make(
        data,
        image_factory=qrcode.image.svg.SvgPathImage,
    )
    return image


def file_to_data_uri(path: pathlib.Path) -> str:
    mime_type, _ = mimetypes.guess_type(path)

    if mime_type is None:
        mime_type = "application/octet-stream"

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")

    return f"data:{mime_type};base64,{encoded}"


def image_to_data_uri(image: qrcode.image.svg.SvgPathImage) -> str:
    buffer = io.BytesIO()
    image.save(buffer)

    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def svg_to_markup(qr_svg) -> Markup:
    if isinstance(qr_svg, bytes):
        qr_svg = qr_svg.decode("utf-8")

    return Markup(qr_svg)


def populate_qr_code_template(video: Video, output_path: pathlib.Path) -> pathlib.Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    qr_code = generate_qr_code(video.video_id, video.source.value)

    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=True,
    )
    template = env.get_template('video_qr.html.j2')
    html = template.render(
        title=video.title,
        thumbnail=file_to_data_uri(video.thumbnail_path),
        svg_url=image_to_data_uri(qr_code),
    )

    with open(output_path, 'w') as f:
        f.write(html)
    return output_path
