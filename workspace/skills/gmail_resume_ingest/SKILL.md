---
name: gmail-resume-ingest
description: Check Gmail for unread messages with resume attachments, save them under candidates/{slug}/, convert to Markdown, and update hiring/pipeline.md.
---

# Gmail resume ingest

Requires `MATON_API_KEY` and an ACTIVE Gmail connection for the **operator's hiring inbox**. Each operator authorizes their own mailbox. Do not ask the current user to connect a personal Gmail if they declined.

Authorize with `scripts/connect-gmail.sh` and open the returned `connect.maton.ai` URL within 30 minutes. Do not use `ctrl.maton.ai` (404). The `gmail` skill must be installed in this workspace.

This gateway runs on Linux. Do not use Desktop folders or macOS tools.

## When to use

- The user asks to check email for new resumes
- A heartbeat finds unread mail with a PDF attachment

## Steps

1. List unread messages via the Gmail skill / Maton gateway.
2. For each message with a PDF (or `.doc`/`.docx` if you can convert):
   - Derive `{slug}` from the candidate name in the subject, filename, or body (`HIRING.md`).
   - Download the attachment to `candidates/{slug}/resume.pdf`.
   - Run `pdf_resume_to_md`.
   - Write or update `candidates/{slug}/profile.md`.
   - Add or refresh the row in `hiring/pipeline.md` with stage `inbox`.
3. Reply with a structured summary per new candidate. If a second candidate already exists, offer or run `candidate_compare`.
4. Do not mark mail read or send replies unless the user asks.

## Send mail

Interview notices and other outbound mail need an explicit ask first (`AGENTS.md`). After sending, record the message id in the candidate folder and in `hiring/pipeline.md`.

## If Gmail is not configured

Say that Gmail is not connected yet. Point the operator at `README.md` (Gmail resume intake): their own Maton key, `./scripts/connect-gmail.sh`, and granting all Gmail scopes. Do not invent inbox contents. Do not ask them to authorize a personal mailbox if they said not to.
