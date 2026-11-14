# 4.1 RAG by hand: chunk, embed, search with numpy (~5 h)

Basic level, first topic of phase 04. Uses 2.5 (embeddings, cosine),
2.6 (context size, silent cut), 3.2 (system rules). Next: 4.2 PDFs,
4.3 better chunking, 4.4 Chroma (a vector database does part 3 for you).

All numbers **measured on BISWAS** (CPU only), Ollama 0.40.16,
qwen3:1.7b + nomic-embed-text, temperature 0, seed 42, 2026-11-15.
Scores were the same in 2 runs; times vary by ~20%.

## The question of this lesson
A customer asks your bot: *"How long does the password reset link work?"*
The answer is in your company handbook: **15 minutes**. The model has never
seen your handbook. It answers: *"The password reset link typically expires
after 10 minutes."* Wrong, and it sounds sure (2.1: it picks what sounds
right). Without the handbook it got **1 of 12** questions right.

The documents here are made up, so the model can't know them:
[handbook_4_1.md](handbook_4_1.md) (13 sections) and
[release_notes_4_1.md](release_notes_4_1.md) (108 app versions).
Together: 25 781 characters = **7 217 real tokens**.

**RAG** (retrieval-augmented generation) = before asking the model, *find*
the few pieces of your documents that fit the question and put only those
in the prompt. Retrieve (2.5 search) + augment (the prompt) + generate.

## Java → Python map
| Java | Python |
|---|---|
| `double[][]` | `np.ndarray`, shape `(rows, columns)` |
| loop: `for each row: dot(row, q)` | `matrix @ question_vector` (one line, all rows) |
| sort indices by value, descending | `np.argsort(-scores)` |
| Lucene / Elasticsearch index | a matrix of chunk vectors in RAM (4.4: Chroma) |
| `String.split` on a marker line | `split_by_headings` (you write it) |

## 1. Why not paste everything into the prompt?
Just one handbook (1 540 tokens) pasted in: **9/9 right**. If your text
fits, pasting it is fine. Real documents don't fit. With both files:

| Way | Right | Time (12 questions) | Prompt tokens |
|---|---|---|---|
| model alone | 1/12 | 22–38 s | 49–56 |
| all text, default context 4096 | **5/12** | 351 s | **2 050** (cut!) |
| all text, `num_ctx` 16384 | 11/12 | 240 s | 7 217 |
| **RAG**, top 3 chunks | **11/12** | 48–62 s | 213–493 |

- At 4096 Ollama **cut the prompt silently** (2.6): it read 2 050 of 7 217
  tokens. No error. Answers went wrong and lost the rules (one talked
  about "Obsidian" and used Markdown headers).
- A bigger context works, but every question reads all 7 217 tokens:
  4–5x slower than RAG on this CPU. A 500-page manual won't fit at all.
- RAG: same score, 15–34x fewer tokens, and it scales: more documents
  = more chunks to search, not a longer prompt.

## 2. The RAG steps
```
ONCE:      documents -> chunks -> embed every chunk -> matrix (122 x 768)
PER ASK:   question -> embed -> scores = matrix @ question -> top 3 rows
           -> prompt: rules + those 3 chunks + question -> model -> answer
```
Embedding the 122 chunks took **10.4–13.4 s**, once. Each question then
needs one small embed call + one chat call.

## 3. Chunking: how you cut decides what you find
Two ways, same text:

| Chunks | Count | Avg size | Right chunk 1st | in top 3 | Answers right |
|---|---|---|---|---|---|
| every 500 characters, overlap 100 | 65 | 495 chars | 10/12 | 12/12 | 10/12 |
| by `## ` headings | 122 | 209 chars | **12/12** | 12/12 | **11/12** |

- A 500-character piece starts and stops anywhere: mid-sentence, two
  release versions in one piece. "Dark mode" was found, but next to
  version 8.6.1, so the model answered **8.6.1** (wrong; it's 7.4.0).
- Headings follow the meaning: one section = one topic. Use the
  document's own structure when it has one. 4.3 compares more ways.
- **Overlap**: a piece repeats the last 100 characters of the one before,
  so a sentence cut at a border is whole in one of the two.

## 4. Search with numpy
2.5 scored notes in a Python loop. numpy does all rows in one step:
```python
scores = chunk_vectors @ question_vector    # (122, 768) @ (768,) -> (122,)
best_first = np.argsort(-scores)            # row numbers, highest score first
```
- nomic vectors have length 1.0 (measured again: 1.000 for all 122), so
  dot = cosine. No dividing needed.
- `@` = matrix times vector = one dot product per row.

| Chunks | numpy | Python loop |
|---|---|---|
| 122 | 0.2–0.3 ms | 6–10 ms |
| 20 000 | 7–13 ms | 1 326–1 546 ms |

Measured on random vectors (part 1). Up to ~100 000 chunks, a numpy
matrix is a fine "vector database". Beyond that: 4.4.

Real top-3 for "Can I get my money back?" (no word in common with the
heading): **0.64 Refunds**, 0.55 Billing, 0.50 Account deletion.

> ▶ **Now run part 1** (needs Ollama, ~15 s).
> `uv run python 04_rag/4_1_rag_by_hand/examples_4_1_1_search.py`

## 5. Things that bite
- **Found is not answered.** "I paid three weeks ago. Can I still get a
  refund?": the Refunds chunk (14 days) was found first, but the model
  said "I don't know". It didn't work out 3 weeks > 14 days. Search
  finds text; the model still has to reason (3.1 step-by-step helps).
- **"I don't know" is a rule you must write.** Without it, a model fills
  gaps with guesses (the "alone" answers above). 4.10 measures it.
- **Same embedding model** for chunks and question (2.5). Mixing models
  gives wrong scores, no error.
- **Embed once, store the vectors.** Re-embedding 122 chunks per question
  would cost 10+ s each time. 4.4 saves them to disk.
- **Your own check counts.** "Right" here = the answer contains the
  expected words ("15 minutes"). Crude, but honest and repeatable. 5.1
  builds a real eval set.

> ▶ **Now run part 2** (needs Ollama, ~3 min).
> `uv run python 04_rag/4_1_rag_by_hand/examples_4_1_2_answer.py`

## 6. Where it is used next
| Lesson | Uses |
|---|---|
| 4.2 PDFs | the same pipeline, text taken from PDF files |
| 4.3 Chunking | more ways to cut, measured like section 3 |
| 4.4 Chroma | stores chunks + vectors, does the `@` + sort for you |
| 4.6 assistant v3 | this pipeline inside the chat app |
| 4.10 Citations | show which chunk an answer came from; "I don't know" |
| 5.1 Eval set | the 12 questions, grown into a real test set |

## Exercises: make the tests pass
You write the 6 `raise NotImplementedError` functions in
[rag_4_1.py](rag_4_1.py). The spec is 2 test files:
[exercises_4_1_1_chunks.py](exercises_4_1_1_chunks.py) (cutting, no
Ollama) and [exercises_4_1_2_search.py](exercises_4_1_2_search.py)
(embed, search, prompt, answer). 27 tests without Ollama + 3 real.
Follow [CODE_STYLE.md](../../docs/CODE_STYLE.md): clear names, one step per
line, `@debug` + `log.debug` for start / steps / result.

| Function | Does | Tests |
|---|---|---|
| `split_by_headings` | one chunk per `## ` section | 8 |
| `split_by_size` | fixed-size pieces with overlap; bad numbers → ValueError | 10 |
| `embed_texts` | one `/api/embed` call → numpy matrix | 2 + 1 real |
| `find_top_chunks` | `@` + `argsort` → best row numbers | 6 + 1 real |
| `build_rag_messages` | rules + chunks + question | 1 |
| `answer_question` | the whole chain | 1 real |

```
uv run pytest 04_rag/4_1_rag_by_hand -v
```
Ollama off? Add `-m "not ollama"`. Reference solution, measured:
**30 passed in 4.2–13.1 s** (3 runs; first run loads the models),
27 + 3 deselected in 0.14 s, pyright 0. The stubs: 27 failed, 3 errors
(the real tests' setup calls `embed_texts`).
