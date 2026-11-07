# 2.4 Sampling: temperature, top_p, max tokens (~1 h)

Read this, run [examples_2_4_1_by_hand.py](examples_2_4_1_by_hand.py) (no Ollama) and
[examples_2_4_2_ollama.py](examples_2_4_2_ollama.py), then solve [exercises_2_4.py](exercises_2_4.py).
Why now: 2.1 ended with "always taking the top word = greedy, boring".
This is the fix, and the knobs every LLM API has (Ollama, OpenAI, Claude).

All numbers **measured on BISWAS** (i5-1135G7, 11.7 GB RAM, no GPU),
Ollama 0.40.14, qwen3:1.7b, 2026-11-07, one run each unless a range is given.

## Java → Python map
| Java | Python |
|---|---|
| `new Random(42)` | `random.Random(42)` |
| weighted pick: loop over cumulative sums | `rng.choices(words, weights=probs)[0]` |
| `list.sort(comparing(...).reversed())` | `sorted(items, key=..., reverse=True)` |
| `list.subList(0, k)` | `items[:k]` |
| `new HashSet<>(list).size()` | `len(set(items))` |
| `Integer` that may be `null` | `int \| None` |

## 1. The model gives odds, you pick
Each step the model scores every token (logits). Softmax turns scores into
odds (2.1). **Sampling** = how one token is picked from those odds.
Greedy = always the top one. Sampling = a weighted random pick.

## 2. Temperature: divide the scores by T before softmax
Scores cat 2.0, mat 1.0, rat 0.5 (example part 1):

| T | cat | mat | rat | Effect |
|---|---|---|---|---|
| 0.2 | 0.99 | 0.01 | 0.00 | almost greedy |
| 1.0 | 0.63 | 0.23 | 0.14 | the model's own odds |
| 2.0 | 0.48 | 0.29 | 0.23 | flatter: rare words more often |

- **T = 0** would divide by zero. In Ollama it acts greedy (same answer 10/10).
- Low T: facts, code, JSON, tests. High T: brainstorming, names, stories.

## 3. top_k and top_p: drop the long tail first
- **top_k = k**: keep the k most likely tokens, rescale to 1. `top_k 1` = greedy.
- **top_p = p** ("nucleus"): keep the smallest top group whose odds add up
  to p. A sure answer → group of 1; many close ones → big group.
  cat 0.63, mat 0.23, rat 0.14 with p 0.8 → cat + mat (0.86), rat is dropped.

qwen3's defaults (`ollama show qwen3:1.7b --parameters`):
**temperature 0.6, top_k 20, top_p 0.95**. Send nothing → you get these.

## 4. Seed: random, but repeatable
`"seed": 42` fixes the random numbers. Same seed + settings + prompt →
same answer, even at T 1.5. Use it in tests and bug reports.
Same idea as `random.Random(7)` in part 1. Tested on one PC only.

## 5. Measured: "Invent an unusual name for a pet cat."
Five calls each, one-word system prompt (example part 2, 21–31 s total):

| Options | Different answers out of 5 |
|---|---|
| temperature 0 | 1 (Zephyrclaw x5) |
| temperature 0.6 (default) | 5 |
| temperature 1.5 | 5 ("Whiskerclaw Conundrum": not one word any more) |
| 1.5 + seed 42 | 1 (Fizzluff x5) |
| 1.5 + top_k 1 | 1 (Zephyrclaw = the T 0 answer) |
| 1.5 + top_p 0.1 | 1 (Zephyrclaw) |

The prompt matters as much as T. Ten calls each at T 1.5:
- "Invent **a** name for a pet cat." → 6 different, Whiskers 4 times.
- "Invent an **unusual** name…" → 9 different, one broke the rule:
  `'Zigguratův Nárit\n\n(Note'`.
- "Name a colour." → only Red / Blue. A sure model barely moves, even at 1.5.

## 6. num_predict: a hard cut, not "be short"
The model does not know the limit; it is stopped mid-sentence:
`num_predict 12` → `'Once upon a time, in a quiet village nestled between rolling'`
(`done_reason: "length"`, lesson 2.3). Want short? Ask in the prompt.

## 7. Exercises
[exercises_2_4.py](exercises_2_4.py): 8 functions, 14 checks. Checks 1–11 are by
hand, no Ollama. 12–14 call qwen3:1.7b. Reference: 14/14 in 6.9–8.4 s (3 runs).
