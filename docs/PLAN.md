# Learning Plan (revised 2026-11-01)

Goal: AI Engineer / AI Backend Engineer. Master RAG, Agents, MCP.
Learner: experienced Java dev, new to Python + AI. Learn by building.
Rules: free/open-source first, fundamentals over libraries.
Review notes and reasons for changes: [PLAN_REVIEW.md](PLAN_REVIEW.md).

## Mentor guidance
- Step by step, practical, working code, small exercises.
- Map Python ideas to Java ones where it helps.
- Build each idea by hand first, then with the framework.

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

## Projects (each one: README, demo, tests, small eval)
1. Python exercises (Java-to-Python mapping).
2. Chatbot over Ollama, raw HTTP first.
3. PDF Q&A RAG.
4. Advanced RAG with reranking + eval scores.
5. Tool-using agent, no framework.
6. Same agent in LangGraph, then multi-agent.
7. Custom MCP server (Python).
8. Agent that uses MCP tools.
9. Spring Boot app calling the FastAPI AI service.
10. Capstone, deployed with Docker.

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

## Repo layout (pending decision, see review)
Top-level numbered folders `01_python_fundamentals/` … `10_capstone/`,
plus `docs/`, `resources/`, `pyproject.toml`.
