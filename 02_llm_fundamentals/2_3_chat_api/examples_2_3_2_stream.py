"""Part 2 of 2: streaming, so the answer appears word by word.

Needs Ollama running with qwen3:1.7b (`ollama list`). Takes ~10 s.
"""

import json  # each stream line is one JSON object
import time  # stopwatch

import httpx

CHAT_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen3:1.7b"

body = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "Answer in three short sentences."},
        {"role": "user", "content": "Why do chat apps stream their answers?"},
    ],
    "stream": True,  # the default: many small JSON lines instead of one
    "think": False,
    "options": {"num_predict": 80},
}

# ---------- 1. Read the reply line by line ----------
# httpx.stream(...) does NOT wait for the whole body. iter_lines() gives each
# line the moment it arrives. Java: HttpResponse.BodyHandlers.ofLines()
# Format = NDJSON: one JSON object per line ("newline-delimited JSON").
start = time.perf_counter()
first_chunk_at = 0.0
last: dict[str, object] = {}  # the final line, kept for its stats
print("answer: ", end="")
with httpx.stream("POST", CHAT_URL, json=body, timeout=120.0) as response:
    for line in response.iter_lines():
        if not line:  # skip blank lines, just in case
            continue
        data = json.loads(line)  # {"message": {"content": "R"}, "done": false}
        if first_chunk_at == 0.0:
            first_chunk_at = time.perf_counter() - start
        # end="" = no newline; flush=True = show now, not when the buffer fills
        print(data["message"]["content"], end="", flush=True)
        if data["done"]:  # last line: empty content + the stats
            last = data
total = time.perf_counter() - start

# ---------- 2. Why stream: the user sees text much sooner ----------
print(f"\n\nfirst chunk after {first_chunk_at:.2f} s, whole answer after {total:.2f} s")

# ---------- 3. The last line carries the same stats as stream=False ----------
print("last line keys:", sorted(last))
eval_count = int(str(last["eval_count"]))  # tokens written
eval_seconds = int(str(last["eval_duration"])) / 1_000_000_000  # ns -> s
print(f"speed: {eval_count} tokens / {eval_seconds:.2f} s = {eval_count / eval_seconds:.1f} tokens/s")
