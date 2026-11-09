# Review: key concepts + keywords

For reviewing what was learned. Grows by one section per finished topic.

## How to use it
1. Read the **big picture** below. Can you say each arrow out loud?
2. Open a review file. Per topic: read the flow, then do the quiz.
   Answer first, then click. A miss → reread that topic's LESSON.
3. Skim a glossary for words you can't explain in one line.

| File | Covers |
|---|---|
| [REVIEW_01_python.md](REVIEW_01_python.md) | 1.1–1.5, 1.7, 1.9: flows + quiz |
| [REVIEW_02_llm.md](REVIEW_02_llm.md) | 2.1–2.5: flows + quiz |
| [GLOSSARY_AI.md](GLOSSARY_AI.md) | AI / LLM keywords, A–Z |
| [GLOSSARY_PYTHON.md](GLOSSARY_PYTHON.md) | Python + pytest keywords, A–Z, with the Java twin |

## The big picture so far
**Generating an answer** (2.1–2.4):
```
your code builds messages [system, user, assistant, ...]          (2.3)
  → POST /api/chat to Ollama on 127.0.0.1:11434                   (1.7, 2.2)
  → text cut into tokens, must fit the context window             (2.1)
  → model (quantized weights in RAM) scores every token: logits   (2.1, 2.2)
  → ÷ temperature → softmax → top_k / top_p → pick (seed)         (2.4)
  → append, repeat until stop or num_predict                      (2.1, 2.4)
  → streamed back as NDJSON lines, or one JSON reply               (2.3)
```
**Finding text by meaning** (2.5, the base of RAG in phase 04):
```
notes + question → /api/embed → vectors → cosine → sort → top k notes
```
**Proving it works** (1.9):
```
pytest: fakes for your logic (no Ollama) + 1 real test marked `ollama`
```
