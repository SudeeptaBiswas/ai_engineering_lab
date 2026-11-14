# Topics

Hours are estimates, not measured. Done = date finished. Totals feed PROGRESS.md.
Lvl: B = Basic, I = Intermediate, A = Advanced (PLAN.md, Levels).

| ID | Topic | h | Done | Lvl |
|---|---|---|---|---|
| **01** | **Python for Java devs** | **15** | | |
| 1.1 | Setup: uv, venv, project layout, run scripts | 1 | 2026-11-02 | B |
| 1.2 | Syntax vs Java: types, control flow, functions | 2 | 2026-11-02 | B |
| 1.3 | Collections: list, dict, set, tuple, comprehensions | 2 | 2026-11-03 | B |
| 1.4 | Classes, dataclasses (vs Java POJOs) | 2 | 2026-11-03 | B |
| 1.5 | Modules, imports, exceptions | 1.5 | 2026-11-08 | B |
| 1.6 | Type hints + pydantic | 2 | 2026-11-12 | B |
| 1.7 | Files, JSON, HTTP with httpx | 1.5 | 2026-11-06 | B |
| 1.8 | async/await | 2 | | B |
| 1.9 | pytest | 1 | 2026-11-09 | B |
| **02** | **LLM fundamentals** | **9** | | |
| 2.1 | How LLMs work: tokens, context window | 1.5 | 2026-11-05 | B |
| 2.2 | Ollama: install, models, quantization, CPU limits | 1 | 2026-11-05 | B |
| 2.3 | Chat API over HTTP: roles, streaming | 1.5 | 2026-11-06 | B |
| 2.4 | Sampling: temperature, top_p, max tokens | 1 | 2026-11-08 | B |
| 2.5 | Embeddings + similarity | 2 | 2026-11-09 | B |
| 2.6 | Project: CLI chatbot with memory | 2 | 2026-11-11 | B |
| **03** | **Prompting + tool calling** | **8** | | |
| 3.1 | Prompt patterns: system, few-shot, step-by-step | 2 | 2026-11-12 | B |
| 3.2 | Structured output: JSON + pydantic validation | 2 | 2026-11-12 | B |
| 3.3 | Raw tool calling over HTTP | 2.5 | 2026-11-13 | B |
| 3.4 | Prompt injection basics | 1.5 | 2026-11-14 | B |
| **04** | **RAG** | **38** | | |
| 4.1 | RAG by hand: chunk, embed, search with numpy | 5 | | B |
| 4.2 | Loading PDFs, cleaning text | 3 | | B |
| 4.3 | Chunking strategies | 3 | | B |
| 4.4 | Chroma vector DB | 3 | | B |
| 4.5 | LangChain basics: models, prompts, chains | 4 | | B |
| 4.6 | Project: PDF Q&A RAG | 6 | | B |
| 4.7 | Hybrid search: BM25 + vectors | 3 | | I |
| 4.8 | Reranking | 3 | | I |
| 4.9 | Query rewriting, multi-query | 3 | | I |
| 4.10 | Citations + "I don't know" answers | 2 | | I |
| 4.11 | Project: advanced RAG | 3 | | I |
| **05** | **Evals + tracing** | **10** | | |
| 5.1 | Test sets: question/answer pairs | 2 | | B |
| 5.2 | Retrieval metrics: recall@k, MRR | 2 | | B |
| 5.3 | LLM-as-judge: faithfulness, relevance | 3 | | I |
| 5.4 | Langfuse tracing | 3 | | I |
| **06** | **Agents + LangGraph** | **43** | | |
| 6.1 | Agent loop by hand (ReAct) | 5 | | I |
| 6.2 | Tool design: schemas, errors, retries | 3 | | I |
| 6.3 | Memory: short and long term | 3 | | I |
| 6.4 | Project: tool-using agent, no framework | 5 | | A |
| 6.5 | LangGraph basics: state, nodes, edges | 4 | | I |
| 6.6 | Rebuild the agent in LangGraph | 4 | | I |
| 6.7 | Routing, loops, checkpoints | 4 | | I |
| 6.8 | Human-in-the-loop | 3 | | I |
| 6.9 | Multi-agent: supervisor, handoff | 5 | | A |
| 6.10 | Project: multi-agent workflow | 5 | | A |
| 6.11 | Agent evals + failure modes | 2 | | A |
| **07** | **MCP** | **17** | | |
| 7.1 | Concepts: host, client, server; tools, resources, prompts | 2 | | B |
| 7.2 | Transports: stdio, streamable HTTP | 1.5 | | B |
| 7.3 | Project: custom MCP server (Python) | 5 | | B |
| 7.4 | Test with MCP Inspector + an AI client | 1.5 | | B |
| 7.5 | MCP client in Python | 2 | | I |
| 7.6 | Project: LangGraph agent using MCP tools | 4 | | I |
| 7.7 | MCP security: auth, tool permissions | 1 | | I |
| **08** | **Serve + ship** | **13** | | |
| 8.1 | FastAPI: routes, pydantic models | 3 | | B |
| 8.2 | Streaming responses (SSE) | 2 | | I |
| 8.3 | Wrap RAG + agent as an API | 3 | | I |
| 8.4 | Docker + docker compose | 3 | | B |
| 8.5 | Guardrails: input/output checks | 2 | | I |
| **09** | **Java bridge** | **13** | | |
| 9.1 | Spring Boot calls the FastAPI service | 3 | | A |
| 9.2 | Spring AI with Ollama | 4 | | A |
| 9.3 | Java MCP server (MCP Java SDK) | 4 | | A |
| 9.4 | Python vs Java AI stack: when to use which | 2 | | A |
| **10** | **Capstone: enterprise assistant** | **33** | | |
| 10.1 | Design: use case, architecture doc | 3 | | A |
| 10.2 | Knowledge base: RAG ingestion | 6 | | A |
| 10.3 | Agents + MCP tools | 8 | | A |
| 10.4 | API + Spring Boot front door | 5 | | A |
| 10.5 | Evals + tracing | 4 | | A |
| 10.6 | Docker deploy | 3 | | A |
| 10.7 | README, diagrams, demo | 4 | | A |
| | **Total** | **199** | | |
