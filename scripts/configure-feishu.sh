#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Missing .env" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

if [[ -z "${FEISHU_APP_ID:-}" || -z "${FEISHU_APP_SECRET:-}" ]]; then
  echo "Set FEISHU_APP_ID and FEISHU_APP_SECRET in .env first." >&2
  echo "Create the bot at https://open.feishu.cn then rerun this script." >&2
  exit 2
fi

docker compose exec -T openclaw-gateway node dist/index.js config set channels.feishu.appId "$FEISHU_APP_ID"
docker compose exec -T openclaw-gateway node dist/index.js config set channels.feishu.appSecret "$FEISHU_APP_SECRET"
docker compose exec -T openclaw-gateway node dist/index.js config set channels.feishu.enabled true
docker compose exec -T openclaw-gateway node dist/index.js config set channels.feishu.connectionMode websocket
docker compose restart openclaw-gateway
echo "Feishu channel written. Gateway restarted."
