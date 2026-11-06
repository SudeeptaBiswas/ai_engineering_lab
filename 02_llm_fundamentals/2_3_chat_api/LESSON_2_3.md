# 2.3 Chat API over HTTP: roles, streaming (~1.5 h)

Read this, run [examples_2_3_1_chat.py](examples_2_3_1_chat.py) and
[examples_2_3_2_stream.py](examples_2_3_2_stream.py), then solve [exercises_2_3.py](exercises_2_3.py).
All of it calls the **real Ollama** with `qwen3:1.7b` — keep Ollama running.
Why now: this is the call every later lesson builds on (chatbot 2.6, RAG, agents).

All numbers **measured on 10284Sudee** (i5-10210U, no GPU), Ollama 0.40.14,
2026-11-06, one run each unless a range is given.

## Java → Python map
| Java | Python |
|---|---|
| `record Message(String role, String content)` | `{"role": "user", "content": "hi"}` |
| `List<Message>` | `list[dict[str, str]]` |
| `HttpClient.send(req, ofString())` | `httpx.post(url, json=body).json()` |
| `BodyHandlers.ofLines()` (a stream of lines) | `with httpx.stream(...) as r:` + `r.iter_lines()` |
| `System.out.print(x); System.out.flush()` | `print(x, end="", flush=True)` |
| `System.nanoTime()` | `time.perf_counter()` (seconds, as float) |

## 1. Messages and roles
A chat is a **list of messages**. Each has a `role` and `content`:

| Role | Who | Example |
|---|---|---|
| `system` | you, the developer: rules for the whole chat | "Answer in one short sentence." |
| `user` | the person | "What is RAG?" |
| `assistant` | the model's earlier answers | "RAG stands for..." |

## 2. One call: `POST /api/chat`
```python
body = {"model": "qwen3:1.7b", "messages": messages,
        "stream": False, "think": False, "options": {"num_predict": 60}}
reply = httpx.post(f"{OLLAMA_URL}/api/chat", json=body, timeout=120.0).json()
reply["message"]["content"]   # the answer text
```
| Reply field | Means |
|---|---|
| `message.content` | the answer |
| `done_reason` | `"stop"` = finished; `"length"` = hit `num_predict`, cut off |
| `prompt_eval_count` / `eval_count` | tokens read / tokens written |
| `load_duration`, `eval_duration`, `total_duration` | **nanoseconds** (÷ 1_000_000_000 = s) |

- `num_predict` = max tokens to write. Keeps tests fast and costs low.
  (Temperature and other sampling options: lesson 2.4.)
- Model not in RAM yet? The first call also loads it: 6.3 s extra for 1.7b.

## 3. The model has no memory
Every call starts from zero. A "chat" only works because **you** resend the
whole history each time — like a stateless REST service.
Measured (example part 1, "What is my favourite colour?"):
- without the earlier messages → **"Blue."** (it made one up — no "I don't know")
- with them → **"Green."**

So history grows every turn, and so do tokens and time. Trimming it to fit
the context window was lesson 2.1; the chatbot in 2.6 does it for real.

## 4. Thinking: always send `"think": False` (for now)
qwen3 writes hidden reasoning first, into `message.thinking`. Those tokens
count against `num_predict`. "What is RAG?", `num_predict` 60:

| Model | `think` | Time | Result |
|---|---|---|---|
| qwen3:1.7b | not sent | 12.8 s (6.3 s load) | `content` **empty**, all 60 tokens were thinking |
| qwen3:1.7b | `False` | 2.5 s | clean one-sentence answer, 15.2 tokens/s |
| qwen3:4b | not sent | 19.2 s (9.2 s load) | `content` empty |
| qwen3:4b | `False` | 8.5 s | thinking **leaks** into `content` ("Hmm, the user is asking...") |

That is why this lesson uses **qwen3:1.7b**: fast, and `think: False` works.
The 4b leak matches what 2.2 found with the CLI.

## 5. Streaming
`"stream": True` is Ollama's **default**. The reply is NDJSON: one JSON
object per line, each with a few characters of the answer:
```
{"message":{"role":"assistant","content":"R"},"done":false}
{"message":{"role":"assistant","content":"AG"},"done":false}
...
{"message":{"role":"assistant","content":""},"done":true,"done_reason":"length","eval_count":30,...}
```
- The **last** line has `done: true` + the same stats as `stream: False`.
- Why bother: first text after **0.13–0.64 s**, whole answer after **2.0–3.2 s**.
  The user reads while the model writes. Same total time.
- Read it with `httpx.stream("POST", url, json=body, timeout=...)` and
  `iter_lines()`. A plain `httpx.post` waits for the whole body.
- Forget `"stream": False` with `httpx.post` → you get all lines in one
  string and `.json()` fails with "Extra data".

## 6. Exercises
[exercises_2_3.py](exercises_2_3.py): 9 functions, 12 checks. Messages and
stream lines first (no HTTP), then real calls. Reference: 12/12 in 3.1–5.7 s
(5 runs). Needs `qwen3:1.7b` on the PC.
