# Decisions

Newest first. One entry per change: what, replaces what, why.

## 2026-11-06 — Chat lessons use qwen3:1.7b with `"think": False`
- What: from 2.3, /api/chat calls send `"think": False`; model qwen3:1.7b.
- Why: measured on 10284Sudee, num_predict 60: 1.7b without it 12.8 s and
  an EMPTY answer (all tokens went to thinking); with it 2.5 s, clean answer.
  qwen3:4b with `think: False` 8.5 s and its thinking leaks into the answer.
- Not decided: model for the real app (`assistant/`, 2.6+). Revisit there.

## 2026-11-06 — One shared `check()` in lab_tools
- What: `lab_tools/check.py`; every exercises file does
  `from lab_tools.check import check`. Results numbered; FAIL prints
  `path:line` for the test and for the error line in your code.
- Replaces: 6 copies (2 styles: 1.2/1.3 passed a value, rest a lambda).
  1.2/1.3 now use lambdas too, so one crash no longer stops the file.
- Why: copies drifted (only 1.7 had the new output). Files 100 lines shorter in total.
- Not done: pytest. Still topic 1.9; it will replace `check()` from then on.

## 2026-11-06 — Lesson file names carry the topic id
- What: `LESSON_1_7.md`, `exercises_1_7.py`, `examples_1_7.py` (one file) or
  `examples_1_7_2_http.py` (several). 24 files renamed, links fixed.
  `hello.py` kept (already unique).
- Replaces: same names in every folder (`exercises.py` x6, `LESSON.md` x7).
- Why: user could not tell which file a tab or a result line belonged to.
- Rejected: VS Code `workbench.editor.labelFormat` (tabs only, not search,
  terminal, or chat); header line in output (output only).
- Also: `check()` in 1.7 now numbers results and prints `path:line` links
  (moved to lab_tools, entry above).

## 2026-11-05 — httpx + always `127.0.0.1` for Ollama
- What: `uv add httpx` (0.28.1). Ollama URL = `http://127.0.0.1:11434`, never
  `localhost`, in lessons and `assistant/`.
- Why: measured on 10284Sudee: `localhost` 2.16 s per call, `127.0.0.1` 0.02 s
  (IPv6 tried first). 1.7 exercises: 25 s -> 1.2 s.
- Rejected: stdlib urllib (clunkier; httpx needed from 2.3 anyway).
- User chose: 1.7 exercises call the real Ollama (not httpx MockTransport),
  so they fail when Ollama is off. Only fast endpoints (tags, show, version).

## 2026-11-05 — Shared debug logging: `lab_tools/log.py`
- What: `from lab_tools.log import debug, log`. `@debug` above a function =
  its `log.debug(...)` lines print (prefixed by function name). One logger.
- How: project is now an installed package (`[build-system]` uv_build in
  pyproject; `uv sync` installs `lab_tools/` into .venv). Works from any folder.
- Replaces: `debug_print` + global `DEBUG` in 2.1 exercises (all-or-nothing,
  untyped = 9 pyright errors), then a per-file copy of the logging block.
- Why: user wanted per-function toggle, one logger, no repeated code.

## 2026-11-04 — Type check with pyright (strict)
- What: pyright 1.1.414 dev dependency, `typeCheckingMode = "strict"` in
  pyproject (same as user's Pylance). New/changed code: 0 errors.
- Replaces: no type check; Pylance red lines were missed (bare `dict`).
- Why: best practice is full type hints (`dict[str, str]`, typed empty lists).
- Not done: `TypedDict` for messages — wait for `assistant/` (2.6).
- Then fixed phase 1 + 2.1 exercises too: 56 -> 2. Hints only, output same.
  Left on purpose: 2.1 exercises `import math` / `Counter` = hints for the
  user's answers; error clears once used. `Shape()` demo: pyright ignore.

## 2026-11-04 — Lesson code: full names + detailed comments
- What: descriptive names (`word_to_id`, `next_word_counts`, `position`),
  no one-letter names (`a`, `b`, `m`, `e`, `i`). Comments show what a
  variable holds (example value) and what each expression does.
- Scope: 2.1 and all future lessons. 1.1–1.4 stay as they are.
- Replaces: short names + one-line comments.
- Why: user asked; easier to read while learning.
- Cost: 2.1 examples split into 4 files to stay under 150 lines.

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
