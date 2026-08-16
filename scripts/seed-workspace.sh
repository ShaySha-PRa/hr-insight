#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

CID="$(docker compose ps -q openclaw-gateway)"
if [[ -z "$CID" ]]; then
  echo "Gateway is not running. Start it with: docker compose up -d" >&2
  exit 1
fi

WS=/home/node/.openclaw/workspace

docker exec "$CID" mkdir -p "$WS/skills" "$WS/hiring" "$WS/candidates" "$WS/comparisons"

for f in AGENTS.md IDENTITY.md SOUL.md USER.md HIRING.md HEARTBEAT.md; do
  docker cp "$ROOT/workspace/$f" "$CID:$WS/$f"
done

if ! docker exec "$CID" test -s "$WS/hiring/pipeline.md"; then
  docker cp "$ROOT/workspace/hiring/pipeline.md" "$CID:$WS/hiring/pipeline.md"
fi

for skill in pdf_resume_to_md candidate_compare gmail_resume_ingest interview_transcribe; do
  docker exec "$CID" rm -rf "$WS/skills/$skill"
  docker cp "$ROOT/workspace/skills/$skill" "$CID:$WS/skills/$skill"
done

docker exec "$CID" chown -R node:node \
  "$WS/AGENTS.md" \
  "$WS/IDENTITY.md" \
  "$WS/SOUL.md" \
  "$WS/USER.md" \
  "$WS/HIRING.md" \
  "$WS/HEARTBEAT.md" \
  "$WS/hiring" \
  "$WS/candidates" \
  "$WS/comparisons" \
  "$WS/skills"

echo "Workspace files copied into the running gateway volume."
