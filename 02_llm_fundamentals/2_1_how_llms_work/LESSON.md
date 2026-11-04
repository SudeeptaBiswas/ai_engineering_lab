# 2.1 How LLMs work: tokens, context window (~1.5 h)

Read this, run the 4 example files in order —
[examples_1_tokens.py](examples_1_tokens.py), [examples_2_bpe.py](examples_2_bpe.py),
[examples_3_predict.py](examples_3_predict.py), [examples_4_context.py](examples_4_context.py) —
then solve [exercises.py](exercises.py).
No real model yet. We build tiny toy versions in plain Python.
Ollama (a real model on your PC) comes in 2.2.

**How to read the code:** lines between `# --- explicit start ---` and
`# --- explicit end ---` are the long, step-by-step way. The `# concise:`
comment right after shows the same thing in short Python style.

## 1. What an LLM really does
Think of **IntelliJ autocomplete**. You type `list.` and it suggests `add`.
An LLM does the same thing, but for any text, and it is much better at it.

It only does one thing: **look at the text so far, guess the next piece.**
To write a full answer, it runs in a loop:

```
"The cat"          -> guess "sat"
"The cat sat"      -> guess "on"
"The cat sat on"   -> guess "the"   ... until it guesses "stop"
```
That loop is the whole trick. It is called *autoregressive* generation.

## 2. Tokens = the pieces the model reads
The model cannot read letters. It reads **numbers**.
So text is cut into pieces (**tokens**), and each piece gets an id.

Java view: a compiler's **lexer** cuts `int x = 5;` into tokens first.
A tokenizer does the same for normal text. The list of all pieces is the
**vocabulary** — like a `Map<String, Integer>`:

```
"unbelievable"  ->  ["un", "believ", "able"]  ->  [403, 9182, 512]
```
- Common words are one token: `"the"`. Rare words are split into parts.
- Unknown word? Still works — it is split into smaller known parts.
- Rough rule for English: **1 token ≈ 4 characters ≈ ¾ of a word.**
  Other languages and code often need more tokens.

**How the pieces are chosen (BPE):** start with single letters. Find the
two neighbours that appear together most often (`t`+`h`). Glue them
into one piece (`th`). Repeat many thousands of times. You will do one
step of this in the exercises.

**Why you care:** price, speed and limits are all counted in tokens.
Like paying per MB on a cloud bill — longer prompts cost more.

## 3. Context window = how much the model can see at once
Every call has a hard limit of tokens. It must fit **everything**:
system prompt + chat history + new question + the model's own answer.
Limits go from a few thousand to over a million tokens, per model.

Java view: like a **max request body size** on a server. Send more and it fails
(or the old part is cut off).

## 4. The model has no memory
Each call is like a **stateless REST call**. The model forgets you right away.
So how does ChatGPT "remember"? **Your code sends the whole chat again,
every time.**

```
Call 1 sends: [system, user1]
Call 2 sends: [system, user1, answer1, user2]
Call 3 sends: [system, user1, answer1, user2, answer2, user3]   <- keeps growing
```
When it gets too big for the window, drop the **oldest** messages.
Keep the system message (it holds the rules). Java view: like **log
rotation** — old lines go, the config stays. Your `assistant/` v1 does
this in topic 2.6.

Too much data to fit at all (e.g. 500 PDFs)? Send only the useful parts.
That is **RAG** (phase 04).

## 5. From scores to a choice
For the next piece, the model gives a raw score to **every** token in the
vocabulary. These scores are called **logits**.

**Softmax** turns scores into percentages that add up to 100%:
```
scores:  cat 2.0   mat 1.0   rat 0.5
softmax: cat 63%   mat 23%   rat 14%
```
Always taking the top one = *greedy*. Picking with some randomness = *sampling*
(topic 2.4).

**Hallucination:** the model picks what *sounds* right, not what *is* right.
Like autocomplete suggesting a method that does not exist. Always check facts.

## 6. How a chat model is made (short)
1. **Pre-training:** read huge amounts of text, learn to guess the next piece.
2. **Instruction tuning:** learn from (question, good answer) examples.
3. **Preference tuning:** people rank answers; the model learns which they like.

## New Python in this lesson
| Python | What it does | Java |
|---|---|---|
| `zip(a, a[1:])` | pairs of neighbours `(a0,a1), (a1,a2)…` | loop with `i` and `i+1` |
| `enumerate(xs, start=1)` | gives `(index, item)` | `for (int i = 1; ...)` |
| `Counter(xs).most_common(1)` | top item + its count; a tie keeps the first one seen | `Map<K,Integer>` + sort |
| `d.setdefault(k, Counter())` | get, or create if missing | `map.computeIfAbsent(k, ...)` |
| `str \| None` | may return `None` | nullable / `Optional<String>` |
| `math.ceil`, `math.exp` | round up, e to the power | `Math.ceil`, `Math.exp` |
| `reversed(xs)` | loop from the end | `for (int i = n-1; i >= 0; i--)` |

## Do it
1. `uv run python 02_llm_fundamentals/2_1_how_llms_work/examples_1_tokens.py`
   then `examples_2_bpe.py`, `examples_3_predict.py`, `examples_4_context.py`
2. Fill each `...` in `exercises.py`.
3. `uv run python 02_llm_fundamentals/2_1_how_llms_work/exercises.py` → all PASS.

## Done when
- [ ] All exercises PASS.
- [ ] You can explain, in your own words: token, BPE, context window,
      logits, softmax, and why the model has no memory.
