# 2.1 How LLMs work: tokens, context window (~1.5 h)

Read this, run [examples.py](examples.py), then solve [exercises.py](exercises.py).
No model yet — pure Python toys. Ollama comes in 2.2.

## The one idea
An LLM is a function: **tokens so far → a score for every possible next token.**
To write a reply it picks one token, appends it, and calls itself again.
That loop is called *autoregressive* generation. Nothing else is magic.

## Tokens
- The model never sees letters. Text → tokens (pieces) → integer ids.
- Pieces are usually sub-words: `"unbelievable"` might be `un` + `believ` + `able`.
- Built with **BPE**: start from characters, merge the most frequent
  neighbour pair, repeat many thousands of times. Vocab = all pieces + ids.
- Rule of thumb for English: ~4 characters per token. Other languages and
  code often need more tokens for the same meaning.
- Why you care: **cost, speed and limits are all counted in tokens.**

## Context window
- Max tokens the model sees in one call: system prompt + history +
  new question + **its own answer**. Sizes range from a few thousand to
  over a million, depending on the model.
- The model is **stateless** — like a REST call, it remembers nothing.
  "Chat memory" = your code resends the history every time.
- History grows → you must drop or summarise old turns. Keep the system
  message. This is what `assistant/` v1 will do (topic 2.6).
- Too much to fit (a whole PDF library)? That is why RAG exists (phase 04).

## From scores to text
- Raw scores are called **logits**. **Softmax** turns them into
  probabilities that sum to 1: `p_i = exp(s_i) / sum(exp(s_j))`.
- Always taking the top token = *greedy*. Sampling options: topic 2.4.
- The model predicts *plausible* text, not *true* text → hallucinations.

## How a chat model is made (one line each)
1. Pre-training: predict the next token on a huge pile of text.
2. Instruction tuning: train on (question, good answer) pairs.
3. Preference tuning (e.g. RLHF): humans rank answers; model learns the style.

## New Python in this lesson
| Python | What / Java equivalent |
|---|---|
| `zip(a, a[1:])` | walk neighbour pairs: `(a0,a1), (a1,a2)…` |
| `enumerate(xs, start=1)` | `(index, item)` pairs — indexed `for` loop |
| `Counter(...).most_common(1)` | `[(item, count)]` of the top item; ties keep first-seen order |
| `d.setdefault(k, Counter())` | `map.computeIfAbsent(k, ...)` |
| `str \| None` | return type that may be `None` — like a nullable / `Optional<String>` |
| `math.ceil`, `math.exp` | `Math.ceil`, `Math.exp` |
| `reversed(xs)` | iterate backwards, no copy |

## Do it
1. `uv run python 02_llm_fundamentals/2_1_how_llms_work/examples.py`
2. Fill each `...` in `exercises.py`.
3. `uv run python 02_llm_fundamentals/2_1_how_llms_work/exercises.py` → all PASS.

## Done when
- [ ] All exercises PASS.
- [ ] You can explain: token, BPE, logits, softmax, context window,
      and why the model has no memory of its own.
