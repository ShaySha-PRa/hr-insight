# HR-Insight

Self-hosted hiring assistant. It lives in Feishu, turns inbound resumes into structured candidate records, and keeps notes consistent across a hiring cycle.

The gateway runs in Docker with named volumes only. Host home directories are not mounted.

## Run

```bash
cp .env.example .env
# fill gateway token, Feishu app credentials, and MiniMax key
docker compose up -d --build
./scripts/seed-workspace.sh
./scripts/configure-feishu.sh
```

Control UI: `http://127.0.0.1:18789/`

## Layout

- `workspace/` — agent identity, operating rules, and skills
- `scripts/` — one-shot setup against the running container
- `docker-compose.yml` — isolated gateway on loopback ports
