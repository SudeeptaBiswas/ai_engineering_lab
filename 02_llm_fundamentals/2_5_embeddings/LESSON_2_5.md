# 2.5 Embeddings + similarity (~2 h)

Read this, run [examples_2_5_1_cosine.py](examples_2_5_1_cosine.py) (no Ollama) and
[examples_2_5_2_ollama.py](examples_2_5_2_ollama.py), then solve
[exercises_2_5_1_cosine.py](exercises_2_5_1_cosine.py) and [exercises_2_5_2_ollama.py](exercises_2_5_2_ollama.py).

All numbers **measured on BISWAS** (i5-1135G7, 11.7 GB RAM, no GPU),
Ollama 0.40.14, nomic-embed-text, 2026-11-08, one run each unless a range is given.

Setup (done on BISWAS): `ollama pull nomic-embed-text` → 274 MB, 137M parameters.

## The question of this lesson
A user types *"I can't log in to my account"*. Your notes contain
*"To reset your password, click 'Forgot password' on the login page."*
That is the right answer, but how does code find it?

Keyword match (like SQL `LIKE '%log in%'`) fails. Shared words: only `to`.
"log in" vs "login", "account" vs "password": same meaning, different words.

This is the core problem of RAG (phase 04): **find text by meaning, not
by spelling**. This lesson is the tool for it.

## Java → Python map
| Java | Python |
|---|---|
| `double[]` | `list[float]` |
| `for (i...) total += a[i] * b[i]` | `sum(x * y for x, y in zip(a, b))` |
| `Math.sqrt(x)` | `math.sqrt(x)` |
| `set.retainAll(other)` | `set_a & set_b` |
| `List<double[]>` | `list[list[float]]` |
| `a, b, c = arr[0], arr[1], arr[2]` | `a, b, c = arr` (unpack) |
| Javadoc `@param` / `@return` / `@throws` | docstring `Args:` / `Returns:` / `Raises:` |

## 1. An embedding = text turned into numbers by meaning
Send text to `/api/embed`, get back a list of numbers (a **vector**):

```
"The cat sat on the mat." → [0.05, 0.062, -0.117, -0.024, 0.052, ...]  768 numbers
```

- Always 768 numbers for this model, one word or one page.
- Texts with similar meaning get similar numbers. That's what the model
  was trained for.
- Link to 2.1: there, text became token **ids**, one number per piece.
  An id carries no meaning (the ids for "cat" and "kitten" are unrelated).
  An embedding is many numbers for the whole text, chosen so meaning shows.
- Measured: `qwen3:1.7b` can't do it here → HTTP 501 *"This server does
  not support embeddings"*. You need a separate embedding model.

## 2. Picture it: arrows on a map
Two numbers per text, so you can draw it: [about animals, about money].

| Text | Vector |
|---|---|
| animal | [0.9, 0.1] → points east |
| kitten | [0.8, 0.2] → nearly the same way |
| invoice | [0.1, 0.9] → points north |

**Similar meaning = arrows pointing the same way.** 768 numbers are the
same idea with 768 directions instead of 2. You can't draw it, but the
maths is identical.

## 3. Cosine similarity: how alike two directions are
```
dot(a, b)    = a0*b0 + a1*b1 + ...         (Java: a for loop)
norm(a)      = sqrt(dot(a, a))             (arrow length, Pythagoras)
cosine(a, b) = dot(a, b) / (norm(a) * norm(b))
```
| Cosine | Means | Toy example |
|---|---|---|
| 1 | same direction | animal vs kitten: 0.99 |
| 0 | right angle, unrelated | east vs north |
| -1 | opposite | east vs west |

**Why divide by the lengths?** A long note and a short note on the same
topic point the same way but have different lengths. `dot` changes with
length (0.74 vs 7.40 in part 1). `cosine` doesn't (1.00).

Shortcut: nomic vectors already have length 1.0 (measured), so
cosine = dot. Chroma and numpy code often rely on this (4.1, 4.4).

## 4. Real scores
| Pair | Cosine |
|---|---|
| cat vs kitten | 0.84 |
| cat vs dog | 0.60 |
| happy vs sad | 0.66 |
| I love this movie vs I hate this movie | 0.69 |
| cat vs invoice | 0.40 |

What this shows:
- **Unrelated is ~0.3–0.45, not 0.** Read scores as "higher than the
  others", never as a fixed meaning. Don't hard-code "0.5 = match".
- **love vs hate scores high.** Embeddings measure *what it's about*
  (a movie review), not *whether it's positive or true*. That's why RAG
  still needs the LLM to read the found text (4.6).

## 5. Search = score all, sort, keep top k
The question from the top, against 5 notes:

| Query | Best note | Score | Next best |
|---|---|---|---|
| I can't log in to my account | reset password | 0.68 | 0.42 |
| When do I get my bill? | invoices by email | 0.58 | 0.44 |

That's a search engine in 3 steps:
1. Embed every note **once**, keep the vectors (later: a vector DB, 4.4).
2. Embed the question.
3. Cosine against each note, sort best first, keep the top k. Same
   `ORDER BY ... LIMIT k` idea as top_k in 2.4.

## 6. Things that bite
- **Same model for notes and question.** Vectors from two models live in
  different "maps". Comparing them gives nonsense scores, with no error.
- **Batch your calls.** `"input"` takes a list. 5 notes: 5 calls 1.34–1.92 s,
  1 call 0.38–0.60 s (2 runs). First call also loads the model (~0.8 s).
- **Different lengths = a bug.** `zip` stops at the shorter list without
  an error, so you get a wrong score. The exercise makes `dot` raise.
- **Prefixes.** nomic's docs ask for `search_query: ` / `search_document: `
  in front of texts. On these 5 notes it was mixed: the login gap shrank
  (0.26 → 0.14), the bill gap grew (0.14 → 0.15). Not used here. Tested
  properly with an eval set in 4.1 + 5.1.

## 7. Where it is used next
| Lesson | Uses |
|---|---|
| 4.1 RAG by hand | chunk notes, embed, this exact search with numpy |
| 4.4 Chroma | stores the vectors + does the search for you |
| 4.7 Hybrid search | keyword (BM25) + vectors: each fixes the other's misses |
| 5.x evals | "is the answer close in meaning to the expected one?" |

## 8. Exercises
Two files, 6 functions, 17 checks. [Part 1](exercises_2_5_1_cosine.py): 4 functions,
10 checks by hand, no Ollama. [Part 2](exercises_2_5_2_ollama.py): 2 functions, 7 checks,
calls nomic-embed-text and imports part 1 (1.5). Edge cases are checked:
different lengths, zero vector, k 0, k too big, empty input, wrong model.
Reference: 17/17. Part 1 0.19 s; part 2 2.4–3.7 s (2 runs), 20.6 s if the
model is not loaded yet.
