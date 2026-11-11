# Learning Plan (revised 2026-11-11)

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

## Levels (2026-11-11)
Goal is a job ASAP, so the course runs in three levels. Phases and topic
ids stay; only the order changes. Each topic's level: TOPICS.md, `Lvl`.

| Level | Gives | Then |
|---|---|---|
| Basic | chatbot, prompting + tools, PDF RAG with scores, MCP server, API in Docker | CV + apply |
| Intermediate | advanced RAG, judge + tracing, agent loop + LangGraph agents, MCP client, full API | interviews |
| Advanced | no-framework agent project, multi-agent, Java bridge, capstone | keep going |

Hours and dates per level: [PROGRESS.md](PROGRESS.md).

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

Version numbers stay, build order follows the levels: in Basic the MCP
server (7.3) and API + Docker (8.4) land before v4.

## Learning order (just-in-time Python)
Python topics come right before the lesson that first needs them.
IDs stay as in TOPICS.md; only the order changes.

Done: 1.1 → 1.2 → 1.3 → 1.4 → 2.1 → 2.2 → 1.7 → 2.3 → 2.4 → 1.5 → 2.5 → 1.9

Basic: 2.6 (v1) → 3.1 → 1.6 → 3.2 → 3.3 (v2) → 3.4 → 4.1–4.4 → 5.1 → 5.2
→ 4.5 → 4.6 (v3) → 1.8 → 7.1–7.4 → 8.1 → 8.4 → CV + apply

Intermediate: 5.3 → 4.7 → 4.8 → 5.4 → 4.9–4.11 (v4) → 6.1–6.3 → 6.5–6.8
→ 7.5–7.7 → 8.2 → 8.3 → 8.5

Advanced: 6.4 → 6.9–6.11 → 9.x → 10.x

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
- LESSON md: a "▶ Now run" line (with the command) right after the
  sections each examples file covers, so the md alone guides the order.
- Track in hours + %, not weeks: [PROGRESS.md](PROGRESS.md).
