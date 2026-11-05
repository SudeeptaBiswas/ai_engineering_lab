# Status

Updated: 2026-11-04

## Now
- 1.1–1.4 done. Overall 3.5%. User working on 2.1 (lesson written).
- 2.1 exercises: 11/11 PASS (2026-11-05, uncommitted user code). Not done yet —
  edge cases fail (checked by running them):
  1. next_word: FIXED 2026-11-05 (`"a b","a"` -> 'b'). Left: line 78 `if` is
     always true now, so `elif` (80-81) never runs — delete both, keep line 79.
  2. most_common_pair: glues pair to one string, then `list()` splits it.
     `["ab","c","ab","c"]` -> ('a','b') (want ('ab','c')). `["a","b"]` -> IndexError
     (`- 2` skips last pair). Fix: key = tuple, range(len - 1).
  3. fit_context: pops from caller's list (TEST_CHAT changed between tests);
     system alone over budget -> IndexError. `...` line left.
  4. most_likely: overwrites caller's logits dict.
  5. decode: enumerate(vocab) — works only while ids = positions.
     `decode([5], {"<unk>":0,"hi":5})` -> ''. Fix: invert vocab once.
  6. pyright: 10 errors (unused Counter, untyped debug_print). Rule: 0.
  7. Style: `token = "";`, `softSome` camelCase, `id` shadows built-in.

## Queue
a. User works 2.1 → check, mark done, update PROGRESS.
b. Write lesson 2.2: Ollama (cover thinking on/off; `think:false` was ignored in test).
c. Lesson 1.7: files, JSON, httpx (order: docs/PLAN.md).

## Done
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
