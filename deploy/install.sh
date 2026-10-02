#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="/opt/analog-youtube"
SERVICE_FILE="$PROJECT_DIR/deploy/analog-youtube.service"
AUTOSTART_FILE="$PROJECT_DIR/deploy/analog-youtube-kiosk.desktop"
UPDATE_SERVICE_FILE="$PROJECT_DIR/deploy/analog-youtube-update.service"
UPDATE_PATH_FILE="$PROJECT_DIR/deploy/analog-youtube-update.path"
CMDLINE_FILE="/boot/firmware/cmdline.txt"

if [[ $EUID -eq 0 ]]; then
    echo "Run this script as the regular Pi user, not root."
    exit 1
fi

CONFIG_FILE="/boot/firmware/config.txt"

echo "Configuring HDMI-only audio..."

if grep -qE '^[[:space:]]*dtparam=audio=' "$CONFIG_FILE"; then
    sudo sed -i \
        's/^[[:space:]]*dtparam=audio=.*/dtparam=audio=off/' \
        "$CONFIG_FILE"
else
    echo 'dtparam=audio=off' | sudo tee -a "$CONFIG_FILE" > /dev/null
fi

echo "Installing h264ify Chromium extension..."

CHROMIUM_POLICY_DIR="/etc/chromium/policies/managed"
CHROMIUM_POLICY_FILE="$CHROMIUM_POLICY_DIR/analog-youtube.json"

sudo mkdir -p "$CHROMIUM_POLICY_DIR"

sudo tee "$CHROMIUM_POLICY_FILE" > /dev/null <<'EOF'
{
  "ExtensionInstallForcelist": [
    "aleakchihdccplidncghkekgioiakgal;https://clients2.google.com/service/update2/crx"
  ]
}
EOF

sudo chmod 644 "$CHROMIUM_POLICY_FILE"

echo "Installing system packages..."

sudo apt-get update
sudo apt-get install -y \
    git \
    chromium \
    cec-utils \
    curl \
    ca-certificates \
    python3


echo "Installing Docker..."

# Add Docker's official GPG key
sudo apt-get update
sudo apt-get install -y ca-certificates curl

sudo install -m 0755 -d /etc/apt/keyrings

sudo curl -fsSL \
    https://download.docker.com/linux/debian/gpg \
    -o /etc/apt/keyrings/docker.asc

sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker's Debian repository
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt-get update

sudo apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

echo "Docker installed."

sudo usermod -aG docker "$USER"

CONNECTED_HDMI=""

for connector in /sys/class/drm/card*-HDMI-A-*; do
    if [[ "$(cat "$connector/status")" == "connected" ]]; then
        CONNECTED_HDMI="$(basename "$connector")"
        break
    fi
done

if [[ -z "$CONNECTED_HDMI" ]]; then
    echo "No connected HDMI display found." >&2
    exit 1
fi

# card1-HDMI-A-1 -> HDMI-A-1
DISPLAY_CONNECTOR="${CONNECTED_HDMI#*-}"

echo "Detected display: $DISPLAY_CONNECTOR"

DISPLAY_CONFIG="$PROJECT_DIR/deploy/display_config.env"
DISPLAY_CONFIG_TEMPLATE="$PROJECT_DIR/deploy/display_config.env.template"

if [[ ! -f "$DISPLAY_CONFIG" ]]; then
    echo "No display configuration found. Creating from template..."
    cp "$DISPLAY_CONFIG_TEMPLATE" "$DISPLAY_CONFIG"
fi

source "$DISPLAY_CONFIG"
DISPLAY_MODE="${DISPLAY_CONNECTOR}:${DISPLAY_RESOLUTION}@${DISPLAY_REFRESH_RATE}D"
echo "Setting to display mode: $DISPLAY_MODE..."


echo "Configuring display resolution..."

sudo python3 - "$CMDLINE_FILE" "$DISPLAY_MODE" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
display_mode = sys.argv[2]

cmdline = path.read_text().strip()

args = [
    arg
    for arg in cmdline.split()
    if not arg.startswith("video=")
]

args.append(f"video={display_mode}")

path.write_text(" ".join(args) + "\n")
PY

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
sudo docker compose build

echo "Starting application..."

sudo systemctl start analog-youtube.service

echo
echo "Installation complete."
echo "Rebooting the Pi so Docker permissions and kiosk autostart take effect."
sudo reboot