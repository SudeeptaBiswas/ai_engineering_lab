# ai_engineering_lab

## What it is
Hands-on AI engineering lab — part of the 2026 career transition.

## How to run
Python 3.13 via uv 0.13.6 (`pyproject.toml` + `uv.lock`, `.venv` git-ignored).
- Sync env: `uv sync`
- Run a file: `uv run python <path>.py` from repo root.
- Type check: `uv run pyright <path>.py` (strict, same as Pylance).
- If `uv` not found in an old shell: restart the terminal (PATH was updated).

## Where things live
- `docs/STATUS.md` — current state + task queue. Read first each session.
- `docs/PLAN.md` — phases, stack, how we work.
- `docs/TOPICS.md` — every topic with hours. Mark done date when finished.
- `docs/PROGRESS.md` — hours + % per phase. Update when a topic finishes,
  and report the new % to the user.
- `docs/DECISIONS.md` — requirement changes and why.
- `NN_phase_name/` — lessons + exercises, one folder per phase.
  Lesson files carry the topic id: `LESSON_1_7.md`, `exercises_1_7.py`,
  `examples_1_7_2_http.py`. Never a bare `exercises.py`.
- `assistant/` — the one real app, grows v1→v10 (from topic 2.6).
- `lab_tools/` — shared helpers, installed by `uv sync`. Debug logging:
  `from lab_tools.log import debug, log`, then `@debug` on a function.
  Exercise checks: `from lab_tools.check import check`, then
  `check("label", lambda: my_func(1), expected)`. Never a local copy.

## Must never break
- Files stay small: aim under 150 lines. Split before growing.
- One concern per commit. Commit + push at each finished step.
- New/changed code: 0 pyright errors before commit.
- No secrets in the repo. Keys go in `.env` (git-ignored).
