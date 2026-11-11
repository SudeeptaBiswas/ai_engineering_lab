# 3.1 Prompt patterns: system, few-shot, step-by-step (~2 h)

Basic level, first topic of phase 03. Next: 1.6 pydantic, then 3.2
structured output, 3.3 tool calling (assistant v2).

All numbers **measured on BISWAS** (i5-1135G7, no GPU), Ollama 0.40.14,
qwen3:1.7b, temperature 0, seed 42, 2026-11-11. Scores were the same in
every run (part 1: 3 runs, part 2: 2 runs); times vary by a few seconds.

## The question of this lesson
A support inbox gets tickets all day. You want code to send each one to
the right team: **billing**, **login**, **bug** or **other**. The model
must answer with one of those words, because code reads it, not a person.

Asked plainly, *"Classify this support ticket: I was charged twice..."*,
qwen3:1.7b wrote a paragraph: *"This support ticket is classified as a
**complaint**..."*. Not one of the 4 words. Code can't route that.

A **prompt pattern** is a known way to write the messages so the answer
comes back in the shape you need. You already used one: `"Be brief."` as
the system message in 2.6.

## Java → Python map
| Java | Python |
|---|---|
| `s.strip().toLowerCase()` | `s.strip().lower()` |
| `s.startsWith("Answer:")` | `s.startswith("answer:")` |
| `s.lines().toList()` | `s.splitlines()` |
| `s.split(":", 2)` (limit = parts) | `s.split(":", 1)` (maxsplit = cuts) |
| `Double.parseDouble(s)` + `NumberFormatException` | `float(s)` + `ValueError` |
| `Function<String, List<Message>>` | `Callable[[str], list[Message]]` |

## 1. Three ways to ask, same 8 tickets
| Prompt | One label back | Correct | Time (8) | Prompt tokens |
|---|---|---|---|---|
| zero-shot: just the question | 0/8 | 0/8 | 29.4 s | ~30 |
| system: + rules | 8/8 | 6/8 | 5.9 s | ~50 |
| few-shot: + 4 solved examples | 8/8 | 7/8 | 6.2 s | ~128 |

- **System message = the rules.** *"Reply with exactly one word:
  billing, login, bug, or other."* Format went 0/8 → 8/8. Also 5x faster:
  one word to write instead of a paragraph (2.3: writing tokens is the
  slow part).
- **Few-shot = show, don't tell.** 4 solved tickets go in as past chat
  turns: user = ticket, assistant = label. The model reads them as "what
  I answered before" (memory, 2.6) and copies the pattern.
- Few-shot fixed 2 misses (*"reset email never arrives"* → login, not
  other; *"save button does nothing"* → bug, not billing) and **broke 1**:
  *"Where is your office located?"* → login. Examples teach things you
  didn't mean. Cost: 2.5x the prompt tokens.
- 8 tickets is too few to trust 6/8 vs 7/8. A real test set has 50+ (5.1).
  **Measure, don't assume** a pattern helps.

> ▶ **Now run part 1** (needs Ollama, ~43 s): the table above, live, with
> each answer.
> `uv run python 03_prompting_tools/3_1_prompt_patterns/examples_3_1_1_classify.py`

## 2. Step-by-step: give the model scratch paper
Word problems: *"A tank holds 120 liters and is 3/4 full. 25 liters are
used. How many liters are left?"* (65). Six of them:

| Way | Right | Followed the format | Time (6) | Tokens written |
|---|---|---|---|---|
| direct: "Reply with only the final number." | 5/6 | 0/6 | 31.4 s | 478 |
| step-by-step + last line `Answer: <n>` | 6/6 | 6/6 | 49.6 s | 832 |
| `think=True` (separate run, 2.3) | 6/6 | — | 210.8 s | 3336 |

- **direct**: the rule was ignored 6/6. The model is trained to show
  work, so it mostly did. Its shortest answer (13 tokens:
  `120 - (25) = 95`) skipped "3/4 full" and was the **wrong** one.
- **step-by-step**: right 6/6, and every answer ended `Answer: ...`, so
  code can find it. Why it works: each token is predicted from the ones
  before (2.1). Written steps are input for the next steps.
- **think=True** is the same idea built in, hidden, and 4x slower here
  (210.8 s vs 52.3 s for step-by-step in that same run). Same score.

> ▶ **Now run part 2** (needs Ollama, ~2 min; think on 2 problems only).
> `uv run python 03_prompting_tools/3_1_prompt_patterns/examples_3_1_2_steps.py`

## 3. Parse what comes back, never trust it
The prompt asks for a shape; code still checks it:
- With rules, labels came back clean here. Not guaranteed: zero-shot
  wrapped words in `**...**` (markdown bold), and another model or prompt
  may add a `.`. Clean (strip, lower, drop `.` and `*`), then accept only an exact
  label. A sentence is **not** a label, even if it has "bug" in it.
- `Answer: 8.00` vs expected `8`: compare as **numbers**, not text.
- Take the **last** `Answer:` line: a model may correct itself.

This is the weak form of "structured output". 3.2 asks for JSON and
checks it with pydantic: same idea, stronger shape.

## 4. Things that bite
- **Temperature 0 + seed for tests.** Same input → same answer (2.4).
  Without it, a test can pass today and fail tomorrow.
- **Small models obey some rules, not others.** One word: yes. "Only
  the number" on maths: no. Test each rule you rely on.
- **A system prompt is not security.** A ticket that says "ignore the
  rules" can win (3.4 prompt injection).
- **Every example and step costs tokens** = time and context (2.6
  budget). Use the fewest that pass your test set.

## 5. Where it is used next
| Lesson | Uses |
|---|---|
| 3.2 Structured output | the rules + parse idea, with JSON + pydantic |
| 3.3 Tool calling | the system message describes the tools |
| 4.6 PDF RAG | rules: "answer only from the context, else say I don't know" |
| 5.3 LLM-as-judge | rules + few-shot to grade answers |
| 6.1 Agent loop (ReAct) | step-by-step + a fixed last line, parsed like `Answer:` |

## Exercises: make the tests pass
You write the 6 `raise NotImplementedError` functions in
[prompts_3_1.py](prompts_3_1.py). The spec is
[exercises_3_1.py](exercises_3_1.py): 20 tests without Ollama + 2 real.

| Function | Does | Tests |
|---|---|---|
| `few_shot_messages` | rules + examples as turns + question | 2 |
| `parse_label` | clean a reply, return a label or None | 6 |
| `final_answer` | text of the last `Answer:` line | 4 |
| `same_number` | `"8.00"` vs `"8"` → True; `"eight"` → False | 4 |
| `score` | share right; different lengths → ValueError | 3 |
| `classify` | few-shot POST to Ollama, then `parse_label` | 1 fake + 2 real |

```
uv run pytest 03_prompting_tools/3_1_prompt_patterns/exercises_3_1.py -v
```
Ollama off? Add `-m "not ollama"`. Reference solution, measured:
**22 passed in 1.82 s**, pyright 0.
