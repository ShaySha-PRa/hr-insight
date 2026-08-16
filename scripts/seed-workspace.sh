#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

CID="$(docker compose ps -q openclaw-gateway)"
if [[ -z "$CID" ]]; then
  echo "Gateway is not running. Start it with: docker compose up -d" >&2
  exit 1
fi

docker cp "$ROOT/workspace/AGENTS.md" "$CID:/home/node/.openclaw/workspace/AGENTS.md"
docker cp "$ROOT/workspace/IDENTITY.md" "$CID:/home/node/.openclaw/workspace/IDENTITY.md"
docker cp "$ROOT/workspace/SOUL.md" "$CID:/home/node/.openclaw/workspace/SOUL.md"
docker cp "$ROOT/workspace/USER.md" "$CID:/home/node/.openclaw/workspace/USER.md"
docker exec "$CID" mkdir -p /home/node/.openclaw/workspace/skills
docker cp "$ROOT/workspace/skills/pdf_resume_to_md" "$CID:/home/node/.openclaw/workspace/skills/pdf_resume_to_md"
docker exec "$CID" chown -R node:node \
  /home/node/.openclaw/workspace/AGENTS.md \
  /home/node/.openclaw/workspace/IDENTITY.md \
  /home/node/.openclaw/workspace/SOUL.md \
  /home/node/.openclaw/workspace/USER.md \
  /home/node/.openclaw/workspace/skills

echo "Workspace files copied into the running gateway volume."
