# Decisions

Newest first. One entry per change: what, replaces what, why.

## 2026-11-11 — Three levels: Basic → apply, Intermediate, Advanced
- What: topics grouped in three levels (PLAN.md Levels, TOPICS.md `Lvl`,
  PROGRESS.md Levels). Basic 58 h left, Intermediate 60 h, Advanced 63 h.
  After Basic: CV + apply. Intermediate runs during the job hunt.
- Replaces: one straight run through phases 01–10 (apply at the end).
- Moved early into Basic: 1.8 async, 7.1–7.4 MCP server, 8.1 FastAPI,
  8.4 Docker. Reason: job posts ask for MCP and an API.
- 6.1 agent loop: Claude put it in Basic, user moved it to Intermediate
  (same day).
- Moved late: 4.7–4.11, 5.3–5.4 to Intermediate; 6.4 to Advanced.
- Nothing dropped: total stays 199 h. No CV task in the plan (user: no need).
- Level contents picked by Claude; user has not reviewed the topic detail.
- Why: user's goal is to learn and apply for a job ASAP.

## 2026-11-09 — 2.6: tests given, user writes the app; v1 memory scope
- What: for 2.6 Claude writes the pytest tests (the spec) and the user
  fills `raise NotImplementedError` stubs in `assistant/`. Tests stay in
  the lesson folder (`exercises_2_6_*.py`); `assistant/` is a package,
  found via `"."` in pytest `pythonpath` (pyright finds it already).
- Replaces: 1.9 style (user writes the tests, `pytest.fail` stubs).
- v1 memory = in RAM + trim to an estimated token budget + `/reset`.
  Saving to a JSON file: rejected for now (user's call, 2 h budget).
- `num_ctx` sent explicitly (4096): measured, Ollama drops messages over
  it silently (wrong answer, no error).
- `TypedDict` for messages, as planned on 2026-11-04.
- `.vscode` pytestArgs: skipped on BISWAS (no `.vscode/` there); do it on
  10284Sudee.
- Why: user's call (question batch before the lesson).

## 2026-11-09 — Review docs: flows, quiz, keyword glossaries
- What: `docs/review/`: README (big picture + how to use), REVIEW_01_python,
  REVIEW_02_llm (per topic: flow, must-remember, quiz with hidden answers),
  GLOSSARY_AI + GLOSSARY_PYTHON (A–Z, one line each, topic id).
  Start: 12 topics, 45 questions, 102 keywords.
- Upkeep: each finished topic adds its section + keywords (CLAUDE.md).
  A phase file over 150 lines splits by topic range.
- Rejected: Claude Docs online (content leaves the PC); Java-mapping
  section (user didn't pick it; glossary Python keeps a Java column).
- Why: user wants to review and remember the concepts later, from one place.

## 2026-11-09 — "▶ Now run" lines inside each LESSON md
- What: after the sections an examples file covers, a "▶ Now run" line
  with the exact command and the expected result. From 1.9 on.
- Replaces: one "read, run, solve" line at the top only.
- Why: user's idea: following the md alone should give the order
  read → run → read → run → exercises.

## 2026-11-09 — Exercises switch to pytest from 2.6; fakes + 1 real test
- What: from 2.6 on, exercises are pytest tests, not `check()`. Code that
  calls Ollama gets tested with fakes (`monkeypatch`); one test per file
  marked `@pytest.mark.ollama` hits the real Ollama.
- 1.9 exercises test the user's own 2.5 code. `pyproject.toml` puts the
  2.5 folder on the import path (pytest `pythonpath`, pyright `extraPaths`):
  folders starting with a digit can't be packages.
- Stubs are `pytest.fail("not written yet")`, not `...`: an empty test passes.
- Replaces: `check()` (stays in 1.2–2.5).
- Why: user's call. Fakes: run with Ollama off, test error cases (501) in
  one line, fixed answers. The real test proves Ollama agrees.

## 2026-11-09 — Lesson rules enforced by a script, not memory
- What: `lab_tools/lesson_rules.py` checks every `examples_*.py`: no idioms
  in code (comprehension, lambda, ternary, zip, unpacking...), a `# concise:`
  line after each explicit block, no one-letter names, docstrings with
  Args/Returns, max 150 lines. `# rule-ok: <reason>` skips idiom + name
  rules on one line (a lesson whose topic IS the idiom).
- Runs: Claude Code hook after each Write/Edit (`.claude/settings.json`) +
  git pre-commit (`.githooks/`, needs `git config core.hooksPath .githooks`
  once per clone). 14 older files listed in `lesson_rules_legacy.txt`.
- Scope: lesson code only. User's exercise code is not checked.
- Can't check: that the long form equals the concise one, or name quality
  beyond length. User review covers those.
- Replaces: rules only in PLAN.md (read when remembered).
- Why: 2.3, 1.5 and 2.5 were written without explicit forms; rules in a doc
  nobody re-opens get missed. A failing check can't be missed.

## 2026-11-08 — Javadoc-style docstrings on every lesson function
- What: each function says what it does, then Args / Returns / Raises
  (Java @param / @return / @throws), with example values. 2.5 exercises
  split in 2 files to stay under 150 lines.
- Replaces: one-line docstrings (input/output were not clear).
- Why: user could not tell input, action and output from `embed`'s docstring.

## 2026-11-08 — Critical issues = test cases; minor notes wait for the end
- What: a critical issue (wrong result, crash, hidden bug) gets a check in
  the exercises, so it shows as FAIL. Minor notes (style, dead code, naming,
  file length) go in STATUS.md "End-of-course review" and are not raised
  topic by topic.
- Replaces: review notes after each topic with an "optional fix?" question.
- Why: user's call — tests catch what matters; polish is batched at the end.

## 2026-11-07 — Teach every new idea through context, not definitions
- What: each new idea in a lesson starts from a real example and shows how
  it connects to earlier lessons and to later ones (where it gets used).
  Definition comes after, short.
- Replaces: definition-first sections (e.g. 2.4 "top_p = keep the smallest
  group…").
- Why: user said they learn easily with real examples and clear links to
  the rest of the content, not just definitions.

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
