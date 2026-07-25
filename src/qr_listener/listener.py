import httpx
from evdev import InputDevice, categorize, ecodes
from src.consts import VIDEO_ID_PATTERN


SCANNER_DEVICE = (
    '/dev/input/by-id',
    'usb-SM_SCANNER_2020-event-kbd'  # TODO: update to correct scanner name
)
PLAY_ENDPOINT = 'http://localhost:8000/api/play'



async def main() -> None:
    scanner = InputDevice(SCANNER_DEVICE)

    # prevent scanner keystrokes from reaching any other window
    scanner.grab()

    buffer = ''

    try:
        async for event in scanner.async_read_loop():
            if event.type != ecodes.EV_KEY:
                continue

            key_event = categorize(event)
            if key_event.keystate != key_event.key_down:
                continue
            
            key = key_event.keycode
            if isinstance(key, list):
                key = key[0]
            
            if key == 'KEY_ENTER':
                match = VIDEO_ID_PATTERN.fullmatch(buffer)
                if match:
                    video_id = match.group(1)

                    async with httpx.AsyncClient() as client:
                        await client.post(
                            PLAY_ENDPOINT,
                            json={'video_id': video_id},
                            timeout=5,
                        )
                buffer = ''
                continue
            character = key_to_character(key)
            if character is not None:
                buffer += character
    finally:
        scanner.ungrab()


def key_to_character(key: str) -> str | None:
    if key.startswith('KEY_'):
        value = key.removeprefix('KEY_')

        if len(value) == 1:
            return value.lower()
        
        if value == 'MINUS':
            return '-'
    return None