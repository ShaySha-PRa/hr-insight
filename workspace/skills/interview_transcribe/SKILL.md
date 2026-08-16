---
name: interview-transcribe
description: Transcribe an interview recording already saved under candidates/{slug}/interviews/. Default backend is Feishu speech-to-text. Optional Whisper-compatible API. Linux/ffmpeg only.
---

# Interview transcribe

Use this when an interview recording arrives over Feishu or email.

This gateway runs on Linux. Do not use Apple Notes, AppleScript, or host Desktop paths.

## Save first

```
candidates/{slug}/interviews/{round}.m4a
```

Accepted input: `m4a`, `mp3`, `wav`, and other common audio containers. `ffmpeg` converts to 16 kHz mono PCM for Feishu.

## Run

```bash
python3 skills/interview_transcribe/transcribe.py \
  --input candidates/{slug}/interviews/{round}.m4a \
  --output candidates/{slug}/interviews/{round}.transcript.md \
  --language zh
```

Default backend is **Feishu ASR** using `FEISHU_APP_ID` / `FEISHU_APP_SECRET` already in the container.

- Clips up to ~55s use file recognize
- Longer recordings use stream recognize
- The Feishu app needs the `speech_to_text:speech` scope (语音识别)

Optional: `--backend whisper` with `WHISPER_API_KEY` and optional `WHISPER_BASE_URL`.

## Afterward

- Treat the transcript as an input, not a verdict.
- Write the interview summary with three labeled sections: facts, interviewer statements, analysis.
- Update `candidates/{slug}/profile.md` and `hiring/pipeline.md` when the transcript adds new facts.

## If transcription fails

Still save the audio file. Tell the user whether the Feishu app is missing `speech_to_text:speech`, or the tenant plan does not include ASR. Do not invent a transcript.
