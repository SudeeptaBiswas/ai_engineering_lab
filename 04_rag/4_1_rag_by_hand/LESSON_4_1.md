# 4.1 RAG by hand: chunk, embed, search with numpy (~5 h)

Basic level, first topic of phase 04. Uses 2.5 (embeddings, cosine),
2.6 (context size, silent cut), 3.2 (system rules). Next: 4.2 PDFs,
4.3 better chunking, 4.4 Chroma (a database that does the search for you).

All numbers **measured on BISWAS** (CPU only), Ollama 0.40.16,
qwen3:1.7b + nomic-embed-text, temperature 0, seed 42, 2026-11-15.
Scores were the same in 2 runs; times vary by ~20%.

## The problem
A customer asks your bot: *"How long does the password reset link work?"*
The answer is in your company handbook: **15 minutes**.
The model has never seen your handbook. It answers:
*"The password reset link typically expires after 10 minutes."*
Wrong, and it sounds sure (2.1: it picks what sounds right).
Without the handbook it got **1 of 12** questions right.

Our documents are made up, so the model can't know them:
- [handbook_4_1.md](handbook_4_1.md): 13 sections (accounts, refunds, sync...).
- [release_notes_4_1.md](release_notes_4_1.md): 108 app versions.

Together: 25 781 characters = **7 217 tokens**.

## Goal
Make the model answer questions from **our own documents**: right, and fast.
Target: from 1/12 right to 11/12 right, in about 5 s per question.

## How we get there
The documents are too big to send with every question.
So for each question we **find the few pieces that fit**,
and send **only those** to the model.

This is called **RAG** (retrieval-augmented generation):
- **Retrieve**: find the pieces (the 2.5 search, now on real documents).
- **Augment**: put them in the prompt.
- **Generate**: the model writes the answer from them.

## Steps
```
ONCE (when the documents change):
  1. Cut the documents into chunks.           "## Refunds\nWithin 14 days..."
  2. Turn every chunk into a vector.          122 chunks -> a 122 x 768 table
PER QUESTION:
  3. Turn the question into a vector.         "Can I get my money back?" -> 768 numbers
  4. Score every chunk, keep the best 3.      0.64 Refunds, 0.55 Billing, 0.50 ...
  5. Send rules + 3 chunks + question.        -> "Refunds are possible within 14 days."
```
Step 2 took **10.4–13.4 s**, once. Steps 3–5 take one small embed
call + one chat call per question.
The "3" in step 4 is called **top_k**: how many of the best chunks we keep.

## Your path through this lesson
1. Read sections 1–3. Run part 1.
2. Read section 4. Run part 2.
3. Read section 5. Run part 3.
4. Do the exercises: write the 6 functions yourself.

## Java → Python map
| Java | Python |
|---|---|
| `double[][]` | `np.ndarray`, shape `(rows, columns)` |
| loop: `for each row: dot(row, q)` | `matrix @ question_vector` (one line, all rows) |
| sort indices by value, high first | `np.argsort(-scores)` |
| Lucene / Elasticsearch index | a table of chunk vectors in RAM (4.4: Chroma) |

## 1. Why not send everything?
If your text is small, sending it all is fine.
One handbook alone (1 540 tokens): **9/9 right** (*).
Both files are bigger.

**Context size** = the most tokens the model reads in one call (2.6).
Ollama calls it `num_ctx`; the default is 4096. Here is what happened:

| Way | Right | Time (12 questions) | Tokens the model read |
|---|---|---|---|
| model alone | 1/12 | 22–38 s | 49–56 |
| all text, default context 4096 (*) | **5/12** | 351 s | **2 050** (cut!) |
| all text, `num_ctx` 16384 (*) | 11/12 | 240 s | 7 217 |
| **RAG**, best 3 chunks | **11/12** | 42–62 s | 213–493 |

(*) Measured once on 2026-11-15 with a one-off script that was not kept.
Part 3 repeats the other rows, and the 4096 row on 2 questions only
(each takes ~30 s).

- **4096 = silent cut.** Ollama read only 2 050 of 7 217 tokens.
  No error. Answers went wrong, and the rules got lost too.
- **16384 works, but slow.** Every question reads all 7 217 tokens:
  4–5x slower than RAG. A 500-page manual won't fit at all.
- **RAG: same score, 15–34x fewer tokens.** More documents means more
  chunks to search, not a longer prompt.

## 2. Chunking: how you cut decides what you find
A **chunk** is one piece of a document. Two ways to cut the same text:

| Chunks | Count | Avg size | Right chunk 1st | in top 3 | Answers right |
|---|---|---|---|---|---|
| every 500 characters, overlap 100 | 65 | 495 chars | 10/12 | 12/12 | 10/12 |
| by `## ` headings | 122 | 209 chars | **12/12** | 12/12 | **11/12** |

Counts and sizes: part 1 prints them. The "right" columns: measured once
(*), same one-off script as section 1.

- **By size** cuts anywhere: mid-sentence, or two versions in one piece.
  Example: "dark mode" was found, but next to version 8.6.1.
  The model answered **8.6.1**. Wrong: it's 7.4.0.
- **By heading** follows the meaning: one section = one topic.
  Rule: if the document has structure, use it. 4.3 compares more ways.
- **Overlap** = each piece repeats the last 100 characters of the one
  before. So a sentence cut at a border is whole in one of the two.
  Example, size 4, overlap 1: `"abcdefghij"` → `"abcd"`, `"defg"`, `"ghij"`.

## 3. Search with numpy
2.5 scored each note in a Python loop. numpy scores all chunks in one line:
```python
scores = chunk_vectors @ question_vector    # (122, 768) @ (768,) -> 122 scores
best_first = np.argsort(-scores)            # row numbers, highest score first
```
- `@` = one dot product per row. One line instead of a loop.
- nomic vectors have length 1.0 (checked: all 122). So dot product =
  cosine (2.5). No dividing needed.
- Example, real top 3 for "Can I get my money back?":
  **0.64 Refunds**, 0.55 Billing, 0.50 Account deletion.
  Not one word in common with "Refunds", and still found first.

> ▶ **Now run part 1** (needs Ollama, ~15 s): documents, chunks, search.
> `uv run python 04_rag/4_1_rag_by_hand/examples_4_1_1_search.py`

## 4. Is numpy fast enough?
Same scores, two ways, on random vectors. Only the scoring is timed
(no sort), after one warm-up call: numpy's first call took 12.6 ms once.

| Chunks | numpy | Python loop |
|---|---|---|
| 122 | 0.025–0.042 ms | 3–4 ms |
| 20 000 | 5.9–7.2 ms | 589–684 ms |

(6 runs, BISWAS, 2026-11-15. About 100x faster.)

Up to ~100 000 chunks, a numpy table is a fine "vector database".
Beyond that: 4.4.

> ▶ **Now run part 2** (no Ollama, ~3 s): numpy vs loop.
> `uv run python 04_rag/4_1_rag_by_hand/examples_4_1_2_speed.py`

## 5. Things that bite
- **Found is not answered.** "I paid three weeks ago. Can I still get a
  refund?" The Refunds chunk (14 days) was found first. But the model
  said "I don't know": it didn't work out that 3 weeks > 14 days.
  Search finds text; the model still has to think (3.1 step by step helps).
- **"I don't know" is a rule you must write.** Without it, the model
  guesses (the "alone" answers above). 4.10 measures this.
- **Same embedding model** for chunks and question (2.5). Mixed models
  give wrong scores, and no error.
- **Embed once, keep the vectors.** Embedding 122 chunks again for each
  question costs 10+ s each time. 4.4 saves them to disk.
- **Check answers your own way.** "Right" here = the answer has the
  expected words ("15 minutes"). Simple, but honest and repeatable.
  5.1 builds a real test set.

> ▶ **Now run part 3** (needs Ollama, ~3 min): 12 questions, alone vs RAG vs all text.
> `uv run python 04_rag/4_1_rag_by_hand/examples_4_1_3_answer.py`

## 6. Where it is used next
| Lesson | Uses |
|---|---|
| 4.2 PDFs | the same steps, text taken from PDF files |
| 4.3 Chunking | more ways to cut, measured like section 2 |
| 4.4 Chroma | stores chunks + vectors, does the `@` + sort for you |
| 4.6 assistant v3 | these steps inside the chat app |
| 4.10 Citations | show which chunk an answer came from; "I don't know" |
| 5.1 Eval set | the 12 questions, grown into a real test set |

## Exercises: write the RAG steps yourself
**Goal:** the same steps as the examples, in
[rag_4_1.py](rag_4_1.py), until all 31 tests pass.
Each function has a `How:` list in its docstring. The tests are the spec:
[exercises_4_1_1_chunks.py](exercises_4_1_1_chunks.py) (no Ollama),
then [exercises_4_1_2_search.py](exercises_4_1_2_search.py).
Follow [CODE_STYLE.md](../../docs/CODE_STYLE.md): clear names, one step
per line, `@debug` + `log.debug` for start / steps / result.

| # | Function | Goal | Example: in → out | Tests |
|---|---|---|---|---|
| 1 | `split_by_headings` | one chunk per `## ` section | `"# T\n## A\nx\n## B\ny"` → `["# T", "## A\nx", "## B\ny"]` | 8 |
| 2 | `split_by_size` | pieces of fixed size, with overlap | `"abcdefghij"`, 4, 1 → `["abcd", "defg", "ghij"]`; overlap 4 → ValueError | 10 |
| 3 | `embed_texts` | all texts → vectors, in ONE call | `["a", "b"]` → table of shape (2, 768) | 2 + 1 real |
| 4 | `find_top_chunks` | best row numbers first | scores `[0.0, 1.0, 0.8]`, top 2 → `[1, 2]` | 7 + 1 real |
| 5 | `build_rag_messages` | rules + chunks, then the question | → `[{system: rules + chunks}, {user: question}]` | 1 |
| 6 | `answer_question` | steps 3–5 together | "How long does the password reset link work?" → "...15 minutes." | 1 real |

Edge cases the tests check (so you don't have to guess):
- Empty text → `[]`. Text with no heading → one chunk. Empty chunks are skipped.
- `split_by_size`: `chunk_size` must be > 0, and `overlap` from 0 to
  `chunk_size - 1`. Anything else → `ValueError` (else the loop never ends).
- `embed_texts([])` → `ValueError`, before any call to Ollama.
- `find_top_chunks`: `top_k` bigger than the chunk count → all rows;
  0 or less → `[]`; equal scores keep their order (`kind="stable"`); plain `int`, not numpy's.

Run:
```
uv run pytest 04_rag/4_1_rag_by_hand -v
```
Ollama off? Add `-m "not ollama"`. Reference solution, measured:
**31 passed in 5.6–9.0 s** (3 runs, 2026-11-15; first run loads the models),
28 + 3 deselected in 0.31 s, pyright 0. The stubs: 28 failed, 3 errors
(the real tests' setup calls `embed_texts`).
