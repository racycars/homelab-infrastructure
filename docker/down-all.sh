#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STACKS_DIR="$ROOT_DIR/stacks"

STACKS=(
  "traefik:docker-compose.yml"
  "authentik:docker-compose.yml"
  "homepage:compose.yaml"
  "ark:docker-compose.yml"
  "arrs:docker-compose.yml"
  "dawarich:docker-compose.yml"
  "immich:docker-compose.yml"
  "karakeep:docker-compose.yml"
  "mealie:docker-compose.yml"
  "media:docker-compose.yml"
  "minecraft:docker-compose.yml"
  "nextcloud:docker-compose.yml"
  "paperless:docker-compose.yml"
  "romm:docker-compose.yml"
  "uptime:docker-compose.yml"
  "vaultwarden:docker-compose.yml"
  "yourspotify:docker-compose.yml"
)

for (( idx=${#STACKS[@]}-1 ; idx>=0 ; idx-- )); do
  item="${STACKS[$idx]}"
  stack="${item%%:*}"
  file="${item##*:}"
  dir="$STACKS_DIR/$stack"
  echo "==> DOWN $stack"
  (cd "$dir" && docker compose --project-name "$stack" -f "$file" down)
done
