# Decisions

Newest first. One entry per change: what, replaces what, why.

## 2026-11-04 — Lesson code: explicit first, concise in a comment
- What: every idiom (comprehension, zip, unpacking, ternary, most_common...)
  is written the long way between `# --- explicit start ---` and
  `# --- explicit end ---`; a `# concise:` comment right after shows the
  short Python form.
- Scope: 2.1 and all future lessons. 1.1–1.4 stay as they are.
- Replaces: concise idioms with a short explaining comment.
- Why: user comes from Java; learn the long form, then the shortcut.
- Cost: files grow; 2.1 examples split into 2 files to stay under 150 lines.

## 2026-11-02 — One growing app + just-in-time Python
- What: one app `assistant/` grows v1→v10 through the phases.
  Python topics 1.5–1.9 move to right before first use.
- Replaces: 10 separate projects; "all Python first" order.
- Why: user learns best by building, "growing with learning".
- Hours unchanged (199). Topic IDs unchanged; order in PLAN.md.

## 2026-11-01 — Track hours + %, not weeks
- What: docs/PROGRESS.md tracks logged hours and milestone % per phase.
- Replaces: week-based timeline idea.
- Why: weekly hours vary too much.

## 2026-11-01 — Layout, env, pace decided
- Repo name stays `ai_engineering_lab`.
- Top-level numbered phase folders; replaces `labs/` (removed).
- uv + pyproject.toml + uv.lock; replaces requirements.txt.
- Pace: one main phase at a time, small overlaps (see PLAN.md "How we work").

## 2026-11-01 — Learning plan adopted, with review changes
- What: user's plan saved as docs/PLAN.md with 10 changes (evals, Java bridge,
  raw-first, hardware-aware models, guardrails, uv). Reasons: docs/PLAN_REVIEW.md.
- Open: repo name, folder layout, uv vs requirements.txt.

## 2026-11-01 — Keep files small
- What: every file aims under 150 lines; split by topic when bigger.
- Why: long sessions; small files keep context usage low.
