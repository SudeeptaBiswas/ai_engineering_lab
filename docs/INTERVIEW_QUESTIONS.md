# AI system design — interview questions

Source: LinkedIn post (2026-11-13), ad text dropped.
Format: no coding round. "Design an AI system for me" on a whiteboard.
They test how you think, not which framework you like.

## The 10 questions

| # | Question | Covered by |
|---|---|---|
| 1 | Design a production-ready RAG system. | 4.1–4.11, 10.2 |
| 2 | When would you choose RAG over fine-tuning? | gap |
| 3 | How would you reduce latency without hurting quality? | 8.2 (streaming); rest gap |
| 4 | What happens if your LLM provider goes down? | 6.2 (retries); fallback gap |
| 5 | How do you evaluate an AI system (after deploy too)? | 5.1–5.4, 6.11 |
| 6 | Where would you add caching? | gap |
| 7 | How do you prevent hallucinations? | 4.10, 5.3, 8.5 |
| 8 | What would you monitor in production? | 5.4 |
| 9 | How would you scale to millions of documents? | 4.4; rest gap |
| 10 | Draw the full architecture, user query → final response. | 10.1, 10.7 |

## Follow-ups they asked
- Where would you store documents?
- How would retrieval work?

## Use
Practice each out loud before the Phase 2 "interviews" milestone (PLAN.md).
Gaps: decide later whether to add topics.
