# Learning Plan (revised 2026-11-01)

Goal: AI Engineer / AI Backend Engineer. Master RAG, Agents, MCP.
Learner: experienced Java dev, new to Python + AI. Learn by building.
Rules: free/open-source first, fundamentals over libraries.
Review notes and reasons for changes: [PLAN_REVIEW.md](PLAN_REVIEW.md).

## Mentor guidance
- Step by step, practical, working code, small exercises.
- Map Python ideas to Java ones where it helps.
- Comment lesson code line by line: what it does + the Java equivalent.
  Explain every new symbol or trick (lambda, `!r`, `**`, decorators).
- Every function gets a Javadoc-style docstring: one line on what it does,
  then `Args:` / `Returns:` / `Raises:` (= `@param` / `@return` / `@throws`),
  each with a real example value.
- Build each idea by hand first, then with the framework.
- Every new idea: real example first, then how it links to earlier and
  later lessons, then a short definition. Never a bare definition.

## Phases and hours
Hours are rough estimates, not measured. (*) = added in the review.

| # | Phase | Hours |
|---|---|---|
| 01 | Python for Java devs (+ typing, async, pydantic, pytest, uv) | 12–18 |
| 02 | LLM fundamentals (tokens, sampling, context, embeddings) | 8–10 |
| 03 | Prompting + structured output + raw tool calling (*) | 6–10 |
| 04 | RAG: by hand, then LangChain, then reranking | 30–45 |
| 05 | Evals + tracing: RAG metrics, LLM-as-judge, Langfuse (*) | 8–12 |
| 06 | Agents: hand-written loop, then LangGraph | 35–50 |
| 07 | MCP: server, client, agent using MCP tools | 14–20 |
| 08 | Serve + ship: FastAPI, Docker, guardrails (*) | 10–15 |
| 09 | Java bridge: Spring Boot calls the AI service; Java MCP server (*) | 10–15 |
| 10 | Capstone: enterprise assistant (RAG + agents + MCP) | 25–40 |
| | **Total** | **158–235** |

## One growing project: `assistant/`
Learn a topic → add it to the same app. Each version: README note, tests, demo.
Lesson folders hold exercises; `assistant/` holds the real app.

| Version | Adds | After topic |
|---|---|---|
| v1 | CLI chatbot with memory (raw HTTP to Ollama) | 2.6 |
| v2 | Structured output + tool calling | 3.3 |
| v3 | RAG over PDFs | 4.6 |
| v4 | Hybrid search, reranking, eval scores | 4.11 + 5 |
| v5 | Agent loop, no framework | 6.4 |
| v6 | LangGraph, multi-agent | 6.10 |
| v7 | MCP server + MCP tools in the agent | 7.6 |
| v8 | FastAPI + Docker + guardrails | 8.5 |
| v9 | Spring Boot front door, Java MCP server | 9.3 |
| v10 | Capstone polish: enterprise use case, docs, demo | 10.7 |

## Learning order (just-in-time Python)
Python topics come right before the lesson that first needs them.
IDs stay as in TOPICS.md; only the order changes.

1.1 → 1.2 → 1.3 → 1.4 → 2.1 → 2.2 → 1.7 → 2.3 → 2.4 → 1.5 → 2.5 → 1.9 → 2.6 (v1)
→ 3.1 → 1.6 → 3.2 → 3.3 (v2) → 3.4 → 4.1–4.4 → 5.1 → 5.2 → 4.5 → 4.6 (v3)
→ 5.3 → 4.7 → 4.8 → 5.4 → 4.9–4.11 (v4) → 6.1–6.4 (v5) → 6.5–6.11 (v6)
→ 1.8 → 7.1–7.7 (v7) → 8.x (v8) → 9.x (v9) → 10.x (v10)

## Stack
| Purpose | Choice |
|---|---|
| Python env | uv (lockfile, like Maven) |
| Local LLM | Ollama; small models first (see review: hardware) |
| Framework | LangChain (one framework; skip LlamaIndex at first) |
| Agents | LangGraph |
| Vectors | Chroma; FAISS for in-memory demos |
| MCP | Official MCP Python SDK; MCP Java SDK in phase 09 |
| API | FastAPI |
| Tracing | Langfuse (self-hosted, open-source) |
| Tests | pytest |

## Repo layout (decided)
Repo stays `ai_engineering_lab`. One top-level folder per phase,
created when the phase starts: `01_python_fundamentals/` … `10_capstone/`.
Plus `docs/`, `resources/`, `pyproject.toml`, `uv.lock`.

## How we work
- Learn and build: every topic adds something real to `assistant/`.
- Follow the learning order below; Python is learned when needed.
- Evals (05) are woven into RAG (04).
- Each session: one small piece → test → commit → push.
- Lesson code: explicit first, concise form in a `# concise:` comment
  (see DECISIONS.md, 2026-11-04).
- Lesson code: full descriptive names; comments say what a variable holds
  and what each expression does.
- These lesson rules are checked by `lab_tools/lesson_rules.py` on every
  edit and commit (DECISIONS.md, 2026-11-09).
- Track in hours + %, not weeks: [PROGRESS.md](PROGRESS.md).
