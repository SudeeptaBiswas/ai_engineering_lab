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
