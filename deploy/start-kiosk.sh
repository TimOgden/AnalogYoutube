#!/usr/bin/env bash

set -x

LOG_FILE="$HOME/analog-youtube-kiosk.log"

exec >>"$LOG_FILE" 2>&1

echo "Starting Analog YouTube kiosk at $(date)"

echo "Waiting for FastAPI..."

until curl \
    --silent \
    --fail \
    http://127.0.0.1:8000/player \
    >/dev/null
do
    sleep 2
done

echo "FastAPI available. Starting Chromium."

exec /usr/bin/chromium \
    --kiosk \
    --noerrdialogs \
    --disable-infobars \
    --no-first-run \
    --disable-session-crashed-bubble \
    --autoplay-policy=no-user-gesture-required \
    http://127.0.0.1:8000/player