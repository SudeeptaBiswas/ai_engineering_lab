# Interview notes

Real interview questions, checked against [TOPICS.md](TOPICS.md):
covered (done) / planned (topic id) / gap (not in the course).
Use: prep before applying, and to decide what the course is missing.

## Accenture — AI/ML Engineer (shared 2026-11-17)
Source: an interview experience post the user pasted. Checked 2026-11-17.

| # | Question | Status | Where / note |
|---|---|---|---|
| R1.1 | Supervised vs unsupervised vs reinforcement learning, examples | gap | — |
| R1.2 | SVM; the kernel trick | gap | — |
| R1.3 | KNN: training phase? how does it predict? | gap | close to 4.1 search: k nearest vectors, then their labels; no real training |
| R1.4 | Stemming vs lemmatization; when which | gap | could fit 4.7 (BM25 word matching) |
| R1.5 | Transformer architecture, self-attention | gap | 2.1 has tokens + context only |
| R1.6 | What is RAG; why an LLM if a vector DB has the documents | covered | 4.1: "found is not answered" (14-day rule found, model still had to reason) |
| R1.7 | Prompting techniques; improve answer quality | covered | 3.1 (+ 3.2 structured output) |
| R1.8 | Evaluate RAG: retrieval + answer metrics | planned | 5.1, 5.2 (recall@k, MRR), 5.3 (judge) |
| R2.1 | Recent project: architecture + your part | planned | assistant/ v2 now, v3 after 4.6 |
| R2.2 | Enterprise GenAI app: LangChain + embeddings + vector DB | planned | 4.4–4.6, capstone 10.x |
| R2.3 | Docker + Kubernetes; scale inference pods | partly planned | Docker 8.4; Kubernetes = gap |
| R2.4 | Python: preprocess data, missing values, train + evaluate a model | gap | pandas + scikit-learn not in the course |

Count: 2 covered, 4 planned (1 partly), 6 gaps.

## Interviewer post — "fundamentals, not frameworks" (shared 2026-11-18)
Source: a post the user pasted (an interviewer of 1–2 yr AI engineers).
Learning note: candidates can build RAG/agents with frameworks but can't
say *why* it works. Frameworks change; fundamentals don't. Be ready to
explain "why", and to debug: retrieval drops, latency doubles,
hallucinations rise, agent loops.

| # | Question / concept | Status | Where / note |
|---|---|---|---|
| F1 | Why do embeddings work? | partly | 2.5 (what + cosine); "why" = trained so similar meaning lands close — say it out loud |
| F2 | Why does chunk size affect retrieval? | planned | 4.3; 4.1 touched it |
| F3 | Why does attention matter? | gap | = R1.5 |
| F4 | What happens before the first token? | partly | 2.1 tokens + next-token predict; prefill + KV cache = gap |
| F5 | Transformers | gap | = R1.5 |
| F6 | Tokenization | covered | 2.1 (BPE) |
| F7 | Vector search | covered | 4.1; more in 4.4, 4.7 |
| F8 | HTTP + APIs | covered | 1.7, 2.3, 3.3; 8.1 planned |
| F9 | System design | partly planned | 10.1; latency, caching, scaling = gap |
| F10 | Databases | gap | only Chroma (4.4); no SQL |
| F11 | Evaluation | planned | 5.1–5.3, 6.11 |
| F12 | Python fundamentals | covered | phase 01; 1.8 async open |
| F13 | Debug: retrieval drops / hallucinations / agent loops | planned | 5.2 / 4.10 + 5.3 / 6.7 + 6.11 |
| F14 | Debug: latency doubles | gap | 5.4 tracing helps; no topic measures latency |

Count: 4 covered, 8 planned or partly, 4 gaps (F3, F5, F10, F14). The post's
closing "Interview Kit" ad is ignored.

## Open (user to decide)
1. Add an "ML basics" block: learning types, KNN, SVM, pandas +
   scikit-learn (missing values, train, evaluate), Transformer attention,
   stemming. Rough guess ~10–12 h (not measured), Intermediate level,
   right after Basic.
2. Add Kubernetes basics (~3 h guess) to phase 08.
3. From the 2026-11-18 post: a "how a model reads a prompt" topic after
   2.1 (Transformer, attention, prefill, KV cache; ~2 h guess), and
   SQL + latency/caching basics (~3 h guess). Item 1 already holds attention.
If yes: add to TOPICS + PLAN, and log it in DECISIONS.
