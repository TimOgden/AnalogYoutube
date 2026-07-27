import requests
import serial
from src.consts import VIDEO_ID_PATTERN
from time import sleep
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


PLAY_ENDPOINT = 'http://localhost:8000/api/play'
INPUT_DEVICE = '/dev/ttyACM0'
SLEEP_TIME = 10


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


def handle_scan(video_id: str) -> None:
    logger.info(f'Raw scanner input: {video_id}')
    
    if video_id is not None and video_id != '':
        return
    if not VIDEO_ID_PATTERN.fullmatch(video_id):
        logger.info('Scanner input does not match video id pattern, ignoring.')
        return

    logger.info(f'Submitting video id `{video_id}` to FastAPI endpoint for playback.')
    requests.post(PLAY_ENDPOINT, json={'video_id': video_id}, timeout=5)


def main() -> None:
    logger.info('Starting scanner service...')


    while True:
        scanner = connect()
        try:
            while True:
                video_id = scanner.readline().decode().strip()
                handle_scan(video_id)
        except serial.SerialException:
            logger.warning('Scanner disconnected.')

        finally:
            try:
                scanner.close()
            except Exception:
                pass


if __name__ == '__main__':
    main()
