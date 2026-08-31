#!/usr/bin/env bash

set -euo pipefail

cd /opt/analog-youtube

git fetch origin
git pull --ff-only

cp "$PROJECT_DIR/deploy/analog-youtube-kiosk.desktop" \
   "$HOME/.config/autostart/analog-youtube-kiosk.desktop"

chmod +x "$PROJECT_DIR/deploy/start-kiosk.sh"

docker compose build --pull
docker compose up -d --remove-orphans

docker image prune -f