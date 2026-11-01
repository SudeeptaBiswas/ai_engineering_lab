# Decisions

Newest first. One entry per change: what, replaces what, why.

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
