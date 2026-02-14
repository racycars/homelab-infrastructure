#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Homelab backup helper script
#
# This script runs Autorestic to back up all defined locations in the
# configuration file `autorestic.yml`.  It assumes that Autorestic is
# installed and available on the host or in a container.  To use it with
# Docker, you can add a service similar to the example below to your
# `docker‑compose.yml`:
#
#   services:
#     autorestic:
#       image: crazymax/autorestic:latest
#       container_name: autorestic
#       volumes:
#         - ./autorestic.yml:/config/autorestic.yml:ro
#         - /docker/appdata:/docker/appdata:ro
#         - /srv/docker:/srv/docker:ro
#         - /backups/homelab:/backups/homelab
#       environment:
#         - TZ=${TZ}
#         - RESTIC_PASSWORD=${RESTIC_PASSWORD}
#       entrypoint: ["/bin/sh", "-c"]
#       command: ["autorestic", "--config", "/config/autorestic.yml", "backup", "all"]
#       profiles: ["backup"]
#
# You can then run the backup manually with:
#
#   docker compose --profile backup run --rm autorestic
#
# Or schedule it via cron on the host system to run at regular intervals.
#
# -----------------------------------------------------------------------------

set -euo pipefail

CONFIG_FILE="${CONFIG_FILE:-$(dirname "$0")/autorestic.yml}"

if ! command -v autorestic >/dev/null 2>&1; then
  echo "ERROR: autorestic binary not found.  Install autorestic or run this"
  echo "script inside the autorestic container (see header comments)."
  exit 1
fi

echo "Running Autorestic backup using config: $CONFIG_FILE"
autorestic --config "$CONFIG_FILE" backup all
