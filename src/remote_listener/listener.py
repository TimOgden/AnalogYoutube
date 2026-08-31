import logging
import os
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


def handle_key(key: str) -> None:
    command = COMMAND_MAP.get(key)

    if command is None:
        return

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
    logger.info("Connecting to remote at %s...", INPUT_DEVICE)

    device = InputDevice(INPUT_DEVICE)

    logger.info(
        'Remote connected: "%s"',
        device.name,
    )

    for event in device.read_loop():
        if event.type != ecodes.EV_KEY:
            continue

        key_event = categorize(event)

        # Only respond to the initial button press.
        # 0 = released
        # 1 = pressed
        # 2 = held / autorepeat
        if key_event.keystate != key_event.key_down:
            continue

        key = key_event.keycode

        # evdev can occasionally return multiple keycodes.
        if isinstance(key, list):
            for keycode in key:
                logger.info("Remote key pressed: %s", keycode)
                yield keycode
        else:
            logger.info("Remote key pressed: %s", key)
            yield key


def get_commands() -> Iterator[str]:
    if INPUT_DEVICE == 'stdin':
        return stdin_commands()
    else:
        return hid_commands()


def main() -> None:
    logger.info('Starting remote listener...')

    for command in get_commands():
        handle_key(command)


if __name__ == '__main__':
    main()
