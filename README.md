```bash
# sudo apt update
sudo apt install -y git tmux

sudo mkdir -p /opt/analog-youtube
sudo chown "$USER":"$(id -gn)" /opt/analog-youtube

git clone https://github.com/TimOgden/analog-youtube.git /opt/analog-youtube
cd /opt/analog-youtube

tmux new -s analog-install

# once inside tmux session
./deploy/install.sh
```

```bash
# restarting Chromium (in case it dies)
./deploy/start-kiosk.sh
```