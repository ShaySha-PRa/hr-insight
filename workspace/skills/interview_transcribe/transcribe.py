#!/usr/bin/env python3
"""Transcribe interview audio. Default: Feishu ASR. Optional: Whisper-compatible API."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

FEISHU_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
FEISHU_FILE_URL = "https://open.feishu.cn/open-apis/speech_to_text/v1/speech/file_recognize"
FEISHU_STREAM_URL = "https://open.feishu.cn/open-apis/speech_to_text/v1/speech/stream_recognize"
# 16 kHz s16le mono: 200ms per packet
STREAM_CHUNK_BYTES = 6400
FILE_RECOGNIZE_MAX_SECONDS = 55.0
WHISPER_FORMATS = {
    ".flac",
    ".m4a",
    ".mp3",
    ".mp4",
    ".mpeg",
    ".mpga",
    ".oga",
    ".ogg",
    ".wav",
    ".webm",
}


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def probe_duration_seconds(path: Path) -> float | None:
    try:
        out = run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "csv=p=0",
                str(path),
            ]
        )
        return float(out.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return None


def format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "unknown"
    return f"{seconds:.1f}s"


def to_pcm_16k(path: Path) -> Path:
    pcm = path.with_suffix(".pcm")
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(path),
            "-f",
            "s16le",
            "-acodec",
            "pcm_s16le",
            "-ac",
            "1",
            "-ar",
            "16000",
            str(pcm),
        ]
    )
    return pcm


def ensure_whisper_format(path: Path) -> Path:
    if path.suffix.lower() in WHISPER_FORMATS:
        return path
    converted = path.with_suffix(".wav")
    run(["ffmpeg", "-y", "-i", str(path), "-ac", "1", "-ar", "16000", str(converted)])
    return converted


def http_json(url: str, payload: dict, headers: dict[str, str] | None = None, timeout: int = 60) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req_headers = {"Content-Type": "application/json; charset=utf-8"}
    if headers:
        req_headers.update(headers)
    last_detail = ""
    for attempt in range(4):
        req = urllib.request.Request(url, data=body, headers=req_headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            last_detail = f"HTTP {exc.code} from {url}: {detail[:800]}"
            reset = exc.headers.get("x-ogw-ratelimit-reset")
            limited = exc.code in (400, 429) and "99991400" in detail
            if limited and attempt < 3:
                wait_s = int(reset) if reset and reset.isdigit() else 20 * (attempt + 1)
                time.sleep(min(wait_s, 90))
                continue
            raise SystemExit(last_detail) from exc
    raise SystemExit(last_detail)


def feishu_token(app_id: str, app_secret: str) -> str:
    data = http_json(FEISHU_TOKEN_URL, {"app_id": app_id, "app_secret": app_secret})
    if data.get("code") not in (0, None) or not data.get("tenant_access_token"):
        raise SystemExit(f"Feishu token failed: {data.get('msg') or data}")
    return data["tenant_access_token"]


def feishu_id() -> str:
    return secrets.token_hex(8)


def feishu_file_recognize(pcm: bytes, token: str) -> str:
    data = http_json(
        FEISHU_FILE_URL,
        {
            "speech": {"speech": base64.b64encode(pcm).decode("ascii")},
            "config": {
                "file_id": feishu_id(),
                "format": "pcm",
                "engine_type": "16k_auto",
            },
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    if data.get("code") != 0:
        raise SystemExit(f"Feishu file recognize failed: {data.get('msg') or data}")
    text = (data.get("data") or {}).get("recognition_text") or ""
    if not text.strip():
        raise SystemExit("Feishu file recognize returned empty text")
    return text.strip()


def feishu_stream_recognize(pcm: bytes, token: str) -> str:
    stream_id = feishu_id()
    chunks = [pcm[i : i + STREAM_CHUNK_BYTES] for i in range(0, len(pcm), STREAM_CHUNK_BYTES)]
    if not chunks:
        raise SystemExit("audio converted to empty PCM")

    last_text = ""
    packets: list[tuple[int, bytes]] = []
    if len(chunks) == 1:
        packets.append((1, chunks[0]))
        packets.append((2, b""))
    else:
        packets.append((1, chunks[0]))
        for chunk in chunks[1:-1]:
            packets.append((0, chunk))
        packets.append((2, chunks[-1]))

    for sequence_id, (action, chunk) in enumerate(packets):
        data = http_json(
            FEISHU_STREAM_URL,
            {
                "speech": {"speech": base64.b64encode(chunk).decode("ascii") if chunk else ""},
                "config": {
                    "stream_id": stream_id,
                    "sequence_id": sequence_id,
                    "action": action,
                    "format": "pcm",
                    "engine_type": "16k_auto",
                },
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        if data.get("code") != 0:
            raise SystemExit(f"Feishu stream recognize failed: {data.get('msg') or data}")
        text = (data.get("data") or {}).get("recognition_text") or ""
        if text.strip():
            last_text = text.strip()

    if not last_text:
        raise SystemExit("Feishu stream recognize returned empty text")
    return last_text


def transcribe_feishu(source: Path, duration: float | None) -> tuple[str, str]:
    app_id = os.environ.get("FEISHU_APP_ID", "").strip()
    app_secret = os.environ.get("FEISHU_APP_SECRET", "").strip()
    if not app_id or not app_secret:
        raise SystemExit("FEISHU_APP_ID and FEISHU_APP_SECRET are required for Feishu transcription")
    token = feishu_token(app_id, app_secret)
    pcm_path = to_pcm_16k(source)
    try:
        pcm = pcm_path.read_bytes()
    finally:
        pcm_path.unlink(missing_ok=True)
    if duration is not None and duration <= FILE_RECOGNIZE_MAX_SECONDS:
        return feishu_file_recognize(pcm, token), "feishu-file"
    return feishu_stream_recognize(pcm, token), "feishu-stream"


def transcribe_whisper(source: Path, language: str, model: str) -> str:
    api_key = os.environ.get("WHISPER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Set WHISPER_API_KEY (or OPENAI_API_KEY) for the Whisper backend")
    base_url = os.environ.get("WHISPER_BASE_URL") or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1"
    upload = ensure_whisper_format(source)
    url = base_url.rstrip("/") + "/audio/transcriptions"
    cmd = [
        "curl",
        "-sS",
        "-X",
        "POST",
        url,
        "-H",
        f"Authorization: Bearer {api_key}",
        "-F",
        f"file=@{upload}",
        "-F",
        f"model={model}",
    ]
    if language:
        cmd.extend(["-F", f"language={language}"])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or "Whisper request failed")
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"unexpected Whisper response: {result.stdout[:500]}") from exc
    if isinstance(data, dict) and data.get("error"):
        raise SystemExit(str(data["error"]))
    text = data.get("text") if isinstance(data, dict) else None
    if not text:
        raise SystemExit("Whisper response had no text")
    return text.strip()


def write_markdown(output: Path, source: Path, duration: str, language: str, backend: str, text: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    body = (
        "---\n"
        f"source_audio: {source.name}\n"
        f"duration: {duration}\n"
        f"language: {language or 'auto'}\n"
        f"backend: {backend}\n"
        f"timestamp_utc: {utc_now_iso()}\n"
        "---\n\n"
        f"{text}\n"
    )
    output.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcribe interview audio to Markdown")
    parser.add_argument("--input", required=True, help="Audio file path")
    parser.add_argument("--output", required=True, help="Markdown output path")
    parser.add_argument("--language", default="zh", help="Language hint (Whisper backend)")
    parser.add_argument("--model", default="whisper-1")
    parser.add_argument(
        "--backend",
        choices=("auto", "feishu", "whisper"),
        default="auto",
        help="auto uses Feishu when app credentials exist, otherwise Whisper",
    )
    args = parser.parse_args()

    source = Path(args.input).expanduser().resolve()
    if not source.is_file():
        print(f"audio file not found: {source}", file=sys.stderr)
        return 1

    duration = probe_duration_seconds(source)
    backend = args.backend
    if backend == "auto":
        if os.environ.get("FEISHU_APP_ID") and os.environ.get("FEISHU_APP_SECRET"):
            backend = "feishu"
        elif os.environ.get("WHISPER_API_KEY") or os.environ.get("OPENAI_API_KEY"):
            backend = "whisper"
        else:
            print(
                "No transcription backend configured. "
                "Feishu app credentials are already enough; enable speech_to_text:speech on the app. "
                "Or set WHISPER_API_KEY.",
                file=sys.stderr,
            )
            return 2

    if backend == "feishu":
        text, method = transcribe_feishu(source, duration)
    else:
        text, method = transcribe_whisper(source, args.language, args.model), "whisper"

    write_markdown(Path(args.output), source, format_duration(duration), args.language, method, text)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
