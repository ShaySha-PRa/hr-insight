# Hiring workspace

All hiring files live in this workspace volume. Do not write to a host Desktop or home directory.

## Directories

```
candidates/{slug}/
  resume.pdf
  resume.md
  profile.md
  interviews/{round}.{m4a,mp3,wav}
  interviews/{round}.transcript.md
hiring/pipeline.md
comparisons/{role}-{date}.md
```

## Slug

- Lowercase ASCII, hyphens only (example: `sha-junshu`, `wang-lin`).
- Derive from the candidate name; use pinyin when the name is Chinese.
- Reuse the same slug when the same person sends a new file.

## `profile.md` fields

Write a short record with these headings. Leave a field as `unknown` when the resume does not state it.

- Name
- Role
- Years of experience
- Skills
- Expected salary
- Availability
- Stage (`inbox` | `screening` | `interview` | `offer` | `hold`)
- Risk notes (facts only)

## `hiring/pipeline.md`

One row per candidate. Update the row when new evidence arrives; do not delete history without a note.

## Inbound files

| Source | What to do |
| --- | --- |
| Feishu PDF | Save as `candidates/{slug}/resume.pdf`, then `pdf_resume_to_md` |
| Gmail PDF attachment | Same path; follow `gmail_resume_ingest` only after the operator connects their hiring inbox |
| Feishu or email audio (`m4a`, `mp3`, `wav`) | Save under `interviews/`, then `interview_transcribe` |

## Compare

When two or more candidates exist for the same role, or the user asks to compare, follow `skills/candidate_compare/SKILL.md`.
