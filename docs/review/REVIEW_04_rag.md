# Review: phase 04, RAG

Per topic: the **flow** (how the process runs), the **must-remember** points,
then a **quiz**. Click a question to see the answer. Say your answer first.
Keywords: [GLOSSARY_AI.md](GLOSSARY_AI.md), [GLOSSARY_PYTHON.md](GLOSSARY_PYTHON.md).

## 4.1 RAG by hand: chunk, embed, search with numpy
```
ONCE:          documents → chunks (by "## " heading) → /api/embed → table (chunks × 768)
PER QUESTION:  question → /api/embed → [0] = one vector (768,)
                 → table @ vector = one score per chunk → argsort(-scores) → top_k rows
                 → system: rules + "I don't know" + chunks, user: question → /api/chat
```
- **The model doesn't know your documents.** Alone: 1/12 right, and it sounds sure.
- **Sending everything cuts silently.** `num_ctx` 4096 read 2 050 of 7 217 tokens: 5/12.
- **RAG = same score, far fewer tokens.** 11/12, 213–493 tokens, 4–5x faster than all text.
- **How you cut decides what you find.** By heading: right chunk 1st 12/12; by size: 10/12.
- **numpy `@` scores all chunks in one line.** 20 000 chunks: ~6 ms vs ~600 ms in a loop.
- **Shapes must match.** `embed_texts([q])` is `(1, 768)`; take `[0]` for `(768,)`.

<details><summary>Q1. What do R, A and G stand for, and what does each step do?</summary>Retrieve: find the chunks that fit the question. Augment: put them in the prompt. Generate: the model answers from them.</details>
<details><summary>Q2. All text, default context: why only 5/12?</summary>Ollama read 2 050 of 7 217 tokens and dropped the rest, with no error. The rules got lost too.</details>
<details><summary>Q3. Why did cutting by size give the wrong "dark mode" version?</summary>The piece held two versions. The model picked 8.6.1, the wrong one. By heading, one section = one topic.</details>
<details><summary>Q4. Why is the dot product enough here, no dividing?</summary>nomic vectors have length 1.0, so dot product = cosine (2.5).</details>
<details><summary>Q5. `split_by_size` with overlap = chunk_size: what happens, and the fix?</summary>`start` never moves: endless loop until MemoryError. Check the numbers first and raise ValueError.</details>
<details><summary>Q6. `(14, 768) @ (1, 768)` fails. Why, and the fix?</summary>The inner sizes must match (768 vs 1). The question is a 1-row table; take row `[0]` to get `(768,)`.</details>
<details><summary>Q7. The Refunds chunk was found first, but the answer was "I don't know". Why?</summary>Found is not answered: the model didn't work out that 3 weeks > 14 days. Search finds text; the model still has to think.</details>

## 4.2 Loading PDFs, cleaning text
```
PDF → pypdf extract_text(layout) → one text per page
  → 1. drop header + footer (line on half the pages or more; digits → "#")
  → 2. NFKC (ﬁ → fi, no-break space → space)
  → 3. glue cut words ("confir-\nmation" → "confirmation")
  → 4. one line per paragraph → CleanPage(page_number, text), empty pages skipped
```
- **A PDF has no words or lines**, only letters at spots. pypdf guesses the lines.
- **layout mode keeps paragraph gaps** (42), plain mode loses all (0).
- **Cleaning matters for exact search**: 3/9 → 9/9 answers found by exact text.
- **Vector search hardly cares**: right chunk 1st 8/9 → 9/9; tokens 1 884 → 1 757.
- **Order matters.** Header out and words glued **before** lines are joined.
- **Scans give `""`.** Need OCR. Always count empty pages.

<details><summary>Q1. Why does searching "confirmation" miss raw PDF text?</summary>The text holds `con\ufb01rmation`: "fi" is one ligature character. NFKC turns it back into "f" + "i".</details>
<details><summary>Q2. How is "Page 2 of 6" found as a footer when every page number differs?</summary>Digits become `#` first, so every page has "Page # of #". A pattern on half the pages or more = header / footer.</details>
<details><summary>Q3. Why glue cut words before joining lines?</summary>The glue looks for `-` + line break. Once lines are joined, the break is gone and "confir- mation" stays split.</details>
<details><summary>Q4. Two ways the header rule goes wrong?</summary>A 1-page PDF: its header is on 1 page only, so it stays. A real sentence on half the pages: it is removed.</details>
<details><summary>Q5. Page 6 gives an empty string. Why, and the fix?</summary>It is a scan: a picture of text, no letters. Needs OCR (e.g. Tesseract). Not in this course.</details>
<details><summary>Q6. Why keep the PDF page number in `CleanPage`?</summary>For answers like "see page 3" (4.10). Empty pages are skipped, so the list position is not the page number.</details>

## 4.3 Chunking strategies
```
clean text → pieces: paragraphs (heading glued to the next) or sentences
  → pack: add whole pieces while chunk + joiner + piece <= max, then a new chunk
recursive: too big? cut at "\n\n", else ". ", else " ", else every max characters
meaning:   embed every sentence → similarity to the next → cut at the lowest 10%
```
- **Size is a trade-off.** 200: answers cut in two, right 1st 6/12. 2000: one blurred vector, 8/12.
- **Cut at boundaries.** Paragraphs + headings at 500: 12/12, 1 161 characters to read vs 1 438.
- **A heading stays with its text.** Plain paragraphs: 10 chunks end on a heading; glued: 0.
- **Packing never cuts a piece.** A piece over the max is its own chunk.
- **Recursive keeps the separators**: `"".join(chunks)` gives the text back.
- **By meaning costs one embed per sentence.** Same 12/12 here; for text with no headings.

<details><summary>Q1. Why does 200 characters, no overlap, find the right chunk first only 6/12?</summary>The answer sentence is cut in two: one chunk has the topic, the next has the number. Neither holds the whole answer.</details>
<details><summary>Q2. Why is 2000 characters worse (8/12) than 500?</summary>One vector for a page of topics is a blur: refunds, storage and sync share it, so each question matches only a bit.</details>
<details><summary>Q3. Why glue a heading to the paragraph after it?</summary>Alone it lands at the end of a chunk as noise, and the next chunk loses its topic name. 4.10 needs it to say "see Refunds".</details>
<details><summary>Q4. In `pack_pieces`, why check `current_chunk == ""` first?</summary>The first piece of a chunk has no joiner in front. Without it, a chunk starts with `" "` or `"\n\n"`.</details>
<details><summary>Q5. `chunk_by_meaning`: why check "no sentences" before the length check?</summary>With 0 sentences, one fewer is -1, so the ValueError would fire wrongly, and `sentences[0]` would crash.</details>
<details><summary>Q6. The 5 least alike sentence pairs: what were they?</summary>All 5 were section starts (e.g. "...Nothing is deleted." | "Refunds"). The embeddings found the headings without being told.</details>
