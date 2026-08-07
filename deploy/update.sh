#!/usr/bin/env bash

set -euo pipefail

cd /opt/analog-youtube

git fetch origin
git pull --ff-only

docker compose build --pull
docker compose up -d --remove-orphans

docker image prune -f