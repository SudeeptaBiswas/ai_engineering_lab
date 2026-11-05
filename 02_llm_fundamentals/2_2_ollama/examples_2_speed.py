"""Part 2 of 2: how long does an answer take on CPU? Load + read + write.

Pure Python math with numbers MEASURED on 10284Sudee (i5-10210U, no GPU),
from `ollama run <model> --verbose`, 2026-11-05.
"""

# ---------- 1. Measured speed per model ----------
# dict of dicts. Java: Map<String, Map<String, Double>>
MEASURED: dict[str, dict[str, float]] = {
    "qwen3:4b": {
        "file_gb": 2.5,  # `ollama list`
        "load_s": 9.4,  # first call: copy file into RAM
        "write_tps": 7.1,  # "eval rate": answer tokens per second
    },
    "qwen3:1.7b": {
        "file_gb": 1.4,
        "load_s": 1.9,
        "write_tps": 15.4,
    },
}


def answer_seconds(model: str, answer_tokens: int, cold: bool) -> float:
    """Seconds for one answer. cold=True -> model not in RAM yet, add load."""
    stats = MEASURED[model]  # inner dict for this model
    # --- explicit start ---
    seconds = answer_tokens / stats["write_tps"]
    if cold:
        seconds = seconds + stats["load_s"]
    # --- explicit end ---
    # concise: seconds = n / tps + (stats["load_s"] if cold else 0)
    return round(seconds, 1)


# ---------- 2. Short vs long answer, cold vs warm ----------
# A short answer ~ 50 tokens. A page of text ~ 500 tokens (~375 words).
for model in MEASURED:  # looping a dict gives its keys
    for tokens in (50, 500):  # tuple: fixed list of values
        cold = answer_seconds(model, tokens, cold=True)  # cold=... named arg
        warm = answer_seconds(model, tokens, cold=False)
        print(f"{model:<11} {tokens:>3} tokens: cold {cold:>5} s, warm {warm:>5} s")


# ---------- 3. The cost of thinking ----------
# Same question "What is 2+2?", qwen3:4b, measured token counts:
THINKING_TOKENS = 236  # --think=true --hidethinking (thinking hidden, not skipped)
NO_THINK_TOKENS = 54  # "/no_think" at the end of the prompt
rate = MEASURED["qwen3:4b"]["write_tps"]
print(f"\nthinking:  {THINKING_TOKENS} tokens = {THINKING_TOKENS / rate:.0f} s")
print(f"/no_think: {NO_THINK_TOKENS} tokens = {NO_THINK_TOKENS / rate:.0f} s")
# The answer was "4" both times. Thinking only pays off on hard questions.
