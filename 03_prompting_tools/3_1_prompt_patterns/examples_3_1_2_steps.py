"""Part 2 of 2: step-by-step. Same 6 word problems, 3 ways. Needs Ollama + qwen3:1.7b.

Run (~2 min):
  uv run python 03_prompting_tools/3_1_prompt_patterns/examples_3_1_2_steps.py

  1. direct       : "Reply with only the final number."
  2. step-by-step : "Solve step by step ... last line: Answer: <number>"
  3. think=True   : the model's own hidden thinking (lesson 2.3), 2 problems only (slow)
"""

import time  # time.perf_counter() = a stopwatch. Java: System.nanoTime()

import httpx  # HTTP client (lesson 1.7)

OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "qwen3:1.7b"
DIRECT_RULES = "Reply with only the final number."
STEP_RULES = "Solve step by step. Write each step on its own line. End with a last line: Answer: <number>"

Message = dict[str, str]  # {"role": ..., "content": ...}

PROBLEMS = [
    {"question": "A shop has 23 apples. It sells 9, then gets 3 boxes of 12. How many apples now?",
     "answer": "50"},
    {"question": "Tom is 3 times as old as Ana. In 4 years Tom will be twice as old as Ana. "
                 "How old is Ana now?", "answer": "4"},
    {"question": "I buy 4 pens at 1.25 each and 2 notebooks at 3.50 each. I pay with 20. "
                 "How much change do I get?", "answer": "8"},
    {"question": "A tank holds 120 liters and is 3/4 full. 25 liters are used. How many liters are left?",
     "answer": "65"},
    {"question": "A hall has 5 rows of 7 chairs. 8 chairs are removed, then 3 rows of 4 chairs "
                 "are added. How many chairs now?", "answer": "39"},
    {"question": "A book has 150 pages. Sara reads 12 pages a day for 9 days. How many pages are left?",
     "answer": "42"},
]


def ask(rules: str, question: str, think: bool) -> tuple[str, int]:
    """One POST /api/chat at temperature 0, whole reply at once.

    Args:
        rules: the system message, e.g. STEP_RULES.
        question: e.g. PROBLEMS[0]["question"].
        think: True = let qwen3 think first (hidden text, 2.3).
    Returns:
        (answer text, tokens the model wrote). Thinking tokens count too.
    """
    messages: list[Message] = [{"role": "system", "content": rules}, {"role": "user", "content": question}]
    # thinking needs room: ~350-1100 tokens measured, so a bigger num_predict
    max_tokens = 400
    if think:
        max_tokens = 1500
    options = {"temperature": 0, "seed": 42, "num_predict": max_tokens}
    body = {"model": MODEL, "messages": messages, "stream": False, "think": think, "options": options}
    response = httpx.post(f"{OLLAMA_URL}/api/chat", json=body, timeout=600.0)
    response.raise_for_status()
    reply = response.json()
    return reply["message"]["content"], reply["eval_count"]


def last_line(text: str) -> str:
    """The last non-empty line, cut to 50 characters, to show how an answer ends.

    Args:
        text: e.g. "23 - 9 = 14\\n14 + 36 = 50\\n\\nAnswer: 50".
    Returns:
        e.g. "Answer: 50".
    """
    lines = text.strip().splitlines()  # split at "\n". Java: text.strip().lines().toList()
    if not lines:
        return ""
    return lines[-1][:50]  # [-1] = last item. Java: list.get(list.size() - 1)


def run(name: str, rules: str, think: bool, problems: list[dict[str, str]]) -> None:
    """Ask every problem one way; print how each answer ends + time and tokens.

    Args:
        name: e.g. "2. step-by-step".
        rules: system message for this way.
        think: passed to ask().
        problems: e.g. PROBLEMS or PROBLEMS[:2] (first 2).
    """
    start = time.perf_counter()
    total_tokens = 0
    for problem in problems:
        result = ask(rules, problem["question"], think)  # a tuple of 2 values
        answer = result[0]
        tokens = result[1]
        # --- explicit end ---
        # concise: answer, tokens = ask(rules, problem["question"], think)
        total_tokens += tokens
        # :>3 = pad to 3 characters, right-aligned. Java: String.format("%3s", ...)
        print(f"  want {problem['answer']:>3}, {tokens:>4} tokens, ends {last_line(answer)!r}")
    print(f"{name}: {time.perf_counter() - start:.1f} s, {total_tokens} tokens written\n")


if __name__ == "__main__":  # Java: public static void main
    ask(DIRECT_RULES, "hi", False)  # load the model first, so timings are fair
    run("1. direct", DIRECT_RULES, False, PROBLEMS)
    run("2. step-by-step", STEP_RULES, False, PROBLEMS)
    run("3. think=True (first 2)", DIRECT_RULES, True, PROBLEMS[:2])  # [:2] = first 2 items
