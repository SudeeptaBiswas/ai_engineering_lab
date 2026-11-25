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

## Post — "production-ready RAG" (shared 2026-11-19)
Source: a post the user pasted. Learning note: "embed + store" is the
demo. Production = what happens when data changes, users grow, and
ingestion fails. Don't write "production-ready" unless you can answer these.

| # | Question | Status | Where / note |
|---|---|---|---|
| P1 | User uploads a new document: what happens? | covered | 4.1 by hand; 4.4 Chroma: only chunk ids not stored yet get embedded (run 2: 0 of 18); 4.6 planned |
| P2 | Same document uploaded twice (dedup) | gap | idea: chunk id = content hash, so re-upload overwrites |
| P3 | Existing document updated (versioning) | gap | idea: doc_id + version in metadata, delete old then add new |
| P4 | Remove outdated embeddings (stale content) | gap | = P3; delete by doc_id metadata |
| P5 | Embedding fails halfway (recovery) | partly | 6.2 retries; idempotent re-run + ingest status = gap |
| P6 | One user's docs never retrieved by another | gap | idea: user_id metadata filter on every query; 7.7 is MCP auth only |
| P7 | Observability: know when ingest/retrieval breaks | partly planned | 5.4 Langfuse (retrieval); ingest logs/counts = gap |

Count: 1 covered, 2 partly, 4 gaps (P2, P3, P4, P6). Closing ad ignored.

## TCS — Agentic AI Engineer (shared 2026-11-21)
Source: an interview experience post the user pasted. Checked 2026-11-21.
Learning note: explain implementation choices and trade-offs, not just terms.

| # | Question | Status | Where / note |
|---|---|---|---|
| T1.1 | Build an LLM inference microservice | planned | 8.1, 8.3 (FastAPI around Ollama), 8.4 Docker |
| T1.2 | KV cache; inference optimization (batching) | partly | 2.2 KV cache = memory for the context; how it speeds decoding + batching = gap (= F4) |
| T1.3 | HPA (autoscaling) for LLM services | gap | Kubernetes (= R2.3) |
| T1.4 | Quantization and distillation | partly | quantization covered 2.2 (Q4_K_M, GB measured); distillation = gap |
| T1.5 | Hallucinations and repetitive output | partly | 4.1 "I don't know" rule, 4.10 + 5.3 planned; repetition (repeat_penalty, sampling) = gap, near 2.4 |
| T1.6 | LLM-as-a-Judge | planned | 5.3 |
| T1.7 | Document versions in RAG | gap | = P3 |
| T1.8 | Large tables from PDFs into RAG | gap | 4.2 only warns ("check a page by eye"); table extraction not taught |
| T1.9 | Micro F1 vs macro F1 | gap | ML basics (Open 1); 5.2 has recall@k, MRR only |
| T1.10 | Imbalanced datasets | gap | ML basics (Open 1) |
| T2.1 | Your project architecture | planned | 10.1 (= R2.1) |
| T2.2 | Latency metrics you measure | partly | 2.2 tokens/s, load time; time to first token, p95 = gap (= F14) |
| T2.3 | Frameworks for LLM deployment | partly | Ollama covered (2.2); vLLM / TGI = gap |
| T2.4 | Build a summarizer agent in LangGraph | planned | 6.5–6.7 |

Count: 0 covered, 4 planned, 5 partly, 5 gaps (T1.3, T1.7, T1.8, T1.9,
T1.10). 4 of the 5 gaps repeat earlier posts (R2.3, P3, Open 1). New
gap: T1.8 tables in PDFs. Closing ad ignored.

## Post — "AI Engineer, 15 questions to practice" (shared 2026-11-22)
Source: a post the user pasted (a recruiter, USA roles). Checked 2026-11-22.
Learning note: be ready to explain your own project: architecture,
challenges, how you solved them.

| # | Question | Status | Where / note |
|---|---|---|---|
| A1 | How does RAG work? | covered | 4.1 (by hand), 4.2 (PDF), 4.3 (chunking) |
| A2 | Reduce LLM hallucinations | partly | 4.1 "I don't know" rule, 3.5 answer check; 4.10 citations + 5.3 judge planned |
| A3 | RAG vs fine-tuning: when which | gap | fine-tuning not in the course; RAG side covered (4.1) |
| A4 | LangChain vs LangGraph | planned | 4.5, 6.5 |
| A5 | Prevent agent loops | planned | 6.7 (loops, max steps), 6.11 (= F13) |
| A6 | When to use multi-agent | planned | 6.9, 6.10 |
| A7 | Handle overfitting | gap | ML basics (Open 1) |
| A8 | Evaluate model performance | partly planned | LLM/RAG: 5.1–5.3; classic ML metrics = gap (= T1.9) |
| A9 | Deploy ML models | planned | 8.1, 8.3, 8.4 (FastAPI + Docker) |
| A10 | Deploy AI models on AWS / Azure | gap | no cloud in the course; Docker 8.4 is the local step |
| A11 | Monitor models in production | partly planned | 5.4 Langfuse; ingest/alerts = gap (= P7) |
| A12 | Optimize inference costs | partly | 2.2 quantization; 4.1–4.3 measured tokens / characters sent; caching = gap |
| A13 | Build an end-to-end AI app | planned | capstone 10.1–10.7 |
| A14 | Reduce LLM latency | partly | 2.2 speeds measured; latency topic = gap (= F14, T2.2) |
| A15 | Secure enterprise AI apps | partly | 3.4 prompt injection + gate covered; 7.7, 8.5 planned |

Count: 1 covered, 6 planned (2 partly), 5 partly, 3 gaps (A3, A7, A10).
A7 repeats Open 1. New gaps: A3 RAG vs fine-tuning, A10 cloud deploy.
Closing ad ignored.

## Interviewer post — "what went wrong?" (shared 2026-11-23)
Source: a post the user pasted (an interviewer of AI engineers). Checked
2026-11-23. Learning note: "everything worked fine" sounds like a tutorial.
Tell what failed, why, what you changed, and the trade-off you accepted.
Your measured numbers are the story.

| # | Question | Status | Where / note |
|---|---|---|---|
| W1 | Biggest problem in your RAG system? | covered | 4.3: cut at 200 characters split 5 of 12 answer sentences ("Each attachment ca" / "n be at most 200 MB") |
| W2 | Retrieval that failed | covered | 4.3: characters 200/0 = 6/12 right 1st; boundaries at 500 = 12/12. 4.1 too |
| W3 | Model gave poor answers | partly | 4.1 "found is not answered"; 5.3 judge planned |
| W4 | Latency became too high | gap | = F14, T2.2 |
| W5 | An approach that didn't work; a decision you changed | covered | 4.3: 9 short-phrase questions showed no difference, so the eval moved to 12 whole answer sentences. DECISIONS.md logs more |
| W6 | A trade-off you accepted | covered | 4.3: meaning cut 12/12 but embeds 93 sentences first (3.9–5.0 s); paragraphs + headings also 12/12, so kept the cheap way |
| W7 | Agent selected the wrong tool | partly | 3.3: model skipped the tool for "A-1001"; 6.2, 6.11 planned |
| W8 | Did you compare embedding models? | covered | 4.4 part 3: nomic-embed-text vs all-MiniLM-L6-v2 on the 4.3 eval: both 12/12; 768 vs 384 numbers, MiniLM ~2x faster, but it drops text after 256 word pieces. Harder eval: 5.2 |
| W9 | How did you know it improved? | partly | 4.3: 12-question eval, same score in 2 runs; 5.1–5.2 planned |

Count: 5 covered, 3 partly, 1 gap (W4 repeats F14; W8 covered by 4.4, 2026-11-25).
Closing ad ignored.

## Open (user to decide)
1. Add an "ML basics" block: learning types, KNN, SVM, pandas +
   scikit-learn (missing values, train, evaluate), Transformer attention,
   stemming. Rough guess ~10–12 h (not measured), Intermediate level,
   right after Basic.
2. Add Kubernetes basics (~3 h guess) to phase 08.
3. From the 2026-11-18 post: a "how a model reads a prompt" topic after
   2.1 (Transformer, attention, prefill, KV cache; ~2 h guess), and
   SQL + latency/caching basics (~3 h guess). Item 1 already holds attention.
4. From the 2026-11-19 post: add "production ingestion" to 4.4 or 10.2 —
   content-hash ids, doc_id + version, delete stale, idempotent re-run,
   per-user filter, ingest counts (~2–3 h guess). Closes P2–P6.
   4.4 (2026-11-25) covers part: stable ids, re-run embeds only new ids,
   update one chunk, metadata filter. Still open: content hash, version,
   delete stale, per-user filter.
5. From the 2026-11-21 post: tables in PDFs (T1.8) in 4.3 or 4.11, and
   an "inference + serving" topic in phase 08 (KV cache, batching,
   distillation, vLLM, latency metrics, autoscaling; ~3 h guess).
6. From the 2026-11-22 post: "RAG vs fine-tuning" as a short concept
   section (when each fits, cost, data needed; ~1 h guess, could sit in
   4.6 or 10.1), and cloud deploy basics, one of AWS / Azure, after 8.4
   (~3 h guess).
7. From the 2026-11-23 post: compare 2 embedding models on the 4.3 eval
   (done in 4.4, 2026-11-25), and a "what went wrong" line per topic
   in REVIEW (failure, why, fix, trade-off) to tell in interviews (~0 h,
   written when a topic finishes).
If yes: add to TOPICS + PLAN, and log it in DECISIONS.
