#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STACKS_DIR="$ROOT_DIR/stacks"

wait_running() {
  local stack="$1"; local file="$2"; local tries=30
  for i in $(seq 1 "$tries"); do
    # if any container in the project is 'running', proceed
    if (cd "$STACKS_DIR/$stack" && docker compose --project-name "$stack" -f "$file" ps --status running >/dev/null 2>&1); then
      return 0
    fi
    sleep 2
  done
  echo "WARN: $stack did not report running containers after 60s" >&2
}

STACKS=(
  "traefik:docker-compose.yml"
  "authentik:docker-compose.yml"
  "homepage:docker-compose.yml"
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

for item in "${STACKS[@]}"; do
  stack="${item%%:*}"
  file="${item##*:}"
  dir="$STACKS_DIR/$stack"
  echo "==> UP $stack"
  (cd "$dir" && docker compose --project-name "$stack" -f "$file" up -d)
  # Ensure core infra is up before starting dependents
  if [[ "$stack" == "traefik" || "$stack" == "authentik" ]]; then
    wait_running "$stack" "$file" || true
  fi
done
