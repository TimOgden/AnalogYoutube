#!/bin/bash

LOG="$HOME/analog-youtube-kiosk.log"
exec >>"$LOG" 2>&1
set -x

echo "DISPLAY=$DISPLAY"
echo "WAYLAND_DISPLAY=$WAYLAND_DISPLAY"
echo "XDG_SESSION_TYPE=$XDG_SESSION_TYPE"

while ! curl -sf http://127.0.0.1:8000/player >/dev/null; do
    echo "Waiting for FastAPI..."
    sleep 2
done

exec /usr/bin/chromium \
    --kiosk \
    --noerrdialogs \
    --disable-infobars \
    --no-first-run \
    --disable-session-crashed-bubble \
    --autoplay-policy=no-user-gesture-required \
    --password-store=basic \
    http://127.0.0.1:8000/player