import logging
import os
from time import sleep
from typing import Iterator
from evdev import InputDevice, categorize, ecodes

import requests

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

INPUT_DEVICE = os.getenv(
    "INPUT_DEVICE",
    "/dev/input/event0"
)
COMMANDS_ENDPOINT = os.getenv(
    "COMMANDS_ENDPOINT",
    "http://web:8000/api/control",
)

COMMAND_MAP = {
    "KEY_PLAYPAUSE": "play_pause",
    "KEY_PLAY": "play",
    "KEY_PAUSE": "pause",
    "KEY_LEFT": "seek_backward",
    "KEY_RIGHT": "seek_forward",
    "KEY_ENTER": "play_pause",
}

SLEEP_TIME = 10


def handle_command(command: str) -> None:
    logger.info(f'Submitting command: "{command}" to FastAPI endpoint...')
    try:
        response = requests.post(
            COMMANDS_ENDPOINT,
            json={"command": command},
            timeout=5,
        )
        if not response.ok:
            logger.error(
                "Command failed: status=%s body=%s",
                response.status_code,
                response.text
            )
        response.raise_for_status()
    except requests.RequestException:
        logger.exception('Failed to send command to %s.', COMMANDS_ENDPOINT)


def stdin_commands() -> Iterator[str]:
    """Yield manually entered commands for local development."""

    logger.info("Mock remote enabled.")
    logger.info("Enter a command and press Enter.")

    while True:
        try:
            yield input("command> ").strip()
        except EOFError:
            logger.info("Mock remote input closed.")
            return

def hid_commands() -> Iterator[str]:

    while True:
        device: InputDevice | None = None

        try:
            logger.info("Connecting to remote at %s...", INPUT_DEVICE)

            device = InputDevice(INPUT_DEVICE)

            logger.info("Remote connected.")
            for event in device.read_loop():
                if event.type != ecodes.EV_KEY:
                    continue
        
                key_event = categorize(event)
                keys = key_event.keycode
        
                if not isinstance(keys, list):
                    keys = [keys]
        
                for keycode in keys:
                    if keycode == "KEY_RIGHT":
                        if key_event.keystate == key_event.key_hold:
                            yield "scrub_forward_start"
                        elif key_event.keystate == key_event.key_down:
                            yield "seek_forward"
                        elif key_event.keystate == key_event.key_up:
                            yield "scrub_stop"
                        continue
        
                    if keycode == "KEY_LEFT":
                        if key_event.keystate == key_event.key_hold:
                            yield "scrub_backward_start"
                        elif key_event.keystate == key_event.key_down:
                            yield "seek_backward"
                        elif key_event.keystate == key_event.key_up:
                            yield "scrub_stop"
                        continue
        
                    # Ordinary buttons only fire once on key-down
                    if key_event.keystate != key_event.key_down:
                        continue
        
                    command = COMMAND_MAP.get(keycode)
                    if command is None:
                        logger.info(f'Unhandled keycode: {keycode}')
                    yield command

        except (
            OSError,
        ) as e:
            logger.warning(
                "Remote unavailable or disconnected: %s. "
                "Retrying in %s seconds...",
                e,
                SLEEP_TIME,
            )
            sleep(SLEEP_TIME)


def get_commands() -> Iterator[str]:
    if INPUT_DEVICE == 'stdin':
        return stdin_commands()
    else:
        return hid_commands()


def main() -> None:
    logger.info('Starting remote listener...')

    for command in get_commands():
        handle_command(command)


if __name__ == '__main__':
    main()
