import os
import pathlib
import re
from dotenv import load_dotenv


load_dotenv(override=True)


VIDEO_ID_PATTERN = re.compile(r"^(YT|LC|LB):([A-Za-z0-9_-]*)$")
MEDIA_PATH = 'media/'
