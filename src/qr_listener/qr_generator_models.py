from dataclasses import dataclass
import pathlib


@dataclass
class CardData:
    title: str
    thumbnail_path: pathlib.Path
    video_id: str
    source: str