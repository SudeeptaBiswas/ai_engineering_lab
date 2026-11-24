# Decisions

Newest first. One entry per change: what, replaces what, why.

## 2026-11-25 — 4.4: Chroma with nomic, plus a built-in model comparison
- What: lesson 4.4 stores chunks in Chroma with Ollama nomic-embed-text
  vectors (as 4.1–4.3). One extra part runs the same 12 questions with
  Chroma's built-in embedding model.
- Why: same vectors keep the 4.3 scores comparable; the comparison
  covers the interview gap "compare embedding models" (INTERVIEW_NOTES
  2026-11-23). `chromadb` install: user OK; user runs `uv add` (Claude's
  run was blocked by the permission check).

## 2026-11-25 — 4.3: Claude gave code for 2 stubs; file kept at 269 lines
- What: user wrote `split_into_sentences`, `pack_pieces`,
  `chunk_by_sentences`, `chunk_recursively` (adapted from the example
  with Claude's fixes). On request, Claude gave the code for
  `chunk_by_paragraphs` and `chunk_by_meaning`; the user pasted it.
- Replaces: "hints only" for these 2 (as 2026-11-18 for 4.2).
- `chunking_4_3.py` is 269 lines (max 250). Pre-commit warned (user
  code: warning only). User chose not to split it.

## 2026-11-18 — 4.2: Claude filled the last 5 stubs
- What: user wrote `read_pdf_pages` + `find_repeated_lines`, then asked
  "implement pdf_text_4_2". Claude filled the other 5 in the example style.
- Replaces: user fills all 7 stubs (STATUS item f). "Hints only" still
  stands for other exercises unless the user asks again.

## 2026-11-16 — 4.2: pypdf, a built sample PDF, layout mode
- What: `pypdf` 7.1.0 added (`uv add`, user OK). The sample PDF is built
  by `make_pdf_4_2.py` from the 4.1 handbook, by fixed rules (header,
  footer, cut words, fi/fl ligatures, no-break space after numbers, one
  scanned page). Pages read in pypdf's `"layout"` mode.
- Rejected: pymupdf (AGPL, native wheel), pdfplumber (slower, more
  deps); a user-supplied real PDF (numbers would depend on the file).
  `"plain"` mode: 0 paragraph gaps vs 42 in layout (4.3 cuts at paragraphs).
- Why: same facts as 4.1, so the 4.1 questions measure the cleaning.
  pypdf is what LangChain's `PyPDFLoader` uses (4.5).
- Measured: exact-text answers 3/9 raw → 9/9 clean; vector search right
  chunk 1st 8/9 → 9/9 (the miss was a near tie, 0.485 vs 0.483).
- Not done: OCR for scanned pages, columns, tables, heading detection.
- `.gitattributes`: `*.pdf binary`. The built PDF has no NUL byte, so
  git took it for text and would turn LF into CRLF on checkout
  (`core.autocrlf true`); that breaks the byte offsets inside the PDF.

## 2026-11-15 — 4.1 reviewer findings: 10 fixed, 2 kept on purpose
- What: the lesson-reviewer's 12 findings on 4.1 (STATUS). Fixed: 1
  one-off numbers marked (*) in the LESSON; 3 one prompt wording (stubs =
  examples); 4 real test reads "15-minute" too; 6 + 7 + 11 + 12 names
  and one step per line; 8 speed timing = scoring only, after a warm-up;
  9 `top_k` < 0 → [] tested (31 tests now); 10 `num_ctx`, `top_k`
  explained.
- Kept: 2 different names in examples vs stubs (on purpose: examples
  must not hand over the stub answers; now a written exception in
  CODE_STYLE rule 2 and in the reviewer, so it isn't flagged again).
  5 documents joined before cutting: the release-notes title sticks to
  the last handbook chunk; fixing it changes every measured number for
  a small gain.
- Measured change: numpy vs loop is ~100x (was "~150x"): the old loop
  time included turning the vectors into lists.
- Why: user: "fix only what is needed"; 2 has a reason, and changing it
  would make the stub names match the examples' answers.

## 2026-11-15 — Rules kept by a script, a template and a reviewer
- What: `lesson_rules.py` now also checks `assistant/`, the 2.6 / 3.5
  tests + fakes, and every `.py` from phase 04 on: `@debug` + a log line
  (stubs and "No own log lines" helpers excepted), no "Checks" test
  docstring, plus the old name / docstring / length rules. LESSON md from
  4.1 on: the six sections of CODE_STYLE section 12, in order. Idiom
  rules stay examples-only; examples before 4.1 keep the old rules.
  `--all` mode added. Template `docs/templates/LESSON_TEMPLATE.md`;
  `lesson-reviewer` agent in `.claude/agents/`.
- User's code: files with `# lesson-rules: user-code` get warnings only,
  never a blocked commit (user's call). Replaces "user's code not
  checked" (2026-11-09).
- Measured: planted breaks in a scratch repo, 11/11 handled as expected.
  First run on the repo found 15 misses in code from this same day.
- Also: `cli.py` drops "﻿" (a PowerShell pipe adds it to line 1),
  with a test.
- Why: user asked how to make sure rules are not forgotten. A rule in a
  doc gets missed; a check that runs on every edit can't be.
- Out of scope: `lab_tools/` itself (tooling, not lesson or app code).

## 2026-11-15 — assistant/ + its tests brought to the latest style
- What: every function Claude writes gets `@debug` + start/result logs
  (examples, stubs, tests, fakes, `assistant/`); loop helpers excepted
  (CODE_STYLE rule 9). Test docstrings say what + why, no "Checks:".
  No list positions with meaning (`tool_specs[3]`, `REAL_STREAM_LINES[4]`).
  Renames: `MODEL` → `CHAT_MODEL` (same as 4.1), `DONE_WORDS` →
  `REFUND_DONE_WORDS`, `ORDER_LOOKUP` → `ORDER_LOOKUP_REPLY`.
  answer_check returns; chat_turn prints the correction (rule 3).
- multiply arguments `a` / `b` → `first_number` / `second_number`.
  Measured, 5 multiply questions x 2 runs, fresh chat each: tool called
  4/5 both ways (the same question, "17 items at 23.75", never calls it).
  Right answers 5/5 → 4/5: that no-tool question, answered by the model
  itself; a single rerun got it right. 3.3's `toolbox_3_3.py` keeps a / b.
- Replaces: `@debug` in example files only; "Checks: ..." test docstrings.
- Why: user's call (all 3 "Recommended"), asked to bring the old code
  used in 4.1 prep up to the latest feedback.

## 2026-11-15 — Commit + push only after the user approves
- What: project CLAUDE.md, PLAN.md and the memory note now say: commit
  and push each finished step only after the user approves.
- Replaces: "commit + push at each finished step" / "push pre-approved".
- Why: conflicted with the user's global review flow; user chose it.

## 2026-11-15 — Backfill: decisions that were only in STATUS
- 2026-11-12: pydantic 2.14.3 added (`uv add`, user OK) for lesson 1.6;
  used by 3.2 and `assistant/tools.py`.
- 2026-11-09: `assistant/` uses qwen3:1.7b + `think: False` (as lessons
  since 2.3). Closes "not decided: model for the real app" (2026-11-06).
  Open, optional: compare gemma4 E2B / qwen3:4b (STATUS queue).
- 2026-11-15: user's own edit to `examples_3_4_2_tools.py` kept (user's
  call), so LESSON_3_4 part 2 text no longer matches that file.
- 2026-11-15: rewriting the 3.4 sample to CODE_STYLE: not wanted (user).

## 2026-11-15 — Lesson .md follows the style guide too; 4.1 reviewed
- What: CODE_STYLE.md section 12: each LESSON md has problem, goal,
  how, steps, your path, then exercises with an `in → out` example per
  function. Simple words, short sentences. LESSON_4_1.md rewritten.
- 4.1 code reviewed against CODE_STYLE: `@debug` + start/result logs on
  every example function; one step per line; no tuple positions
  (`SearchTimes`, `EmbeddedHandbook`); print only in `main`; tests named
  by behaviour, docstring says why. Speed part moved to its own file:
  part 1 was 260 lines. Parts now: 1 search, 2 speed, 3 answer
  (`examples_4_1_2_answer.py` → `examples_4_1_3_answer.py`).
- Replaces: lesson md written as sections only (no goal / steps).
- Why: user's feedback: the lesson must say the goal, how, and the
  steps in simple words, with examples where needed.
- Scope: lesson 4 and later. Older lessons not rewritten (not asked).

## 2026-11-15 — 4.1: user fills stubs; numpy added
- What: lesson 4.1 written by Claude (lesson, 2 examples, 6 stubs in
  `rag_4_1.py`, 30 tests); user fills the stubs. `uv add numpy`
  (2.5.4; needed `--system-certs` on BISWAS).
- Replaces: open STATUS question "4.1: write it or read the solution".
- Why: user's choice (both "Recommended"). Topic is "with numpy".
- Data: made-up handbook (13 sections) + generated release notes (108
  versions), so the model can't know the facts. Generator script not
  kept (one-off; seed 7).

## 2026-11-15 — assistant v2 (Claude writes it) + v1 restyled
- What: Claude wrote v2: 3.3 tools + fake `refund`, tool loop in
  `chat_turn.py`, 3.4 gate in `tool_gate.py`, streaming kept. Tests in
  `03_prompting_tools/3_5_assistant_v2/`. All of `assistant/` and the 2.6
  tests rewritten to CODE_STYLE.md (new names, see LESSON_2_6 note).
- Choices (user, all "Recommended"): fake refund yes; new test folder;
  restyle v1 tests; keep streaming.
- Claude's calls: memory keeps only question + final answer (tool
  messages live one turn: trimming could split a call from its result);
  temperature 0 + seed 42 in every request (tools need steady choices);
  `--debug` shows the log, hidden otherwise; gate also blocks a refund
  with no / non-number amount (the 3.4 review bug).
- Standing rule (user): when old `assistant/` code is used, bring it up
  to the latest feedback first, so it is always ready to review.
- System prompt: the 3.3 one. Measured: + "Answer in 1 to 3 short
  sentences." dropped tool use 5/5 → 3/5.

## 2026-11-15 — Code style guide for lesson code
- What: [CODE_STYLE.md](CODE_STYLE.md), 11 rules: clear names with purpose,
  same name across functions, one job per function, inputs as parameters,
  docstring goal-first + "How:" steps, simple words, one step per line,
  result in a variable before return, comment on multi-step lines,
  `@debug` logging (start / steps / result) in examples, tests say what
  they check. Applies from lesson 4.1. Line limit 150 → 250 (aim 150),
  `lab_tools/lesson_rules.py` MAX_LINES changed to match.
- Replaces: "full descriptive names" alone (PLAN "How we work"); hard 150.
- Why: user's review of 3.4 (12 points): names like `SUSPICIOUS`,
  `ask_json`, `item[0]` unclear; `ask_json(...)["injection"]` unreadable;
  globals mixed with parameters; functions doing many jobs; no log of
  the call order; docstrings don't say the goal.
- Old lessons (≤ 3.4) not rewritten (not asked).
- Same day, 2nd round: name by use (`reply_format`, not `reply_schema`);
  name each value before comparing; log `expected=... got=...`; log
  lines now start with `file:line` (`lab_tools/log.py`, all files);
  `cut_text()` + `TEXT_CUT_LENGTH` (40) in one place; Java twin in code
  comments dropped.

## 2026-11-13 — 3.3: user writes it; assistant v2 is its own step
- What: 3.3 by hand: Claude writes lesson, tools, tests; user fills the
  4 stubs. assistant v2 (tools in `assistant/`) comes after, in its own
  commit.
- Replaces: open STATUS question (write vs read Claude's solution);
  PLAN v2 "after 3.3" built in the same step.
- Why: user's choice (both "Recommended" options). Smaller steps.
- Tools given in `toolbox_3_3.py`: one file with tools + loop was 190 lines.
- Still open: Claude API topic; "AI workflow integration" (STATUS queue).

## 2026-11-12 — VS Code test folders: tracked + checked
- What: `.vscode/settings.json` + `launch.json` (F5 debug setups) now in
  git (rest of `.vscode/` still ignored). `lab_tools/vscode_tests.py` fails the pre-commit if a folder
  with pytest files is missing from `pytestArgs`.
- Replaces: settings.json git-ignored, edited by hand on each PC.
- Why: 3.1 tests didn't show in VS Code (folder not listed); user asked
  to track it and make sure new test folders always get added.

## 2026-11-11 — 2.6: Claude wrote the solution
- What: Claude filled the 10 stubs in `assistant/` (user: "write it, do
  commit"). User reads the code instead of writing it.
- Replaces: user fills the stubs (2026-11-09 entry). The "hints only"
  rule for exercises still stands unless the user asks again.
- Why: user wants the job ASAP; libraries do chat memory in real work.
- Still open: same choice for 3.3 and 4.1 (STATUS queue).
- Added: `__main__.py` sets stdout `errors="replace"`. Measured: piped
  output on this PC is cp932, an emoji from the model crashed the app.

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
  (Later: qwen3:1.7b, see the 2026-11-15 backfill entry.)

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
