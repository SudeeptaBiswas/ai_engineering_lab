# ai_engineering_lab

## What it is
Hands-on AI engineering lab — part of the 2026 career transition.

## How to run
Python via uv (`pyproject.toml` + `uv.lock`). Commands added once uv is set up.

## Where things live
- `docs/STATUS.md` — current state + task queue. Read first each session.
- `docs/PLAN.md` — phases, stack, how we work.
- `docs/TOPICS.md` — every topic with hours. Mark done date when finished.
- `docs/PROGRESS.md` — hours + % per phase. Update when a topic finishes,
  and report the new % to the user.
- `docs/DECISIONS.md` — requirement changes and why.
- `NN_phase_name/` — one top-level folder per phase, each with a short README.

## Must never break
- Files stay small: aim under 150 lines. Split before growing.
- One concern per commit. Commit + push at each finished step.
- No secrets in the repo. Keys go in `.env` (git-ignored).
