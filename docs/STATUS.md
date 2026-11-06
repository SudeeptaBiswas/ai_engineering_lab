# Status

Updated: 2026-11-06

## Now
- 1.1–1.4 + 1.7 + 2.1 + 2.2 done. Overall 5.5% (phase 01: 57%, 02: 28%).
- Optional 2.1 cleanup (user skipped, 2026-11-05): old most_common_pair code in
  a string literal; `softSome` name; most_likely rounds before picking best
  (300 equal tokens -> ("", 0)); next_word `if` always true; decode inner loop.

## Queue
a. BISWAS PC: `uv sync` (lab_tools) + `ollama pull qwen3:1.7b` (for 2.2 section 7).
b. Lesson 2.3: chat API over HTTP (order: docs/PLAN.md).
c. Optional: compare gemma4 E2B vs qwen3:4b on this PC (user to decide).
d. Optional: one shared `check()` in lab_tools (6 lesson copies now).

## Done
- 2026-11-06 — topic 1.7 done: 12/12 PASS, pyright 0. Lesson files renamed
  with topic id (24 files). 1.7 `check()` numbers results + `path:line` links.
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

## Review notes 1.3 + 1.4 (2026-11-03)
- 1.4 `last(0)` returns ALL messages (`[-0:]` == `[0:]`). Guard: `if n <= 0: return []`.
- 1.3 `Counter`, `defaultdict` imported, unused. `word_freq` could be `Counter(text.lower().split())`.
- 1.3 `merge_counts`: old code left as a string literal — delete it.
- 1.3 `top_k`: `key=scores.get` is shorter than the lambda.
- 1.4 `run` overrides: add type hints `(self, arg: str) -> str` to match `Tool`.
