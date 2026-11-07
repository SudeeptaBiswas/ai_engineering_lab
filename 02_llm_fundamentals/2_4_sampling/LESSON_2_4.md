# 2.4 Sampling: temperature, top_p, max tokens (~1 h)

Read this, run [examples_2_4_1_by_hand.py](examples_2_4_1_by_hand.py) (no Ollama) and
[examples_2_4_2_ollama.py](examples_2_4_2_ollama.py), then solve [exercises_2_4.py](exercises_2_4.py).

All numbers **measured on BISWAS** (i5-1135G7, 11.7 GB RAM, no GPU),
Ollama 0.40.14, qwen3:1.7b, 2026-11-07, one run each unless a range is given.

## The question of this lesson
You saw two odd things already:
- **2.1**: the greedy loop always took the top word, so it wrote the same
  boring line every time.
- **2.3**: the same request sent twice can give two different answers.
  Asked "my favourite colour?" with no history, it said "Blue." (a guess).

Both come from one step: **how the next token is picked**. This lesson
shows that step, and the four knobs that control it.

## Java → Python map
| Java | Python |
|---|---|
| `new Random(42)` | `random.Random(42)` |
| weighted pick: loop over cumulative sums | `rng.choices(words, weights=probs)[0]` |
| `list.sort(comparing(...).reversed())` | `sorted(items, key=..., reverse=True)` |
| `list.subList(0, k)` | `items[:k]` |
| `new HashSet<>(list).size()` | `len(set(items))` |
| `Integer` that may be `null` | `int \| None` |

## 1. Same question, five answers
Five calls, same prompt: *"Invent an unusual name for a pet cat."*

| Setting | Answers |
|---|---|
| temperature 0 | Zephyrclaw, Zephyrclaw, Zephyrclaw, Zephyrclaw, Zephyrclaw |
| temperature 0.6 (default) | Squidlepus, Squidooch, Whiskerwisp, Zestraught, Zephyrclaw |

Why? Remember 2.1, part 4: the model never "chooses" a word. It outputs
**odds** for every token (softmax: cat 63%, mat 23%, rat 14%). Something
else then picks one. That pick is **sampling**:
- always the top one = **greedy** (2.1) → Zephyrclaw every time
- a weighted random pick (like a loot table in a game) → a new name each time

Zephyrclaw is the model's top choice. The others are the less likely
choices it picked on other calls.

## 2. Temperature: how bold the pick is
Same cat / mat / rat scores as 2.1. Temperature is one division
(score ÷ T) right before the softmax you already wrote:

| T | cat | mat | rat | Feels like |
|---|---|---|---|---|
| 0.2 | 0.99 | 0.01 | 0.00 | almost greedy: safe, repeats |
| 1.0 | 0.63 | 0.23 | 0.14 | the model's own odds |
| 2.0 | 0.48 | 0.29 | 0.23 | flatter: rare words come up often |

T = 0 would divide by zero. In Ollama it acts greedy (same answer 10/10).

**Where you will set it**:
| Job | T | Why | Lesson |
|---|---|---|---|
| JSON output | 0 | one "creative" brace and parsing fails | 3.2 |
| tool calls | 0 | the tool name must match exactly | 3.3 |
| RAG answers | low | stick to the found text, don't invent | 4.6, 4.10 |
| LLM-as-judge | 0 | same answer → same score every run | 5.3 |
| chatbot small talk | default | some variety feels human | 2.6 |
| names, ideas | 1+ | you *want* surprises | 3.1 |

## 3. top_k and top_p: cut off the junk first
At T 1.5, one of ten "names" came back as `'Zigguratův Nárit\n\n(Note'`.
Where does junk like that come from? qwen3 has 151 936 tokens
(`ollama show qwen3:1.7b --verbose`).
Each odd one has a tiny chance, but together they add up, and a high T
makes them bigger. **top_k / top_p remove that tail before the pick.**
Measured: T 1.5 + top_p 0.1 → Zephyrclaw x5, calm again.

With cat 0.63, mat 0.23, rat 0.14:
- **top_k 2** = keep the 2 best → cat 0.73, mat 0.27. Java/SQL view:
  `ORDER BY prob DESC LIMIT 2`. `top_k 1` = greedy.
- **top_p 0.8** = keep the best ones until they cover 80% → cat (0.63) +
  mat (0.86, stop). SQL view: a running total cut-off. If the model is sure,
  1 word is enough. If many words are close, the group gets bigger.

You have used these since 2.3 without knowing it. qwen3's defaults
(`ollama show qwen3:1.7b --parameters`): **temperature 0.6, top_k 20,
top_p 0.95**. Send nothing and you get these.

## 4. Seed: random, but repeatable
The 2.3 check `"green" in ask(COLOUR)` passes because the history makes
"green" the obvious answer. With an open prompt (section 1) the same kind
of test would be **flaky**: it passes on some runs and fails on others. Fix:
`"seed": 42`. It works like `new Random(42)` in a JUnit test: same seed
+ same settings + same prompt → same answer.
Measured: T 1.5 + seed 42 → Fizzluff x5. Tested on one PC only.
Where used next: repeatable test sets (5.1), judge scores (5.3), and
replaying a broken agent run (6.11).

## 5. The prompt sets the odds; temperature only reshapes them
Ten calls each at T 1.5:
- "Invent **a** name for a pet cat." → 6 different, "Whiskers" 4 times.
- "Invent an **unusual** name…" → 9 different.
- "Name a colour." → only Red / Blue. A sure model barely moves.

So when answers are too samey or too wild, **fix the prompt first**
(3.1), then touch T.

## 6. num_predict: a hard cut, not "be short"
2.3 set `num_predict` to keep tests fast. It cuts off the answer. It does
not tell the model to be short. The model writes as usual and is stopped
mid-sentence:
`num_predict 12` → `'Once upon a time, in a quiet village nestled between rolling'`
→ `done_reason: "length"` (2.3). Links:
- 2.1 context window: prompt + answer must fit, so this also reserves room.
- 2.6 chatbot: a cut answer looks broken → high limit + "Answer briefly"
  in the system prompt.

## 7. One-line summary per knob
| Knob | Met before | Used next |
|---|---|---|
| temperature | 2.1 greedy, 2.3 random answers | 3.2, 3.3, 4.6, 5.3 |
| top_k / top_p | silent defaults in 2.3 | when raising T |
| seed | `random.Random` | 5.1, 5.3, 6.11 |
| num_predict | 2.3 `done_reason` | 2.6 chatbot |

## 8. Exercises
[exercises_2_4.py](exercises_2_4.py): 8 functions, 14 checks. Checks 1–11 are by
hand, no Ollama. 12–14 call qwen3:1.7b. Reference: 14/14 in 6.9–8.4 s (3 runs).
