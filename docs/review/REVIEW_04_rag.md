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
