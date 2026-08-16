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

## Optional channels

**Gmail resume intake** — optional. Connect the **hiring inbox** you want the bot to read, not a personal mailbox unless that is intentional.

1. Create a Maton key at https://maton.ai/settings and put it in `.env` as `MATON_API_KEY`.
2. `ctrl.maton.ai` is retired (it returns `{"detail":"Not Found"}`).
3. Install the skill, then generate a fresh authorize URL:

```bash
./scripts/install-gmail-skill.sh
./scripts/connect-gmail.sh
```

4. Open the printed `connect.maton.ai` link within about 30 minutes. If you see `Session token expired`, run `./scripts/connect-gmail.sh` again.
5. On the Google permission screen, grant **all Gmail access**. Unchecking mail scopes makes the connection look active but unread checks fail with `insufficient authentication scopes`.
6. In Feishu: ask to check unread mail for new resumes. Attachments land under `candidates/{slug}/` in the workspace volume, not on the host desktop.

To replace an inbox: `MATON_FORCE_RECONNECT=1 ./scripts/connect-gmail.sh` and authorize the new account.

**Interview transcription** — send an `m4a` / `mp3` / `wav` in Feishu. The default backend is Feishu speech-to-text (same app as the bot). Enable the `speech_to_text:speech` scope on that app, then create a new version and publish it. Optional override: `WHISPER_API_KEY` plus `WHISPER_BASE_URL`.

**Compare candidates** — after a second resume is in `candidates/`, ask Feishu to compare them. The report is written to `comparisons/`.

## Layout

- `workspace/` — agent identity, operating rules, and skills
- `scripts/` — one-shot setup against the running container
- `docker-compose.yml` — isolated gateway on loopback ports
