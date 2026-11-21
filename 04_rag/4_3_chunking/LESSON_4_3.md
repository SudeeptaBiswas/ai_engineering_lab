# 4.3 Chunking strategies: where to cut, so search finds the whole answer (~3 h)

Basic level, phase 04. Uses: 4.1 (cut by size, overlap, top 3), 4.2
(clean text, one line per paragraph), 2.5 (cosine), 1.9 (fixtures). Next:
4.4 Chroma stores these chunks, 4.5 LangChain's splitter = the recursive
way here, 4.6 PDF Q&A, 4.10 "see section Refunds".

All numbers **measured on BISWAS** (CPU only), Ollama 0.40.16,
nomic-embed-text, 2026-11-22. Scores were the same in 2 runs.
(*) = checked once with a one-off script that was not kept.
Text: [handbook_4_3.txt](handbook_4_3.txt) = the 4.2 clean handbook
(`clean_pdf_pages`, pages joined by an empty line), 6 131 characters.

## The problem
4.1 cut every 500 characters and it worked. Try 200, no overlap, and ask
*"What is the biggest attachment I can add?"*. The answer sentence is
cut in two:
```
chunk 17: "...Storage and attachments\n\nEach attachment ca"
chunk 18: "n be at most 200 MB. Images inside notes are shrun..."
```
Chunk 17 has the topic, chunk 18 has the number. Neither has the answer.
At 200 characters, **5 of the 12** answer sentences are cut like this,
and search puts the chunk with the whole answer first for only **6/12**.

## Goal
Cut where the text itself has a **boundary** (a natural place to cut). Best chunk holds the whole answer
sentence **12/12**, and the model reads **1 161** characters per question
instead of 1 438 (4.1's way, 500 + overlap 100).

## How we get there
Text has natural places to cut: between paragraphs, between sentences,
between words. Cut at the biggest one that keeps a chunk small enough.
Then put whole pieces together until the chunk is full.
A **heading** ("Refunds") is tiny but tells what the next paragraph is
about, so it must stay with that paragraph.
A **chunking strategy** = the rule for where to cut. We compare 4.1's
way with four new ones.

## Steps
```
1. Cut into pieces: paragraphs or sentences.   38 paragraphs, 93 sentences
2. Glue each heading to the paragraph after.   "Refunds" + "You can ask for a full refund..."
3. Pack whole pieces into chunks of <= 500.    16 chunks, none cut mid-sentence
4. A piece still too big? Cut it smaller:       paragraph -> sentence -> word -> character
   that is the "recursive" way.
5. Or: cut where 2 sentences in a row are       0.379 between "...Nothing is deleted." and "Refunds"
   least alike ("by meaning").
6. Measure: whole answer in the best chunk?     12/12, 1 161 characters to read
```

## Your path
1. Read sections 1–3. Run part 1 (no Ollama).
2. Read sections 4–5. Run part 2.
3. Read section 6. Run part 3.
4. Read sections 7–8. Do the exercises: write the 6 functions yourself.

## Java → Python map
| Java | Python |
|---|---|
| `text.split("(?<=[.!?])\\s+")` | `re.split(r"(?<=[.!?])\s+", text)` |
| `s.endsWith(a) \|\| s.endsWith(b)` | `s.endswith((a, b))` (a tuple = any of these) |
| `list.addAll(other)` | `my_list.extend(other)` |
| a method that calls itself | same: a recursive function |

## 1. Ways to cut: 4.1's way + 4 new ones
| Way | Cuts at | Example (max 30) |
|---|---|---|
| **characters** (4.1) | every N characters, maybe overlap | `"Ask within 14 days. After th"` / `"at, no refund."` |
| **sentences** | after `.` `!` `?` + space | `"Ask within 14 days."` / `"After that, no refund."` |
| **paragraphs + headings** | at empty lines; heading glued to next | `"Refunds\n\nAsk within 14 days."` |
| **recursive** | `"\n\n"`, else `". "`, else `" "`, else characters | the biggest boundary that fits |
| **by meaning** (section 6) | where neighbor sentences differ most | needs embeddings |

All but the first **pack**: add whole pieces to a chunk while it fits
(chunk + joiner + piece <= max), then start the next chunk.
A piece bigger than the max alone stays whole (packing never cuts).

**Recursive** = a function that calls itself on a smaller problem.
Here: try to cut at paragraphs; a paragraph still too big is cut
again, at sentences, by the same function with the next separator.

## 2. How the chunks end (part 1)
Same handbook, max 500 characters:

| Way | Chunks | Average | End mid-sentence | End on a heading |
|---|---|---|---|---|
| characters 500, overlap 100 | 16 | 476 | **14** | 0 |
| sentences | 14 | 434 | 0 | 4 |
| paragraphs | 16 | 381 | 0 | **10** |
| paragraphs + headings | 16 | 381 | 0 | **0** |
| recursive | 16 | 381 | 0 | 10 |

- **Characters** end mid-sentence 14 times out of 16.
- **Sentences** and **paragraphs** never cut a sentence, but a heading
  is a piece too. When it is the last piece that fits, it lands at the
  **end** of a chunk, and its text starts the next one:
```
paragraphs:             ...'ad-only. Nothing is deleted.\n\nRefunds]'      ] = chunk end
paragraphs + headings:  '[Refunds\n\nYou can ask for a full refund within 14 days...'
```
- **Recursive** does the same: it knows boundaries, not headings.

> ▶ **Now run part 1** (no Ollama, ~1 s): the table above + where "Refunds" lands.
> `uv run python 04_rag/4_3_chunking/examples_4_3_1_cut.py`

## 3. Why a heading must stay with its text
- At the end of chunk A, "Refunds" is noise: A is about payments.
- At the start of chunk B, it is missing: B says "You can ask for a full
  refund within 14 days" but not that this is *the* refund rule.
- 4.10 will quote a section name ("see Refunds"). That needs the
  heading inside the chunk.

Search scored the same with or without the glue: recursive has no glue
(at 500 and 1000 its chunks are exactly the "paragraphs" ones, checked
once (*)), and it ties with paragraphs + headings (section 5).
The glue is about clean chunks for the model and for citations.

## 4. Size matters (part 2, section 1)
Cut by characters. "Right 1st" = the best chunk holds the whole answer
sentence. "To read" = the top 3 chunks together: what the model gets.

| Size, overlap | Chunks | Right 1st | In top 3 | To read |
|---|---|---|---|---|
| 200, 0 | 31 | **6/12** | 7/12 | 600 |
| 200, 40 | 39 | 9/12 | 9/12 | 587 |
| 500, 0 | 13 | 10/12 | 11/12 | 1 377 |
| 500, 100 (4.1) | 16 | 11/12 | 11/12 | 1 438 |
| 1000, 0 | 7 | 9/12 | 11/12 | 2 637 |
| 1000, 200 | 8 | 11/12 | 12/12 | 2 921 |
| 2000, 400 | 4 | **8/12** | 12/12 | 5 498 |

- **Too small** (200): answers are cut in two (the problem above).
- **Too big** (2000): one vector for a whole page of topics is a blur.
  Refunds, storage and sync share one vector, so a refund question
  matches it only a bit. Right 1st drops to 8/12, and the model reads
  5 498 characters per question.
- **Overlap** repairs some cuts (200: 6 → 9; 1000: 9 → 11), but every
  repeated part is embedded and stored twice (200: 31 → 39 chunks).
- This answers an interview question (INTERVIEW_NOTES F2): *"Why does
  chunk size affect retrieval?"* Small cuts answers apart; big blurs the vector.

## 5. Cut at boundaries, same size (part 2, section 2)
| Way | 200: right 1st | 500: right 1st | 1000: right 1st | 500: to read |
|---|---|---|---|---|
| characters, overlap 1/5 | 9/12 | 11/12 | 11/12 | 1 438 |
| sentences | 10/12 | 11/12 | 10/12 | 1 334 |
| paragraphs + headings | 11/12 | **12/12** | 10/12 | **1 161** |
| recursive | 11/12 | **12/12** | 10/12 | 1 166 |

In top 3: 12/12 for every boundary-based way, except sentences at 1000 (11/12).
- At **500**, paragraphs and recursive get 12/12 with **19% less** to
  read than 4.1's way (1 161 vs 1 438), and without overlap.
- At **200**, boundaries matter most: 6/12 (characters, no overlap) → 11/12.
- At **1000**, every way is 10–11/12: too big blurs whatever the cut.
- 12 questions on one handbook: one question = 8%. Read 11 vs 12 as
  "about the same", 6 vs 11 as a real difference.

> ▶ **Now run part 2** (needs Ollama, 49–57 s): both tables.
> `uv run python 04_rag/4_3_chunking/examples_4_3_2_score.py`

## 6. Cut by meaning (part 3)
No boundaries to use? Let the embeddings find the topic changes.
This is called **semantic chunking** (semantic = about meaning):
1. Embed every sentence (93 vectors).
2. Compare each sentence with the next: 92 similarities (dot = cosine, 2.5).
3. Cut where a similarity is among the lowest 10% (or 25%).

The 5 lowest pairs, all from part 3:
```
0.323  'annot take over an account quickly.' | 'Plans and prices'
0.360  'tes on the device but stop syncing.' | 'Export and import'
0.369  'n.example with your invoice number.' | 'Storage and attachments'
0.379  'but you cannot add new attachments.' | 'Sync'
0.379  'Nothing is deleted.' | 'Refunds'
```
Every one is a section start. The embeddings found the headings without
being told.

| Way, max 500 | Chunks | Right 1st | To read |
|---|---|---|---|
| meaning, lowest 10% (< 0.410) | 17 | 12/12 | 1 161 |
| meaning, lowest 25% (< 0.466) | 26 | 12/12 | 913 |
| paragraphs + headings | 16 | 12/12 | 1 161 |

- Same score as paragraphs here. The handbook already marks its topics
  with headings, so meaning finds nothing new.
- **Cost**: every sentence is embedded once to cut, then each chunk
  again to search. Part 3: 93 sentences 3.9–5.0 s, vs the 16 chunks 2.8–3.0 s (2 runs).
- Use it for text with **no** structure: a chat log, a speech, OCR text
  (OCR = text read from a picture of a page, 4.2 section 6).

> ▶ **Now run part 3** (needs Ollama, ~18 s): lowest pairs, score, cost.
> `uv run python 04_rag/4_3_chunking/examples_4_3_3_meaning.py`

## 7. Things that bite
- **Abbreviations**: `"e.g. a note"` has `. ` inside one sentence. Our
  regex cuts there. This handbook has none; real text does. Fine for
  packing (the pieces go back together), wrong for counting sentences.
- **Max is in characters, not tokens.** The model counts tokens
  (2.1: roughly 4 characters each in English). 500 characters ≈ 125 tokens.
- **Headings need a rule.** Ours: short (≤ 60) and no end mark.
  A one-line list item "Free plan" looks the same. Markdown has `#`; PDFs
  lose it (4.2). Check a few by eye.
- **Tables and lists** get cut like text: a row without its header row
  means nothing. Not in this course yet (INTERVIEW_NOTES T1.8).
- **Recursive keeps the separators**: chunks end with `"\n\n"` or `" "`,
  so `"".join(chunks)` is the text again. Strip before you show one.
- **The lowest 10%** is a share, not a fixed number: a document with
  no topic change still gets cuts.

## 8. Which one to use
| Text | Way | Why |
|---|---|---|
| has paragraphs + headings (handbooks, docs) | paragraphs + headings, ~500 | 12/12, least to read |
| has paragraphs, unknown shape | recursive, ~500 | never over the max, LangChain's default (4.5) |
| no structure (chat, speech, scanned pages) | by meaning | finds topic changes, costs one embed per sentence |
| a quick test | characters + overlap | simple; 11/12 at 500 |

Start at ~500 characters, measure with your own questions, then change.

## Where it is used next
| Lesson | Uses |
|---|---|
| 4.4 Chroma | stores the chunks + vectors, does the search |
| 4.5 LangChain | `RecursiveCharacterTextSplitter` = `chunk_recursively` |
| 4.6 PDF Q&A, assistant v3 | 4.2 clean pages → `chunk_by_paragraphs` |
| 4.10 Citations | the heading inside the chunk → "see Refunds" |
| 5.2 Retrieval metrics | "right 1st" grows into recall@k and MRR |

## Exercises: cut a document 4 ways
**Goal:** the cutting functions above, in [chunking_4_3.py](chunking_4_3.py),
until all 36 tests pass. Each function has a `How:` list in its docstring.
The tests are the spec: [exercises_4_3_1_pieces.py](exercises_4_3_1_pieces.py)
(sentences, packing), then [exercises_4_3_2_chunks.py](exercises_4_3_2_chunks.py)
(paragraphs, recursive, meaning, the real handbook). No Ollama needed.
`is_heading` and `split_into_paragraphs` are given. Follow
[CODE_STYLE.md](../../docs/CODE_STYLE.md).

| # | Function | Goal | Example: in → out | Tests |
|---|---|---|---|---|
| 1 | `split_into_sentences` | paragraphs, then sentences | `"Refunds\n\nAsk within 14 days. No refund after."` → `["Refunds", "Ask within 14 days.", "No refund after."]` | 6 |
| 2 | `pack_pieces` | whole pieces into chunks ≤ max | `["aa", "bb", "cc"]`, 5, `" "` → `["aa bb", "cc"]` | 7 |
| 3 | `chunk_by_sentences` | 1 + 2, joiner `" "` | `"A b. C d. E f."`, 9 → `["A b. C d.", "E f."]` | 3 + 1 |
| 4 | `chunk_by_paragraphs` | heading glued to next, then 2 | `"Refunds\n\nAsk within 14 days."` with max 30 → one chunk, heading in front | 5 + 1 |
| 5 | `chunk_recursively` | biggest boundary that fits | `"Aa bb. Cc dd."`, 8 → `["Aa bb. ", "Cc dd."]` | 6 + 1 |
| 6 | `chunk_by_meaning` | new chunk below `cut_below` | similarities `[0.81, 0.42]`, 0.5 → cut before the 3rd sentence (index 2) | 6 |

"+ 1" = one test on the real handbook. Total: 36.

Edge cases the tests check (so you don't have to guess):
- `split_into_sentences`: `"7.2 or newer"` is not an end (no space after
  the `.`). Extra spaces and empty lines are dropped. `""` → `[]`.
- `pack_pieces`: exactly max fits. The joiner counts toward the length
  (`"aa\n\nbb"` is 6). A piece over the max is its own chunk, never cut.
  `max_characters` < 1 → `ValueError`.
- `chunk_by_paragraphs`: two headings in a row both wait for the next
  paragraph. A heading at the very end becomes its own piece (packing
  may still add it to the chunk before). Handbook at 500: 16
  chunks, 0 end on a heading.
- `chunk_recursively`: the separator stays at the end of its piece
  (`"Aa bb. "`). No separators left → cut every max characters.
  `""` → `[]`. Handbook: `"".join(chunks)` == the text, none over 500.
- `chunk_by_meaning`: exactly `cut_below` is not below (no cut). Full
  chunk → cut too. No sentences → `[]`. Wrong number of similarities
  (not one fewer than sentences) → `ValueError`.

Run: `uv run pytest 04_rag/4_3_chunking -v`.
Reference solution, measured: **36 passed in 0.19–0.21 s** (3 runs);
stubs: 36 failed.
