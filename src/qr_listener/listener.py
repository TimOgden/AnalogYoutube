import os
from typing import Iterator

import requests
import serial
import subprocess
from src.consts import VIDEO_ID_PATTERN
from time import sleep
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


PLAY_ENDPOINT = os.getenv(
    "PLAY_ENDPOINT",
    "http://web:8000/api/play",
)
INPUT_DEVICE = os.getenv(
    "INPUT_DEVICE",
    "/dev/ttyACM0",
)
SLEEP_TIME = 10


def serial_scans() -> Iterator[str]:
    """Yield scans from a USB serial scanner, reconnecting as needed."""

    while True:
        scanner: serial.Serial | None = None

        try:
            logger.info("Connecting to scanner at %s...", INPUT_DEVICE)

            scanner = serial.Serial(
                port=INPUT_DEVICE,
                baudrate=9600,
                timeout=None,
            )

            logger.info("Scanner connected.")

            while True:
                raw_scan = scanner.readline()
                yield raw_scan.decode("utf-8").strip()

        except (
            serial.SerialException,
            serial.SerialTimeoutException,
            OSError,
        ):
            logger.warning(
                "Scanner unavailable or disconnected; retrying in %s seconds...",
                SLEEP_TIME,
            )
            sleep(SLEEP_TIME)

        except UnicodeDecodeError:
            logger.warning("Scanner returned invalid UTF-8 input.")

        finally:
            if scanner is not None and scanner.is_open:
                scanner.close()


def stdin_scans() -> Iterator[str]:
    """Yield manually entered scans for local development."""

    logger.info("Mock scanner enabled.")
    logger.info("Enter a YouTube video ID and press Enter.")

    while True:
        try:
            yield input("scan> ").strip()
        except EOFError:
            logger.info("Mock scanner input closed.")
            return


def get_scans() -> Iterator[str]:
    if INPUT_DEVICE == "stdin":
        return stdin_scans()
    else:
        return serial_scans()


def connect() -> serial.Serial:
    while True:
        try:
            scanner = serial.Serial(INPUT_DEVICE, 9600)
            logger.info("Scanner connected.")
            return scanner
        except serial.SerialException:
            logger.info(
                "Cannot find %s, retrying in %s seconds...",
                INPUT_DEVICE,
                SLEEP_TIME,
            )
            sleep(SLEEP_TIME)


def activate_tv() -> None:
    """
    Wake the TV and ask it to switch to the Pi's HDMI input.

    CEC logical address 0 is normally the TV.
    """
    try:
        result = subprocess.run(
            ['cec-client', '-s', '-d', '1'],
            input="on 0\nas\n",
            text=True,
            capture_output=True,
            timeout=10,
            check=False
        )

        if result.returncode != 0:
            logger.warning(
                'HDMI-CEC command failed with exit code %s: %s',
                result.returncode,
                result.stderr.strip()
            )
            return
        logger.info('Sent TV wake and active-source commands.')
    except FileNotFoundError:
        logger.error('cenc-client is not installed in the scanner container.')
    except subprocess.TimeoutExpired:
        logger.warning('HDMI-CEC command timed out')
    except OSError:
        logger.exception('Could not execute HDMI-CEC command')


def handle_scan(video_id: str) -> None:
    logger.info("Raw scanner input: %r", video_id)

    if not video_id:
        logger.info("Scanner input is empty; ignoring.")
        return

    if not VIDEO_ID_PATTERN.fullmatch(video_id):
        logger.info(
            "Scanner input does not match the video ID pattern; ignoring."
        )
        return

    logger.info("Valid video ID scanned: %s", video_id)

    # Skip HDMI-CEC in local development
    if INPUT_DEVICE != 'stdin':
        activate_tv()
    submit_video(video_id)


def submit_video(video_id: str) -> None:
    logger.info(f'Raw scanner input: {video_id}')
    
    if not video_id:
        return
    if not VIDEO_ID_PATTERN.fullmatch(video_id):
        logger.info('Scanner input does not match video id pattern, ignoring.')
        return

    logger.info(f'Submitting video id `{video_id}` to FastAPI endpoint for playback.')
    try:
        response = requests.post(PLAY_ENDPOINT, json={'video_id': video_id, 'device_id': INPUT_DEVICE}, timeout=5)
        if not response.ok:
            logger.error(
                "Playback request failed: status=%s body=%s",
                response.status_code,
                response.text,
            )
        response.raise_for_status()
    except requests.RequestException:
        logger.exception('Failed to submit video id to %s.', PLAY_ENDPOINT)


def listen(scanner: serial.Serial) -> None:
    while True:
        raw_value = scanner.readline()
        video_id = raw_value.decode('utf-8').strip()
        handle_scan(video_id)


def main() -> None:
    logger.info('Starting scanner service...')

    for video_id in get_scans():
        handle_scan(video_id)


if __name__ == '__main__':
    main()
