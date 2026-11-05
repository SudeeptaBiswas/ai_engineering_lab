# 1.7 Files, JSON, HTTP with httpx (~1.5 h)

Read this, run [examples_1_files_json.py](examples_1_files_json.py) and
[examples_2_http.py](examples_2_http.py), then solve [exercises.py](exercises.py).
Part 2 and the exercises call the **real Ollama** on your PC — keep it running.
Why now: in 2.3 we talk to Ollama over HTTP, with JSON, from Python.

## Java → Python map
| Java | Python |
|---|---|
| `java.nio.file.Path` | `pathlib.Path` |
| `path.resolve("a.txt")` | `path / "a.txt"` |
| `Files.readString(p)` / `writeString` | `p.read_text(encoding="utf-8")` / `write_text` |
| `BufferedReader` + try-with-resources | `with open(p, encoding="utf-8") as f:` |
| `NoSuchFileException` | `FileNotFoundError` |
| Jackson `writeValueAsString` | `json.dumps(obj)` (`indent=2` = pretty) |
| Jackson `readValue` | `json.loads(text)` |
| `HttpClient` | `httpx.Client` (or quick: `httpx.get(...)`) |
| `response.statusCode()` / `body()` | `r.status_code` / `r.text` / `r.json()` |
| `ConnectException` | `httpx.ConnectError` / `ConnectTimeout` (parent: `httpx.TransportError`) |

## 1. Files
- Always write `encoding="utf-8"`. Windows' default is not UTF-8, so text
  with `ü` or `—` breaks without it.
- `with open(...) as f:` closes the file for you, even on an error —
  same idea as try-with-resources.
- Modes: `"r"` read (default), `"w"` write (**wipes** the file first), `"a"` append.
- Small file: `read_text()`. Big file: `for line in f:` reads line by line.

## 2. JSON
JSON maps straight onto Python types — no classes needed:

| JSON | Python |
|---|---|
| `{...}` object | `dict` |
| `[...]` array | `list` |
| `"text"` | `str` |
| `1`, `2.5` | `int`, `float` |
| `true` / `false` / `null` | `True` / `False` / `None` |

`json.loads` returns `Any` (any type, like Java `Object`). Later (1.6,
pydantic) we turn it into typed objects, like Jackson into a POJO.

## 3. HTTP with httpx
```python
response = httpx.get(url, timeout=10.0)          # GET
response = httpx.post(url, json={"model": "x"})  # POST with a JSON body
response.status_code   # 200
response.json()        # body -> dict
```
- `json=...` turns the dict into JSON and sets `Content-Type` for you.
- Always give a `timeout`. A local LLM can be slow: a 500-token answer
  took ~70 s on this PC (lesson 2.2, section 5:
  [02_llm_fundamentals/2_2_ollama/LESSON.md](../../02_llm_fundamentals/2_2_ollama/LESSON.md)).
- **A 404 is not an exception.** Check `status_code`, or call
  `response.raise_for_status()` to throw `httpx.HTTPStatusError`.
- Many calls → one `httpx.Client(base_url=..., timeout=...)` in a `with`
  block. It reuses the connection, like one shared `HttpClient`.

## 4. Two Windows surprises (measured on 10284Sudee)
- `http://localhost:11434` took **2.16 s** per call, `http://127.0.0.1:11434`
  **0.02 s**. "localhost" tries IPv6 first, fails, then waits before using
  IPv4. The exercises went from 25 s to 1.2 s just by this change.
  So this lab always uses `127.0.0.1`.
- Nothing listening on a port → `ConnectTimeout` (after the timeout), not
  `ConnectError`. Catch the parent `httpx.TransportError` to get both.

## 5. Ollama endpoints used here (all fast, no text generation)
| Call | Gives | CLI twin |
|---|---|---|
| `GET /api/version` | `{"version": "0.40.14"}` | `ollama --version` |
| `GET /api/tags` | `{"models": [{"name", "size" (bytes), "details"}, ...]}` | `ollama list` |
| `POST /api/show` `{"model": "qwen3:4b"}` | details, `model_info`, `capabilities`; 404 if missing | `ollama show` |
| `GET /api/ps` | models in RAM now | `ollama ps` |

## 6. Exercises
[exercises.py](exercises.py): 9 functions, 12 checks. Files + JSON first
(temp folder, deleted after), then Ollama calls, then one that combines
all three. Needs `qwen3:4b` on the PC.
