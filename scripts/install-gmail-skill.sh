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

if [[ -z "${MATON_API_KEY:-}" ]]; then
  echo "Set MATON_API_KEY in .env first." >&2
  echo "Create a key at https://maton.ai/settings and connect Gmail at https://ctrl.maton.ai" >&2
  exit 2
fi

CID="$(docker compose ps -q openclaw-gateway)"
if [[ -z "$CID" ]]; then
  echo "Gateway is not running. Start it with: docker compose up -d" >&2
  exit 1
fi

echo "Installing the gmail skill into the gateway workspace volume..."
if docker compose exec -T -e MATON_API_KEY="$MATON_API_KEY" openclaw-gateway \
  node dist/index.js skills install @byungkyu/gmail; then
  echo "gmail skill installed via openclaw skills."
else
  echo "openclaw skills install failed; trying clawhub..."
  docker compose exec -T -e MATON_API_KEY="$MATON_API_KEY" openclaw-gateway \
    bash -lc 'cd /home/node/.openclaw/workspace && npx --yes clawhub@latest install @byungkyu/gmail'
fi

docker compose exec -T openclaw-gateway \
  chown -R node:node /home/node/.openclaw/workspace/skills/gmail || true

echo "Gmail skill is in the workspace volume. Restart the gateway so it picks up MATON_API_KEY."
docker compose restart openclaw-gateway
echo "Done. Authorize Gmail with ./scripts/connect-gmail.sh or at https://maton.ai → Connections."
