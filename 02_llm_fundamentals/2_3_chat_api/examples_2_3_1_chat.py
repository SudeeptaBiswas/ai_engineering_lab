"""Part 1 of 2: one chat call, roles, and why the model has no memory.

Needs Ollama running with qwen3:1.7b (`ollama list`). Takes ~20 s.
"""

import time  # time.perf_counter() = a stopwatch in seconds. Java: System.nanoTime()

import httpx  # HTTP client (lesson 1.7)

CHAT_URL = "http://127.0.0.1:11434/api/chat"  # 127.0.0.1, not localhost (1.7)
MODEL = "qwen3:1.7b"

# ---------- 1. Messages = a list of {role, content} ----------
# system    = rules for the whole chat (the model reads it first)
# user      = what the person typed
# assistant = what the model answered earlier
messages = [
    {"role": "system", "content": "Answer in one short sentence."},
    {"role": "user", "content": "What is RAG?"},
]

# ---------- 2. One call, no streaming ----------
body = {
    "model": MODEL,
    "messages": messages,
    "stream": False,  # one JSON reply at the end. Default is True (part 2)
    "think": False,  # qwen3 "thinks" first unless told not to (section 4)
    "options": {"num_predict": 60},  # max tokens to write. Java: a hard limit
}
start = time.perf_counter()
reply = httpx.post(CHAT_URL, json=body, timeout=120.0).json()  # slow: big timeout
seconds = time.perf_counter() - start

print("answer:", reply["message"]["content"])  # the text
print("role:  ", reply["message"]["role"])  # always "assistant"
print("done_reason:", reply["done_reason"])  # "stop" = finished, "length" = cut
# Durations are in NANOseconds: 1 s = 1_000_000_000 ns
print(f"tokens in: {reply['prompt_eval_count']}, out: {reply['eval_count']}, "
      f"load: {reply['load_duration'] / 1e9:.1f} s, wall clock: {seconds:.1f} s")

# ---------- 3. No memory: every call starts from zero ----------
# The model keeps NOTHING between calls. A "chat" works because YOU send the
# whole history every time. Java view: a stateless REST service.
question = {"role": "user", "content": "What is my favourite colour? One word."}
no_history = [messages[0], question]
with_history = [
    messages[0],
    {"role": "user", "content": "My favourite colour is green."},
    {"role": "assistant", "content": "Nice, green is a calm colour."},
    question,
]
for name, history in [("no history", no_history), ("with history", with_history)]:
    body = {"model": MODEL, "messages": history, "stream": False, "think": False,
            "options": {"num_predict": 20}}
    answer = httpx.post(CHAT_URL, json=body, timeout=120.0).json()["message"]["content"]
    print(f"\n{name:<13}->", answer.strip())

# ---------- 4. Thinking (qwen3) ----------
# Without "think": False, qwen3 first writes its reasoning into a separate
# field, message.thinking. Those tokens count against num_predict, so with a
# small limit the real answer comes back EMPTY.
body = {"model": MODEL, "messages": messages, "stream": False,
        "options": {"num_predict": 60}}  # no "think" key
reply = httpx.post(CHAT_URL, json=body, timeout=120.0).json()
print("\nthinking on -> content:", repr(reply["message"]["content"]))
print("              thinking:", repr(reply["message"].get("thinking", "")[:70]), "...")
print("              done_reason:", reply["done_reason"])
