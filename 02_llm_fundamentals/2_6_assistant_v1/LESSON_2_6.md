# 2.6 Project: assistant v1, a CLI chatbot with memory (~2 h)

The first version of the one real app, [assistant/](../../assistant/).
It grows to v10 (PLAN.md): v2 adds tools (3.3), v3 RAG (4.6), v5 agents (6.4).

All numbers **measured on BISWAS** (i5-1135G7, no GPU), Ollama 0.40.14,
qwen3:1.7b, 2026-11-09, one run each unless a range is given.

## The question of this lesson
In 2.3 the "memory" test was a list you typed by hand: `COLOUR = [...]`.
A real chat has no fixed list. Every turn adds 2 messages: your question
and the model's answer. So:
- Who keeps that list, and how big may it get?
- What happens when it gets too big?

## Java → Python map
| Java | Python |
|---|---|
| `record Message(String role, String content)` | `class Message(TypedDict)` |
| `Iterator<String>` + `next()` | a generator: a function with `yield` |
| try-with-resources (`AutoCloseable`) | `with ... as x:` (+ `@contextmanager` for fakes) |
| `scanner.nextLine()` | `input("you> ")` |
| `NoSuchElementException` at end of input | `EOFError` (Ctrl+Z on Windows, Ctrl+D) |
| `java -jar app.jar` (Main-Class) | `python -m assistant` (runs `assistant/__main__.py`) |
| `UnsupportedOperationException` | `raise NotImplementedError` (the stubs) |

## 1. Memory = you resend the history, and it grows
The model keeps nothing between calls (2.3). Part 1 resends the full
history for 4 turns. `prompt_eval_count` = tokens the model really read:

| Turn | Question | Tokens read | Estimate (chars / 4, from 2.1) |
|---|---|---|---|
| 1 | My favourite colour is green. | 33 | 16 |
| 2 | What is RAG? | 53 | 24 |
| 3 | Name one fruit. | 101 | 79 |
| 4 | What is my favourite colour? | 122 | 91 → answer "Green." |

- Each turn costs more tokens **and** more time: a 4131-token prompt took
  **91.5 s** on this PC. The chat slows down as it grows.
- The estimate is **low**: real was 1.2–2.2x. Roles and chat markers cost
  tokens too. So the budget must leave room.

## 2. Too big? Ollama cuts, and says nothing
Same chat (fact, then ~1600 tokens of filler, then the question), two
context sizes (`num_ctx` = how many tokens the model can see, 2.1):

| `num_ctx` | Tokens read | Answer |
|---|---|---|
| 4096 | 1611 | "green" ✔ |
| 1024 | **35** | "Blue" ✘, made up |

- No error, no warning. Ollama dropped the whole long message and kept
  only the system message + the last question.
- `ollama ps` shows the default here: **4096**. A 4131-token prompt with
  the default gave "Red." the same way.
- So the app trims **itself**, on purpose, before Ollama does it blindly.
  It also sends `num_ctx` explicitly, so the limit is in the code and not
  a hidden default.

> ▶ **Now run part 1** (needs Ollama, ~31 s): see both tables come out live.
> `uv run python 02_llm_fundamentals/2_6_assistant_v1/examples_2_6_1_context.py`

## 3. TypedDict: a dict with known keys
Up to now a message was `dict[str, str]`, so `{"role": "user", "contnet": "hi"}`
passed pyright and failed later at Ollama. A `TypedDict` lists the keys:
pyright flags the typo while you type. At runtime it's still a plain `dict`,
so `httpx` sends it as JSON just like before. (Pydantic, 1.6, adds checks
at **runtime** too; that's for model output in 3.2.)

## 4. Generators: `yield`
`stream_chat()` must hand out chunks **while** they arrive, so the CLI can
print each one right away. A function with `yield` does that:
- Calling it runs nothing. It returns a generator.
- Each `for` step runs the body up to the next `yield` and pauses there.
- One pass only: a second loop gets nothing (like a Java `Iterator`).

In 2.3, `ask_stream` collected a whole list first. A generator gives the
same chunks but starts printing at the first one. LangChain streaming (04)
and agents (06) use the same pattern.

> ▶ **Now run part 2** (no Ollama): TypedDict, "making / got" taking turns,
> stream lines → chunks.
> `uv run python 02_llm_fundamentals/2_6_assistant_v1/examples_2_6_2_yield.py`

## 5. The app: 3 files, one job each
```
you type ──> cli.py main()        loop, commands /reset /exit, errors
               │  answer()        one turn: add → stream → print → add
               ▼
           memory.py ChatMemory   history + trim to MAX_HISTORY_TOKENS
               │  messages()
               ▼
           ollama_client.py       chat_body → POST /api/chat → yield chunks
```
- `ChatMemory` keeps the system message **apart** from the history, so
  trimming can never drop the rules.
- `trim()` never drops the newest message: sending nothing is worse.
- Budget: `MAX_HISTORY_TOKENS = 2000` (estimate) + 300 answer tokens.
  2.2x was on tiny messages (fixed cost per message); the long chat was
  1.17x. So 2000 → ~2350 real + 300 fits in `num_ctx` 4096.

## Exercises: make the tests pass
This time the tests are given; **they are the spec**. You write the
`raise NotImplementedError` parts in `assistant/`. Order:

| Step | You write | Tests | Ollama |
|---|---|---|---|
| 1 | [memory.py](../../assistant/memory.py) | [exercises_2_6_1_memory.py](exercises_2_6_1_memory.py): 10 | no |
| 2 | [ollama_client.py](../../assistant/ollama_client.py) | [exercises_2_6_2_client.py](exercises_2_6_2_client.py): 8 + 1 real | 1 test |
| 3 | [cli.py](../../assistant/cli.py) | [exercises_2_6_3_cli.py](exercises_2_6_3_cli.py): 8 fake + 1 real | 1 test |

Run each with `uv run pytest <file> -v`. The cli fakes sit in
[fakes_2_6_3_cli.py](fakes_2_6_3_cli.py). New in the tests (read them):
- `capsys`: a built-in fixture that captures `print()`. Java: a fake `System.out`.
- `monkeypatch.setattr("builtins.input", fake_input)`: typed lines, no keyboard.
- `@contextmanager`: makes the fake `httpx.stream` work with `with`.
- Two bugs from your 2.3 code are tests now: the empty last chunk and
  the missing `raise_for_status()`.

Then talk to it: `uv run python -m assistant`. Try: tell it a fact, ask a
question, ask for the fact, `/reset`, ask again (measured: "Green.", then
made-up "Blue.").

Done = all 3 files pass with `-v`, and the real chat remembers. Reference
solution, measured: **28 passed in 3.32–3.91 s** (3 runs), **26 passed,
2 deselected in 0.11 s** with `-m "not ollama"`. Real chat, 4 turns: 9.3 s.

## v1 limits (fixed later)
- Token counts are estimates. Real counts: `prompt_eval_count` from each reply.
- Trimming drops single messages, so an answer can lose its question.
- If Ollama fails mid-answer, the question stays in memory.
- Memory lives in RAM: quit = forgotten. Saving to disk: a later version.
