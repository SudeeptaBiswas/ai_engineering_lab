# assistant

The one real app of the course. Grows v1 → v10 (see `docs/PLAN.md`).
Code style: `docs/CODE_STYLE.md`.

## Run
From the repo root, with Ollama running and `qwen3:1.7b` pulled:
```
uv run python -m assistant            # the chat
uv run python -m assistant --debug    # the chat + the log of every step
```
Commands: `/reset` forgets the chat, `/exit` or `/quit` ends it.
Try: "Where is my order A-1001?", "What is 4821 * 3967?", "Please refund my order A-1001, 20 dollars."

## Tests
Tests live in the lesson folder of the version that added them:
```
uv run pytest 02_llm_fundamentals/2_6_assistant_v1 03_prompting_tools/3_5_assistant_v2 -v
```
`-m "not ollama"` skips the tests that need a running Ollama.

## Versions
| Version | Adds | Lesson |
|---|---|---|
| v1 | CLI chat with memory: history resent each turn, trimmed to a token budget, streamed answers | 2.6 |
| v2 | 4 tools (multiply, order_status, today, fake refund), the tool loop, a code gate before every tool | 3.3, 3.4 |

## How one turn runs (v2)
```
cli.main            reads a line, handles /reset /exit
chat_turn           answer_one_turn: save question -> model call -> tool calls?
  ollama_client       stream_reply: POST /api/chat, text + tool calls, piece by piece
  tool_gate           find_reason_to_block: may this call run?
  tool_runner         run_tool: check arguments, run, errors as text
  ... model call again with the results, until a reply has no tool calls (max 4)
  answer_check        correct_false_refund_claim: no "refund done" without a real refund
memory              only the question + final (checked) answer are saved
```

## Files
| File | Job |
|---|---|
| `cli.py` | input loop, commands, system prompt |
| `chat_turn.py` | one turn: the tool loop, printing, what goes into memory |
| `ollama_client.py` | `POST /api/chat` with streaming; reads text + tool calls |
| `tools.py` | the 4 tools: arguments models + functions |
| `tool_runner.py` | tool specs for the model; runs a tool, never raises |
| `tool_gate.py` | the rules for which tool calls may run |
| `answer_check.py` | the final answer: corrects a refund claim when no refund ran |
| `memory.py` | `ChatMemory`: system message + history, trimmed |
| `__main__.py` | makes `python -m assistant` work; `--debug` |

## Known limits (measured 2026-11-15, BISWAS)
- In a long chat the model sometimes copies an earlier answer instead of
  calling a tool: "Refund order A-1002, amount 500." as the 5th question
  -> no tool call, but it said the refund was "recorded". The gate only
  sees tool calls, not words (3.4). Alone, the same question was blocked.
  Now `answer_check.py` prints a correction (2 of 2 runs caught it). The
  false text is still shown first: streaming prints before the check.
- The check only knows refunds. Other false claims ("your order shipped")
  are not checked.
- The system prompt is fragile: adding "Answer in 1 to 3 short sentences."
  dropped tool use from 5/5 to 3/5 (see `cli.py`).
