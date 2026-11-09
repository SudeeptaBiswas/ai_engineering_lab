# Status

Updated: 2026-11-09

## Now
- 1.1–1.5 + 1.7 + 2.1–2.5 done. Overall 8.5% (phase 01: 67%, 02: 78%).
- Lesson 1.9 pytest written, waiting for the user. Lesson rules checked by a hook.
- Review rule (DECISIONS 2026-11-08): critical issue → a check; minor → the
  "End-of-course review" list at the bottom.
- From 2.6: exercises are pytest tests (DECISIONS 2026-11-09).

## Queue
a. User works 1.9 → check, mark done, update PROGRESS. Then 2.6 (assistant v1).
b. Optional: compare gemma4 E2B vs qwen3:4b on this PC (user to decide).

## Done
- 2026-11-09 — lesson 1.9 written (pytest: assert, approx, raises, parametrize,
  fixture, monkeypatch, marker): 2 examples (7 + 3 tests, 0.07 s / 0.42 s),
  exercises test the user's 2.5 code. Reference 14/14 in 0.93–3.64 s
  (3 runs, 10284Sudee); 13 + 1 deselected without Ollama. pyright 0,
  lesson rules 0. pyproject: pythonpath/extraPaths + `ollama` marker.
- 2026-11-09 — topic 2.5 done: 17/17 PASS (10 + 7), pyright 0. nomic-embed-text
  now on 10284Sudee too.
- 2026-11-09 — lesson-rule check: `lab_tools/lesson_rules.py` + Claude hook
  + git pre-commit. Fake files: 9/9 planted breaks caught, good file 0,
  `# rule-ok:` skipped; pre-commit exit 1 on bad staged file. 14 old files
  in legacy list. BISWAS: run `git config core.hooksPath .githooks`.
- 2026-11-08 — 2.5 comments: Javadoc-style docstrings (Args/Returns/Raises),
  more line comments; exercises split in 2 files. Solved copy 17/17, pyright 0.
- 2026-11-08 — lesson 2.5 written (embeddings, cosine, search): 2 examples +
  17 checks; reference 17/17 in 2.3–2.5 s (3 runs, BISWAS), pyright 0.
  nomic-embed-text pulled (274 MB, 768 numbers, length 1.0). qwen3:1.7b on
  /api/embed → 501. Batch of 5: 0.38–0.60 s vs 1.34–1.92 s one by one.
- 2026-11-08 — rule: critical bug → a check; minor → end-of-course list.
  3 old BUGs left for the end (user's call).
- 2026-11-08 — topic 1.5 done: 16/16 PASS in 3.7 s, pyright 0. Two rounds:
  chat_errors stub left at first; then `reply["messages"]` typo (key is "message").
- 2026-11-08 — lesson 1.5 written (modules, imports, exceptions): 2 examples,
  demo module, user module `chat_errors_1_5.py` + 16 checks; reference 16/16
  in 4.3–4.7 s (3 runs, BISWAS), pyright 0 (stubs + solution). Measured:
  missing model → 404 `{"error": ...}`; dead port → ConnectTimeout after timeout.
- 2026-11-08 — topic 2.4 done: 14/14 PASS, pyright 0. Bug fixed: T=0 compared
  word to `dict.keys` (method) → all 0.0. Check 12 failed once (2 answers at
  T=0, first call after model load); 3 reruns gave 1. Added a warm-up call.
- 2026-11-07 — lesson 2.4 written (sampling by hand + in Ollama): 2 examples +
  14 checks; reference 14/14 in 6.9–8.4 s (3 runs, BISWAS). qwen3 defaults:
  temperature 0.6, top_k 20, top_p 0.95. "a name" prompt too sure for a
  variety check (Whiskers 4/10 at T 1.5) → "an unusual name" (9/10 different).
- 2026-11-07 — BISWAS PC: `ollama pull qwen3:1.7b` done (1.4 GB).
- 2026-11-06 — topic 2.3 done: 12/12 PASS in 6.3 s, pyright 0.
- 2026-11-06 — lesson 2.3 written (chat API, roles, no memory, thinking,
  streaming): 2 examples + 12 checks; reference 12/12 in 3.1–5.7 s (5 runs).
  qwen3:1.7b + `think: False`: 2.5 s vs 12.8 s with thinking (empty answer).
- 2026-11-06 — shared `lab_tools/check.py` replaces 6 copies; 62/62 PASS.
- 2026-11-06 — topic 1.7 done: 12/12 PASS, pyright 0. Lesson files renamed
  with topic id (24 files). 1.7 `check()` numbers results + `path:line` links.
- 2026-11-05 — BISWAS PC: `uv sync` failed (`invalid peer certificate: UnknownIssuer`). Fixed with `uv sync --system-certs`; httpx 0.28.1 + lab_tools import OK.
- 2026-11-05 — lesson 1.7 written (files, JSON, httpx vs real Ollama): 2 examples + 12 checks; reference 12/12 in 1.2 s. httpx 0.28.1 added. `127.0.0.1` not `localhost` (2.16 s -> 0.02 s per call).
- 2026-11-05 — topic 2.2 done: 13/13 PASS + 5 edge cases fixed, pyright 0.
- 2026-11-05 — lesson 2.2 Ollama written: 2 examples + 13 checks; reference 13/13.
  Measured (10284Sudee, one run each): qwen3:4b 2.5 GB file / 3.2 GB in RAM,
  load 9.4 s, write 7.1 tok/s. qwen3:1.7b (pulled, `show` says 2.0B) 1.4 / 1.9 GB,
  load 1.9 s, write 15.4 tok/s. Thinking: `--think=false` ignored (210 tokens,
  leaks into answer); `--hidethinking` hides only (236); `/no_think` 54 on 4b,
  no effect on 1.7b (184). User chose: explain only, no default change.
- 2026-11-05 — topic 2.1 done: 11/11 PASS + 5 edge-case bugs fixed, pyright 0.
- 2026-11-05 — `lab_tools/log.py`: shared per-function debug logging (`@debug`).
- 2026-11-04 — type hints in phase 1 + 2.1 exercises: 56 → 2 pyright errors (2 = unused hint imports, on purpose). Same output.
- 2026-11-04 — pyright (strict) added; 2.1 examples 1–4: 18 → 0 errors, same output. 56 left elsewhere (docs/DECISIONS.md).
- 2026-11-04 — 2.1 code: full names + detailed comments; examples now 4 files. Same output; ref 11/11.
- 2026-11-04 — 2.1 code rewritten: explicit first, concise in comment; examples split in 2. Same output; ref answers 11/11.
- 2026-11-03 — BISWAS PC: Ollama 0.40.14 installed (winget, `--source winget`; msstore source fails with a cert error). qwen3:4b pulled (2.5 GB). Test: 6.99 tokens/s, 51 s; `--think=false` ignored here too.
- 2026-11-03 — qwen3:4b pulled (2.5 GB). Speed on this PC (10284Sudee, CPU only, 31.8 GB RAM): 5.8 tokens/s; one short answer took 80.6 s because it "thinks" first (436 tokens).
- 2026-11-03 — Ollama 0.40.14 installed (winget), `ollama --version` OK.
- 2026-11-03 — lesson 2.1 written; reference answers pass 11/11.
- 2026-11-03 — topics 1.3 + 1.4 done (8/8 + 8/8 PASS).
- 2026-11-02 — plan: one growing `assistant/` app, just-in-time Python.
- 2026-11-02 — lessons 1.3 + 1.4 written; reference answers pass 8/8 each.
- 2026-11-02 — topic 1.2 done (10/10 PASS).
- 2026-11-02 — topic 1.1 done; pytest added as dev dependency (by user).
- 2026-11-01 — uv 0.13.6 installed (winget); pyproject, uv.lock, .python-version.
- 2026-11-01 — topic breakdown: 68 topics, 199 h.
- 2026-11-01 — progress tracker: docs/PROGRESS.md (hours + %).
- 2026-11-01 — decided: name, layout, uv, pace.
- 2026-11-01 — plan review: 10 changes, saved in docs.
- 2026-11-01 — skeleton: README, CLAUDE.md, docs, .gitignore.

# End-of-course review
Minor notes, batched for the end (DECISIONS 2026-11-08). BUG = wrong result,
should get a check instead.

## Review notes 2.5 (2026-11-09)
- `search`: 2 embed calls instead of 1 (`embed([query] + notes)`); ranks by
  hand instead of reusing `top_matches` from part 1.
- Leftover `...` after each `return` (dead code), both 2.5 files.
- Lesson code (Claude's) breaks PLAN rules: 2.5 examples have no
  explicit-first / `# concise:` form and use short names (`x`, `v`, `s`, `i`).
  2.3 + 1.5 also have no markers (not checked by hand). Rewrite at the end.
- User's 2.5 exercise code: short names (`v`, `p`, `i`).

## Review notes 2.1 (2026-11-05)
- BUG: most_likely rounds before picking best (300 equal tokens -> ("", 0)).
- Old most_common_pair code in a string literal; `softSome` name;
  next_word `if` always true; decode inner loop.

## Review notes 1.5 (2026-11-08)
- Leftover `...` after each `return` (dead code), both files.
- `ask`: `else:` after `raise` not needed. `settings:dict` → `settings: dict`.
- chat_errors: TODO lines still in the class docstrings.

## Review notes 2.3 (2026-11-06)
- BUG: `ask_stream` keeps empty chunks (last line has content ""); docstring says skip.
  Check passes anyway (`> 1`). Fix: `if text: append`.
- `@debug` + `log.debug` left on `tokens_per_second`: prints a debug line each run.
- Leftover `...` after each `return` (dead code); commented-out code in
  `add_message` and `ask_stream`.
- File now 164 lines (aim under 150).
- `ask_stream` builds body with stream False then sets True: pass `True` directly.
- `ask` has no `raise_for_status()` (`stop_reason` does).

## Review notes 1.3 + 1.4 (2026-11-03)
- BUG: 1.4 `last(0)` returns ALL messages (`[-0:]` == `[0:]`). Guard: `if n <= 0: return []`.
- 1.3 `Counter`, `defaultdict` imported, unused. `word_freq` could be `Counter(text.lower().split())`.
- 1.3 `merge_counts`: old code left as a string literal — delete it.
- 1.3 `top_k`: `key=scores.get` is shorter than the lambda.
- 1.4 `run` overrides: add type hints `(self, arg: str) -> str` to match `Tool`.
