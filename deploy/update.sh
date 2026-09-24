#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="/opt/analog-youtube"
REBOOT_AFTER_UPDATE=false

if [[ "${1:-}" == "--reboot" ]]; then
   REBOOT_AFTER_UPDATE=true
fi

cd "$PROJECT_DIR"

git fetch origin --tags

LATEST_TAG="$(git tag --sort=-version:refname | head -n 1)"
if [[ -z "$LATEST_TAG" ]]; then
   echo "No git tags found" >&2
   exit 1
fi

CURRENT_TAG="$(git describe --tags --exact-match HEAD 2>/dev/null || true)"
if [[ "$CURRENT_TAG" == "$LATEST_TAG" ]]; then
   echo "Already running latest tag: $LATEST_TAG"
   if [[ "$REBOOT_AFTER_UPDATE" == true ]]; then
      /usr/bin/systemctl reboot
   fi
   exit 0
fi

echo "Updating from ${CURRENT_TAG:-untagged} to $LATEST_TAG"
git checkout --force "$LATEST_TAG"

cp "$PROJECT_DIR/deploy/analog-youtube-kiosk.desktop" \
   "$HOME/.config/autostart/analog-youtube-kiosk.desktop"

chmod +x "$PROJECT_DIR/deploy/start-kiosk.sh"

docker compose build --pull
docker compose up -d --remove-orphans

docker image prune -f

if [[ "$REBOOT_AFTER_UPDATE" == true ]]; then
   /usr/bin/systemctl reboot
fi