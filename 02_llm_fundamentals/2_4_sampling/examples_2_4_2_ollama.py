"""Part 2 of 2: the same sampling knobs, sent to the real Ollama.

Needs Ollama running with qwen3:1.7b (`ollama list`). Takes ~30 s.
"""

import httpx  # HTTP client (lesson 1.7)

CHAT_URL = "http://127.0.0.1:11434/api/chat"  # 127.0.0.1, not localhost (1.7)
MODEL = "qwen3:1.7b"

# An open question: many good answers, so the sampling settings show.
PET = [
    {"role": "system", "content": "Reply with one word only."},
    {"role": "user", "content": "Invent an unusual name for a pet cat."},
]


def ask(options: dict[str, float | int], messages: list[dict[str, str]] = PET) -> str:
    """One call with these sampling options -> the answer text.
    `float | int` = either type. Java: Number."""
    body = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "think": False,  # qwen3: no hidden reasoning (lesson 2.3, section 4)
        "options": options,  # the sampling knobs go here, next to num_predict
    }
    reply = httpx.post(CHAT_URL, json=body, timeout=120.0).json()
    return reply["message"]["content"].strip()


def five_answers(title: str, options: dict[str, float | int]) -> None:
    answers = [ask(options) for _ in range(5)]  # 5 calls, same settings
    # set(answers) keeps one copy of each. Java: new HashSet<>(answers)
    print(f"{title:<22} {len(set(answers))} different: {answers}")


# ---------- 1. Temperature ----------
# 0   -> acts greedy: the top token every time -> the same answer every time.
# 0.6 -> qwen3's default (`ollama show qwen3:1.7b --parameters`).
# 1.5 -> flatter odds: more surprising names (and more nonsense).
five_answers("temperature 0", {"temperature": 0, "num_predict": 10})
five_answers("temperature 0.6", {"temperature": 0.6, "num_predict": 10})
five_answers("temperature 1.5", {"temperature": 1.5, "num_predict": 10})

# ---------- 2. Seed: random, but repeatable ----------
# Same seed + same settings + same prompt -> same answer, even at 1.5.
# Like random.Random(7) in part 1. Useful for tests and bug reports.
five_answers("temp 1.5 + seed 42", {"temperature": 1.5, "seed": 42, "num_predict": 10})

# ---------- 3. top_k and top_p ----------
# top_k 1 = keep only the top token = greedy, whatever the temperature.
five_answers("temp 1.5 + top_k 1", {"temperature": 1.5, "top_k": 1, "num_predict": 10})
# A small top_p cuts the long tail of odd tokens, so 1.5 calms down.
five_answers("temp 1.5 + top_p 0.1", {"temperature": 1.5, "top_p": 0.1, "num_predict": 10})

# ---------- 4. num_predict: a hard cut, not a "be short" request ----------
# The model does not know the limit. It writes as usual and is stopped
# mid-sentence. To get SHORT answers, ask for them in the prompt.
story = [{"role": "user", "content": "Tell a story about a cat."}]
print("\nnum_predict 12:", repr(ask({"num_predict": 12}, story)))
