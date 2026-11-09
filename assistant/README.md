# assistant

The one real app of the course. Grows v1 → v10 (see `docs/PLAN.md`).

## Run
From the repo root, with Ollama running and `qwen3:1.7b` pulled:
```
uv run python -m assistant
```
Commands: `/reset` forgets the chat, `/exit` or `/quit` ends it.

## Tests
Tests live in the lesson folder of the version that added them:
```
uv run pytest 02_llm_fundamentals/2_6_assistant_v1 -v
```
`-m "not ollama"` skips the tests that need a running Ollama.

## Versions
| Version | Adds | Lesson |
|---|---|---|
| v1 | CLI chat with memory: history resent each turn, trimmed to a token budget, streamed answers | 2.6 |

## Files (v1)
| File | Job |
|---|---|
| `cli.py` | input loop, commands, one turn = `answer()` |
| `memory.py` | `ChatMemory`: system message + history, trimmed |
| `ollama_client.py` | `POST /api/chat` with streaming, yields text chunks |
| `__main__.py` | makes `python -m assistant` work |
