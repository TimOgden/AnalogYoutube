#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="/opt/analog-youtube"
SERVICE_FILE="$PROJECT_DIR/deploy/analog-youtube.service"
AUTOSTART_FILE="$PROJECT_DIR/deploy/analog-youtube-kiosk.desktop"
UPDATE_SERVICE_FILE="$PROJECT_DIR/deploy/analog-youtube-update.service"
UPDATE_PATH_FILE="$PROJECT_DIR/deploy/analog-youtube-update.path"

if [[ $EUID -eq 0 ]]; then
    echo "Run this script as the regular Pi user, not root."
    exit 1
fi

echo "Installing system packages..."

sudo apt-get update
sudo apt-get install -y \
    git \
    chromium \
    cec-utils \
    curl \
    ca-certificates

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is not installed."
    echo "Install Docker Engine from Docker's Debian repository first."
    exit 1
fi

sudo usermod -aG docker "$USER"

echo "Creating application directories..."

mkdir -p \
    "$PROJECT_DIR/runtime" \
    "$PROJECT_DIR/media/videos" \
    "$PROJECT_DIR/media/thumbnails"

echo "Installing Docker service..."

sudo cp "$SERVICE_FILE" \
    /etc/systemd/system/analog-youtube.service

echo "Installing update service..."

sudo cp "$UPDATE_SERVICE_FILE" \
    /etc/systemd/system/analog-youtube-update.service

sudo cp "$UPDATE_PATH_FILE" \
    /etc/systemd/system/analog-youtube-update.path

sudo systemctl daemon-reload

sudo systemctl enable analog-youtube.service
sudo systemctl enable analog-youtube-update.path

echo "Installing Chromium autostart..."

chmod +x "$PROJECT_DIR/deploy/start-kiosk.sh"

mkdir -p "$HOME/.config/autostart"
cp "$AUTOSTART_FILE" \
    "$HOME/.config/autostart/analog-youtube-kiosk.desktop"

echo "Building application containers..."

cd "$PROJECT_DIR"
docker compose build

echo "Starting application..."

sudo systemctl start analog-youtube.service

echo
echo "Installation complete."
echo "Reboot the Pi so Docker permissions and kiosk autostart take effect."