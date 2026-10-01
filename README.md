An end-to-end open-source Raspberry Pi project that lets kids watch parent-selected videos by scanning physical QR cards without the algorithmic recommendations or endless scrolling.

Supports youtube videos played directly from youtube, custom video uploads, and a curatable list of vintage cartoons from archive.org

Inspired by [this instagram video](https://www.instagram.com/p/DUZAitUDxT3/), I wanted a way for parents to set this up for their kids without the required setup of a home media server

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
