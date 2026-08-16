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
  exit 2
fi

python3 - <<'PY'
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

key = os.environ["MATON_API_KEY"]
base = "https://api.maton.ai"


def request(method: str, path: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        base + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"Maton API HTTP {exc.code}: {detail[:400]}", file=sys.stderr)
        raise SystemExit(1) from exc
    return json.loads(raw) if raw else {}


def items(payload: dict) -> list:
    if isinstance(payload, list):
        return payload
    for name in ("connections", "items", "data"):
        value = payload.get(name)
        if isinstance(value, list):
            return value
    if "connection" in payload:
        return [payload["connection"]]
    return []


listed = request("GET", "/connections?app=google-mail")
rows = items(listed)
print(f"existing google-mail connections: {len(rows)}")
for row in rows:
    status = row.get("status") or "unknown"
    conn_id = row.get("connection_id") or row.get("id") or "?"
    email = (row.get("metadata") or {}).get("email") or "-"
    print(f"  {conn_id}  status={status}  email={email}")
    if status == "ACTIVE" and os.environ.get("MATON_FORCE_RECONNECT") != "1":
        print("Gmail is already authorized. Ask in Feishu to check unread resumes.")
        raise SystemExit(0)
    if status == "ACTIVE" and os.environ.get("MATON_FORCE_RECONNECT") == "1" and conn_id != "?":
        request("DELETE", f"/connections/{urllib.parse.quote(str(conn_id))}")
        print(f"  deleted insufficient-scope connection {conn_id}")
    if status == "PENDING" and conn_id != "?":
        request("DELETE", f"/connections/{urllib.parse.quote(str(conn_id))}")
        print(f"  deleted expired pending connection {conn_id}")

created = request("POST", "/connections", {"app": "google-mail"})
conn = created.get("connection") or created
conn_id = conn.get("connection_id") or conn.get("id")
if conn_id and not conn.get("url"):
    viewed = request("GET", f"/connections/{urllib.parse.quote(str(conn_id))}")
    conn = viewed.get("connection") or viewed
url = conn.get("url")
if not url:
    print("Maton created a connection but did not return an authorize URL.", file=sys.stderr)
    print("Use https://maton.ai → Connections → New → Gmail instead.", file=sys.stderr)
    raise SystemExit(1)
print(url)
print("Open that URL in a browser (valid about 30 minutes), sign in to Gmail, then come back.")
PY
