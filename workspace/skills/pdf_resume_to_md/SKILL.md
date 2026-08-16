---
name: pdf-resume-to-md
description: Convert a resume PDF (by filename) into a Markdown file with the same name using a local Python extractor. Supports deterministic output and extraction reports.
---

# **PDF Resume → Markdown**

Convert a specific resume PDF into Markdown by invoking a local Python script.

The PDF is identified **by filename**, resolved from a predefined resume directory, and saved as a .md file with the same base name.

Offline-only. No network access.

## Setup

1. **Install dependencies:**
   ```bash
   pip3 install pypdf
   ```
   
   Or use the provided requirements.txt:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Optional (better PDF metadata):** install poppler-utils / pdftotext

## Input Convention

Store each resume under the workspace candidate folder (see `HIRING.md`):

- Input: `candidates/{slug}/resume.pdf`
- Output: `candidates/{slug}/resume.md`

## Convert Resume (Single PDF)

```bash
python3 skills/pdf_resume_to_md/pdf_to_md.py \
  --input candidates/{slug}/resume.pdf \
  --output candidates/{slug}/resume.md
```

## Batch Conversion (Optional)

```bash
python3 skills/pdf_resume_to_md/pdf_to_md.py \
  --input candidates \
  --output candidates \
  --recursive
```

## Output Format

Each PDF produces exactly one Markdown file with the following structure:

- YAML frontmatter:
  - `source_pdf`
  - `pages`
  - `extracted_chars`
  - `extraction_method`
  - `timestamp_utc`
- Resume text body
- Page markers: `<!-- page:N -->`
- Extraction report (warnings, density, method)

## Limitations

- No OCR.
- Image-only or scanned PDFs may yield empty text.
- A Markdown file is still produced with warnings.

## Safety Notes

- Operates only on local files.
- No directory scanning beyond the resume root.
- No network access.
- No arbitrary shell execution.

## Notes

- Validate the PDF filename exists before execution.
- Warn before overwriting an existing .md file.
- Do not assume text completeness for scanned resumes.
