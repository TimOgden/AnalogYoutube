```bash
sudo mkdir -p /opt/analog-youtube
sudo chown "$(whoami)":"$(id -gn)" /opt/analog-youtube

git clone https://github.com/TimOgden/analog-youtube.git /opt/analog-youtube

cd /opt/analog-youtube

./deploy/install.sh
```