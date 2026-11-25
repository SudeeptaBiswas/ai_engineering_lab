# 4.4 Chroma vector DB: embed once, keep it on disk, search with filters (~3 h)

Basic level, phase 04. Uses: 4.1 (search = table @ vector, top 3), 4.3
(the handbook text, the 12 questions, ~500 characters), 2.5 (cosine,
vectors of length 1.0), 1.9 (fixtures, `yield`). Next: 4.5 LangChain's
`Chroma` store wraps the same calls, 4.6 PDF Q&A stores its chunks here,
4.10 cites the heading kept as metadata.

All numbers **measured on 10284Sudee** (CPU only), Ollama 0.40.18,
nomic-embed-text, chromadb 1.5.9, 2026-11-25. Scores were the same in 2 runs.
Text: the 4.3 handbook ([handbook_4_3.txt](../4_3_chunking/handbook_4_3.txt)),
cut into **18 chunks**, one section each (a long section gives 2), every
chunk starting with its heading ([handbook_4_4.py](handbook_4_4.py)).
4.3 made 16: there a chunk could hold 2 short sections. Here a chunk
never crosses a section, so each has exactly one heading to store.

## The problem
4.1–4.3 kept the vectors in a numpy table in memory. When the script
ends, the table is gone. Every run embeds every chunk again:
```
4.3 part 2: 12 questions, but first 16 chunks embedded ... every run, every way to cut
```
On this PC, the 18 handbook chunks take **5.6 s** to embed. That is fine
once. Not on every start, and not for 10 000 chunks (4.1: 20 000 rows).
And numpy has no way to say "search only in the Refunds section", or
"this one chunk changed, replace it".

## Goal
Embed each chunk **once**, keep it on disk. The next run finds the 18
chunks and is ready to search in **0.34 s** instead of 5.6 s, with the **same
12/12** right answers as numpy.

## How we get there
Keep the table of vectors in a file, next to each chunk's text and a
few labels (its heading). Give each chunk a name, so the program can
ask "do you have `refunds-0` already?" and embed only what is new.
A **vector database** does this: it stores vectors with their text,
finds the nearest ones to a question vector, and filters by the labels.
**Chroma** is one that runs inside Python, no server, no account.

## Steps
```
1. Open a client on a folder.            chromadb.PersistentClient(path="chroma_db_4_4")
2. Open a collection (a named table).    "handbook", measured by cosine
3. Ask which chunk ids are missing.      run 1: all 18; run 2: none
4. Embed only those, add them.           ids + vectors + texts + {"heading", "position"}
5. Search with a question vector.        refunds-0 first, distance 0.315 = similarity 0.685
6. Filter by heading if needed.          where={"heading": "Export and import"}
7. A chunk changed? update(), not add(). add() with a known id changes nothing
```

## Your path
1. Read sections 1–3. Run part 1 **twice**.
2. Read sections 4–7. Run part 2.
3. Read section 8. Run part 3 (the first run downloads 79 MB).
4. Read sections 9–10. Do the exercises: write the 5 functions yourself.

## Java → Python map
| Java | Python |
|---|---|
| `Map<String, Object>` for labels | `{"heading": "Refunds", "position": 10}` (a dict) |
| try-with-resources on a DB connection | not needed: run 2 found the 18 chunks, no save or close call |
| `set.contains(id)` | `chunk_id in stored_ids` (a `set`) |
| `float[][]` | `np.array(vectors, dtype=np.float32)` |

## 1. What Chroma stores
A **collection** = one table. Each row has 4 parts:

| Part | Example | 4.1 numpy had it? |
|---|---|---|
| **id** (a unique name) | `"refunds-0"` | no: a row number |
| **embedding** (the vector) | 768 numbers | yes: one table row |
| **document** (the text) | `"Refunds\n\nYou can ask for a full refund..."` | separate list |
| **metadata** (labels) | `{"heading": "Refunds", "position": 10}` | no |

The id is the key to everything below: "missing?", "replace", "delete".
Make it from the content's place (`heading-number`), not a counter, so
the same chunk gets the same id on every run.

**Client** = the connection. Two kinds:
- `PersistentClient(path=...)`: saved in a folder. Part 1.
- `EphemeralClient()`: memory only, gone at the end. Parts 2–3, tests.

## 2. Store once, reuse (part 1)
| Run | Found on disk | Embedded | Store step | Whole script |
|---|---|---|---|---|
| 1st | 0 | 18 | 5.55–5.64 s | 5.69–5.74 s |
| 2nd | 18 | **0** | **0.34 s** | 0.49 s |

(2 rounds, folder deleted before each.) The folder `chroma_db_4_4/`
holds **666 KB** for 18 chunks. It is git-ignored: any PC rebuilds it
from the text in 6 s. Delete it to start over.

How "embed once" works: ask `get(ids=[...], include=[])`. It returns
only the ids it has (`include=[]` = no text, no vectors). Embed the rest.
This also answers an interview question (INTERVIEW_NOTES P1): *"A user
uploads a new document: what happens?"* Only the new chunks get embedded.

## 3. What a search gives back (part 1)
```
query(query_embeddings=[vector], n_results=2)
ids       = [['refunds-0', 'billing-and-invoices-1']]
distances = [[0.31509464979171753, 0.47771257162094116]]
```
- **Lists inside lists**: you may send many questions at once, so you
  get one list per question. One question → take `[0]`.
- **Distance**, not similarity: smaller = closer (section 4).
- Only what you `include` comes back. Default: documents, metadatas,
  distances. Vectors are left out (768 numbers each).

Top 3 for *"I paid three weeks ago. Can I still get a refund?"*:
```
0.685  refunds-0               You can ask for a full refund within 14 days of a payment...
0.522  billing-and-invoices-1  We accept Visa, Mastercard and PayPal...
0.515  billing-and-invoices-0  We charge the card on the same day of the month...
```

> ▶ **Now run part 1, twice** (needs Ollama; ~6 s, then ~0.5 s).
> `uv run python 04_rag/4_4_chroma/examples_4_4_1_store.py`

## 4. Distance: cosine or l2 (part 2, section 2)
Chroma measures how far apart two vectors are. You pick how, once, when
the collection is made. **Chroma's default is `"l2"`**, not cosine.

| Space | What Chroma returns | Same vectors, refund question, best 3 |
|---|---|---|
| `"cosine"` | 1 − similarity | 0.315, 0.478, 0.485 |
| `"l2"` | squared straight-line distance | 0.63, 0.955, 0.97 |

- Same 3 chunks, same order. The l2 numbers are exactly **2×** the cosine ones.
- Why: our vectors have length 1.0 (2.5). Then l2² = 2 − 2 × similarity.
- So the order is the same, but a rule like "keep chunks with distance
  < 0.4" means something else in each space. We set `"cosine"`, so
  similarity = 1 − distance, the number we know since 2.5.

## 5. As good as numpy? (part 2, section 1)
| Search | Right 1st | In top 3 | Same top 3 as numpy |
|---|---|---|---|
| Chroma, cosine, 18 chunks | **12/12** | 12/12 | **12/12** |

Same ids, same order as 4.1's `table @ vector` for all 12 questions.
Inside, Chroma uses an **index** called HNSW (a graph that jumps
close to the answer without comparing every row). It can miss a row on
very big collections; at 18 chunks it found the same as numpy (not
measured on big ones here).

## 6. Filter by metadata (part 2, section 3)
*"How long is the link valid?"* Which link? Password reset, export,
shared note. Without a filter, the export rule is not even in the top 3:
```
where=None                              where={"heading": "Export and import"}
0.593  sharing-0                        0.493  export-and-import-0
0.569  passwords-and-sign-in-0
0.550  accounts-and-sign-up-0
```
The filter runs **before** the ranking: only chunks with that heading
compete. Use it when the app knows more than the question (the user is
on the Export page, or asked about one product).

More filters (from Chroma's types; only the first is run in this lesson):

| Filter | Means |
|---|---|
| `{"heading": "Refunds"}` | heading equals "Refunds" |
| `{"position": {"$lt": 5}}` | position below 5 (`$gt`, `$lte`, `$gte`, `$ne` too) |
| `{"heading": {"$in": ["Refunds", "Billing and invoices"]}}` | one of these |
| `{"$and": [{...}, {...}]}` | both (`$or`: either) |

## 7. Change a chunk: add() vs update() (part 2, section 4)
The refund window goes from 14 to 30 days:
```
add()    same id: 18 chunks, text 'You can ask for a full refund within 14 days of a payment. A'
update() same id: 18 chunks, text 'You can ask for a full refund within 30 days of a payment.'
```
- `add()` with an id that exists: **nothing happens, no error**. The
  old rule stays, and search keeps quoting 14 days.
- `update()` changes the text and the vector; metadata left out is kept.
- `update()` with an id that does **not** exist: also nothing, no error
  (checked once, Chroma 1.5.9). So check first (exercise 5).
- `upsert()` = update if there, add if not. `delete(ids=[...])` removes.
- Always change the vector **with** the text. New text, old vector =
  the chunk is found by its old meaning.

> ▶ **Now run part 2** (needs Ollama, ~16 s): sections 4–7.
> `uv run python 04_rag/4_4_chroma/examples_4_4_2_search.py`

## 8. Two embedding models (part 3)
Chroma has its own model, **all-MiniLM-L6-v2**. It runs inside Python,
no Ollama, through **onnxruntime** (a library that runs a trained model
file; installed with chromadb). First use downloads it: **79.3 MB, 2 min 15 s**
here, into `C:\Users\<you>\.cache\chroma\` (174.5 MB unpacked).

| Model | Numbers per text | Embed 18 chunks + 12 questions | Right 1st | In top 3 |
|---|---|---|---|---|
| nomic-embed-text (Ollama) | 768 | 3.94–5.69 s | 12/12 | 12/12 |
| all-MiniLM-L6-v2 (Chroma) | 384 | 1.82–2.38 s | 12/12 | 12/12 |

(4 runs, model loaded first, so loading is not counted.)

- **Same score** on this handbook: 12 easy questions can't tell them
  apart. A harder set (5.2) might.
- MiniLM: half the numbers (half the disk), ~2× faster here.
- **But it reads only the start.** Chroma cuts its input at 256 word
  pieces (chromadb source, `onnx_mini_lm_l6_v2.py`, `max_length=256`).
  Test: 2 518 characters of other sections, then the refund chunk at the end.
```
                   refund question vs text: without the refund part | with it
nomic-embed-text   0.409 | 0.439      the refund part counts
all-MiniLM-L6-v2   0.026 | 0.026      not read at all
```
  With ~500-character chunks this never bites. With big chunks, MiniLM
  silently ignores the end.

**Easy mode**: give `add(documents=...)` without vectors, and
`query(query_texts=[...])`. Chroma embeds with MiniLM for you. Refund
question → `['refunds-0', 'billing-and-invoices-1', 'billing-and-invoices-0']`.

**The trap**: our nomic collection still has MiniLM attached as its
default. `query_texts` on it embeds the question with MiniLM:
```
InvalidArgumentError: Collection expecting embedding with dimension of 768, got 384
```
Here it crashes, luckily. Two models with the **same** length would not
crash: they would return nonsense. Rule: the question and the chunks
must be embedded by the **same model**.

This answers an interview question (INTERVIEW_NOTES W8): *"Did you
compare embedding models?"* Yes: same eval, score, size, speed, input limit.

> ▶ **Now run part 3** (needs Ollama, 14–18 s; first run +2 min download).
> `uv run python 04_rag/4_4_chroma/examples_4_4_3_models.py`

## 9. Things that bite
- **Default distance is l2.** Set `configuration={"hnsw": {"space": "cosine"}}`
  when you create the collection. Later it can't change: `modify()` →
  `unknown field 'space'`, and `get_or_create_collection` with `"l2"` on
  an existing cosine collection silently keeps cosine (checked once).
- **Silent no-ops**: `add` of a known id and `update` of an unknown id
  both do nothing and raise nothing.
- **Same model on both sides** (section 8). Changing the model = new
  collection, embed everything again.
- **Collection names**: 3–512 characters, letters, digits, `.` `_` `-`.
  `"t"` → `InvalidArgumentError`.
- **EphemeralClient is shared** inside one Python process: two of them
  see the same collections. The tests use a random name per test.
- **float32**: Chroma keeps 7 digits. 1 − 0.6 comes back as 0.39999998.
  Compare with `pytest.approx`.
- **Telemetry**: `anonymized_telemetry` is `True` by default. In 1.5.9
  its sender is empty (`posthog.py`: `capture` does `pass`), older
  versions sent usage stats. We turn it off anyway (`NO_TELEMETRY`).
- **Types**: pyright wants the vectors as `np.array(..., dtype=np.float32)`
  for `add` / `update`; a `list[list[float]]` is a type error there.

## 10. When to use what
| Need | Use |
|---|---|
| a quick test, a few hundred chunks | numpy table (4.1): nothing to install |
| keep vectors between runs, filter, change chunks | **Chroma** `PersistentClient` |
| many users, a server, backups | a database server (Chroma server, pgvector, ...): later topics |

## Where it is used next
| Lesson | Uses |
|---|---|
| 4.5 LangChain | `Chroma` vector store = these calls behind one class |
| 4.6 PDF Q&A, assistant v3 | stores the PDF chunks once, asks many questions |
| 4.10 Citations | the `heading` metadata → "see Refunds" |
| 5.2 Retrieval metrics | harder questions to compare the 2 models again |

## Exercises: a small chunk store on Chroma
**Goal:** the 5 functions in [chroma_store_4_4.py](chroma_store_4_4.py), until
all 21 tests pass. Each function has a `How:` list in its docstring.
The tests are the spec: [exercises_4_4_1_store.py](exercises_4_4_1_store.py)
(distance, missing ids, store once), then
[exercises_4_4_2_search.py](exercises_4_4_2_search.py) (search, filter,
replace, the real handbook). `open_collection`, `SearchHit` and the
settings are given. Test helpers: [fakes_4_4.py](fakes_4_4.py) (3 tiny
chunks, vectors of 3 numbers, a fake embed function that counts calls).
Follow [CODE_STYLE.md](../../docs/CODE_STYLE.md).

| # | Function | Goal | Example: in → out | Tests |
|---|---|---|---|---|
| 1 | `distance_to_similarity` | Chroma's distance → similarity | `(0.29, "cosine")` → `0.71`; `(0.58, "l2")` → `0.71` | 6 |
| 2 | `find_missing_ids` | ids not stored yet, in order | `"refunds-0"` stored, ask `["refunds-0", "sync-0"]` → `["sync-0"]` | 3 |
| 3 | `add_missing_chunks` | embed + add only new chunks | 3 chunks, empty → `3` (1 embed call); again → `0` (no call) | 4 |
| 4 | `search_chunks` | top_k hits, optional heading filter | vector `[0.9, 0.436, 0]`, top 3 → refunds 0.9, sync 0.436, plans 0.0 | 5 + 1 |
| 5 | `replace_chunk_text` | new text + vector, same heading | `"refunds-0"`, `"Sync\n\nNow every 30 seconds."` → found by a sync vector | 2 |

"+ 1" in row 4 = one test on the real handbook with Ollama (12/12).
Total: 21 (20 without Ollama).

Edge cases the tests check (so you don't have to guess):
- `distance_to_similarity`: distance 0 → 1.0; cosine distance 1 → 0.0.
  Any space but `"cosine"` / `"l2"` (e.g. `"ip"`) → `ValueError`.
- `find_missing_ids`: empty collection → all ids, in the order asked.
  All stored → `[]`.
- `add_missing_chunks`: exactly **one** embed call for all new chunks.
  Nothing new → no call at all. Only the new chunk's text is sent.
  Metadata is `{"heading": ..., "position": ...}`.
- `search_chunks`: best first; similarity within 0.0001 (float32).
  `top_k` 2 → 2 hits. Filter keeps only that heading, even when another
  chunk is closer. Unknown heading → `[]`.
- `replace_chunk_text`: the heading metadata stays. Unknown id →
  `KeyError`, and no embed call (check before you pay for one).

Run: `uv run pytest 04_rag/4_4_chroma -v` (Ollama off? `-m "not ollama"`).
Reference solution, measured: **21 passed in 6.33–7.11 s** (3 runs);
without Ollama 20 passed in 1.61–1.83 s. Stubs: 14 failed + 7 errors
(an error = the fixture itself calls `add_missing_chunks`).
