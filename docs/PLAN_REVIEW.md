# Plan Review (2026-11-01)

Verdict: the plan is solid. The order (Python → LLM → RAG → Agents → MCP) is right.
It needs 10 changes. Revised plan: [PLAN.md](PLAN.md).

## Facts checked on this PC (BISWAS)
- RAM 11.7 GB, Intel Iris Xe (no CUDA GPU) → models run on CPU only.
- Python 3.13.15 installed. Ollama: not installed. uv: not installed.

## Changes
1. **Hardware limit (most urgent).** 7B+ models will be slow on CPU with 11.7 GB RAM.
   Start with 3–4B models that support tools (for example qwen3:4b, llama3.2:3b).
   Speeds not measured yet; measure after installing Ollama.
   Option: a free API tier for agent tests if small models fail at tool calls.
2. **Hours are missing for 6 topics.** Prompting, LangChain, LangGraph, vector DB,
   FastAPI and deployment had no hours. Revised total: 158–235 h (estimate).
3. **No evaluation.** Without evals you can't tell if a RAG change helped.
   Added phase 05: retrieval metrics, LLM-as-judge, Langfuse tracing.
4. **Frameworks too early.** Build the raw version first: tool calling over HTTP,
   then an agent loop in ~50 lines, then LangGraph. This matches "fundamentals first".
5. **Java background unused.** Spring Boot is listed but no project uses it.
   Added phase 09: Spring Boot calls the FastAPI service, plus a Java MCP server.
   This is the portfolio's strongest differentiator.
6. **Python list missing key parts.** Added typing, async/await (MCP and FastAPI need it),
   pydantic, pytest, uv.
7. **Two RAG frameworks.** LangChain and LlamaIndex split your time. Pick LangChain.
8. **Folders 05 agents / 06 langgraph overlap.** Merged into one phase:
   hand-written loop first, then LangGraph.
9. **No safety topic.** Agents and MCP tools can be hijacked through prompt injection.
   Added guardrails to phase 08.
10. **"Done" not defined.** Each project needs a README, demo, tests and a small eval.

## Mismatches with this repo
- The plan names the repo `ai-engineering-lab`; GitHub has `ai_engineering_lab`.
- The plan has top-level numbered folders; the current skeleton has `labs/`.
- The plan uses `requirements.txt`; the review suggests uv + `pyproject.toml`.
