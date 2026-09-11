import os
import pathlib
import re


VIDEO_ID_PATTERN = re.compile(r"^(YT|LC|LB):([A-Za-z0-9_-]*)$")
MEDIA_PATH = pathlib.Path(os.environ['media_path'])
