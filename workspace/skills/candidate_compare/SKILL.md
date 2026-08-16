---
name: candidate-compare
description: Compare two or more candidates already stored under candidates/ and write a dated report under comparisons/.
---

# Candidate compare

Use this when a second resume arrives, or when the user asks who fits a hiring goal better.

Read each `candidates/{slug}/profile.md` and `resume.md`. If a profile is missing, build it from the resume first. Refresh `hiring/pipeline.md`.

## Do not

- Write the recommendation into `MEMORY.md`
- Invent facts that are not in the files
- Treat the recommendation as a final hiring decision

## Reply in chat

Use this table (Feishu supports markdown tables):

| Dimension | {Candidate A} | {Candidate B} |
| --- | --- | --- |
| Company background | | |
| Team size | | |
| Experience | | |
| Expected salary | | |
| Strengths | | |
| Availability | | |

Then a short recommendation block:

- **Recommendation:** name, with the hiring goal restated
- **Why:** 2–4 bullets tied to the table
- **Gaps:** what is still unknown

If the user stated a goal (speed, cost, startup fit, large-team process), score each row against that goal. If they did not, say so and give a conditional recommendation.

## Persist

Write the same table and recommendation to:

`comparisons/{role}-{YYYY-MM-DD}.md`

`{role}` is a lowercase hyphenated job family (`hrbp`, `backend`). Use today's date in `Asia/Shanghai`.
