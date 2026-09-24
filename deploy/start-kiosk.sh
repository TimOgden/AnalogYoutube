#!/bin/bash

LOG="$HOME/analog-youtube-kiosk.log"

exec >>"$LOG" 2>&1
set -x

echo "Starting Analog YouTube kiosk"
echo "DISPLAY=$DISPLAY"
echo "WAYLAND_DISPLAY=$WAYLAND_DISPLAY"
echo "XDG_SESSION_TYPE=$XDG_SESSION_TYPE"
echo "XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR"

# Wait for the graphical session
while [[ -z "$WAYLAND_DISPLAY" ]] || \
      [[ ! -S "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" ]]; do
    echo "Waiting for Wayland..."
    sleep 2
done

echo "Wayland available."

# Wait for FastAPI
while ! curl -sf http://127.0.0.1:8000/player >/dev/null; do
    echo "Waiting for FastAPI..."
    sleep 2
done

echo "FastAPI available."

# Small grace period after everything claims to be ready
sleep 2

echo "Starting Chromium."

exec /usr/bin/chromium \
    --ozone-platform=wayland \
    --kiosk \
    --noerrdialogs \
    --disable-infobars \
    --no-first-run \
    --disable-session-crashed-bubble \
    --autoplay-policy=no-user-gesture-required \
    --password-store=basic \
    http://127.0.0.1:8000/player