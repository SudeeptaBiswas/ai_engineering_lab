"""Replace each `...` with code. Run until every line says PASS.
Checks 1-11 need nothing. Checks 12-14 need Ollama with qwen3:1.7b."""

import math  # pyright: ignore[reportUnusedImport] — math.exp
import random  # random.Random(seed). Java: new Random(seed)
from typing import Any  # "any type". Java: Object

import httpx  # pyright: ignore[reportUnusedImport] — until you use it

from lab_tools.check import check  # numbered PASS/FAIL + path:line links
from lab_tools.log import debug, log  # pyright: ignore[reportUnusedImport]

OLLAMA_URL = "http://127.0.0.1:11434"  # not "localhost": 2 s slower on Windows
MODEL = "qwen3:1.7b"

Message = dict[str, str]  # {"role": ..., "content": ...} (lesson 2.3)
Probs = dict[str, float]  # word -> probability, e.g. {"cat": 0.63, "mat": 0.37}


# ---------- Sampling by hand (no HTTP) ----------
def softmax_t(word_to_score: dict[str, float], temperature: float) -> Probs:
    """Softmax of score / temperature (example part 1, section 1).
    Edge case: temperature 0 -> top word 1.0, every other word 0.0
    (Ollama's "greedy"). Do not divide by zero."""
    word_to_exp: dict[str, float] = {}
    if temperature < 0:
        raise ValueError("Temperature cannot be negative")

    # Handle greedy sampling
    if temperature == 0:
        best_word = top_k(word_to_score, 1)
        probs: Probs = {
            word: 1.0 if word == list(best_word.keys())[0] else 0.0
            for word in word_to_score
        }
        return probs
    for word in word_to_score:
        word_to_exp[word] = math.exp(word_to_score[word] / temperature) # the only new part
    exp_total = sum(word_to_exp.values())
    word_to_prob: dict[str, float] = {}
    for word in word_to_exp:
        word_to_prob[word] = word_to_exp[word] / exp_total
    # --- explicit end ---
    # concise: exps = {w: math.exp(s / temperature) for w, s in word_to_score.items()}
    #          return {w: e / sum(exps.values()) for w, e in exps.items()}
    #          {k: v for ...} = a "dict comprehension": builds a dict in one line
    return word_to_prob


def top_k(word_to_prob: Probs, k: int) -> Probs:
    """Keep the k most likely words, rescaled to add up to 1.
    k bigger than the number of words -> keep them all."""
    ranked_words = sorted(word_to_prob, key=lambda word: word_to_prob[word], reverse=True)
    kept_words = ranked_words[:k]  # [:k] = first k items. Java: subList(0, k)
    kept_total = sum(word_to_prob[word] for word in kept_words)
    return {word: word_to_prob[word] / kept_total for word in kept_words}


def top_p(word_to_prob: Probs, p: float) -> Probs:
    """Biggest first, add words until their total reaches p. Rescale."""
    ranked_words = sorted(word_to_prob, key=lambda word: word_to_prob[word], reverse=True)
    kept_words: list[str] = []
    running_total = 0.0
    for word in ranked_words:
        kept_words.append(word)
        running_total += word_to_prob[word]
        if running_total >= p:  # covered enough: stop
            break
    # --- explicit end ---
    return {word: word_to_prob[word] / running_total for word in kept_words}


def pick(word_to_prob: Probs, rng: random.Random) -> str:
    """One weighted random word. Hint: rng.choices(words, weights=...)[0]"""
    words = list(word_to_prob)
    weights = list(word_to_prob.values())
    return rng.choices(words, weights=weights)[0]  # choices returns a list of 1


def picks(word_to_prob: Probs, seed: int, count: int) -> list[str]:
    """`count` picks from ONE random.Random(seed). Same seed -> same list."""
    seeded_rng = random.Random(seed)  # a fresh generator, started from `seed`
    return [pick(word_to_prob, seeded_rng) for _ in range(count)]


# ---------- Sampling in Ollama (real calls) ----------
def sampling_body(messages: list[Message], temperature: float,
                  seed: int | None, max_tokens: int) -> dict[str, Any]:
    """The 2.3 chat body (stream False, think False) whose "options" hold
    "temperature", "num_predict" and — only when seed is not None — "seed".
    `int | None` = an int or nothing. Java: Integer that may be null."""
    options = {"temperature": temperature, "num_predict": max_tokens}
    if seed is not None:
        options["seed"] = seed
    body: dict[str, Any] = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "think": False,  # qwen3: no hidden reasoning (lesson 2.3, section 4)
        "options": options,  # the sampling knobs go here, next to num_predict
    }
    return body


def ask(messages: list[Message], temperature: float,
        seed: int | None = None, max_tokens: int = 10) -> str:
    """POST /api/chat with sampling_body -> the answer, .strip()-ed."""
    body = sampling_body(messages, temperature, seed, max_tokens)
    reply = httpx.post(OLLAMA_URL + "/api/chat", json=body, timeout=120.0).json()
    return reply["message"]["content"].strip()


def distinct_answers(messages: list[Message], temperature: float, runs: int) -> int:
    """Ask `runs` times (no seed). How many DIFFERENT answers came back?
    Hint: a set keeps one copy of each. Java: new HashSet<>()"""
    response_list = [ask(messages, temperature) for _ in range(runs)]
    return len(dict.fromkeys(response_list))


# ---------- Test data ----------
SCORES = {"cat": 2.0, "mat": 1.0, "rat": 0.5}  # same as the example
PROBS = {"cat": 0.63, "mat": 0.23, "rat": 0.14}  # softmax of SCORES at T = 1
PET = [  # an open question: many good answers, so temperature shows
    {"role": "system", "content": "Reply with one word only."},
    {"role": "user", "content": "Invent an unusual name for a pet cat."},
]


def rounded(word_to_prob: Probs) -> Probs:
    """Round each probability to 2 decimals, so checks can use ==."""
    return {word: round(prob, 2) for word, prob in word_to_prob.items()}


# Runs only when you run this file directly (like public static void main)
if __name__ == "__main__":
    check("softmax T=1", lambda: rounded(softmax_t(SCORES, 1.0)), PROBS)
    check("softmax T=0.5", lambda: rounded(softmax_t(SCORES, 0.5)),
          {"cat": 0.84, "mat": 0.11, "rat": 0.04})
    check("softmax T=0", lambda: softmax_t(SCORES, 0), {"cat": 1.0, "mat": 0.0, "rat": 0.0})
    check("top_k 2", lambda: rounded(top_k(PROBS, 2)), {"cat": 0.73, "mat": 0.27})
    check("top_k too big", lambda: rounded(top_k(PROBS, 5)), PROBS)
    check("top_p 0.8", lambda: rounded(top_p(PROBS, 0.8)), {"cat": 0.73, "mat": 0.27})
    check("top_p 0.5", lambda: rounded(top_p(PROBS, 0.5)), {"cat": 1.0})
    check("pick sure", lambda: pick({"cat": 1.0, "mat": 0.0}, random.Random(1)), "cat")
    check("picks seed", lambda: picks(PROBS, 7, 8) == picks(PROBS, 7, 8), True)
    check("body", lambda: sampling_body(PET, 0.7, None, 5),
          {"model": MODEL, "messages": PET, "stream": False, "think": False,
           "options": {"temperature": 0.7, "num_predict": 5}})
    check("body seed", lambda: sampling_body(PET, 0.7, 42, 5)["options"]["seed"], 42)
    ask(PET, 0.0)  # warm-up: 1st call after model load can differ, even at T=0
    check("T=0 same", lambda: distinct_answers(PET, 0.0, 3), 1)
    check("seed same", lambda: ask(PET, 1.5, seed=42) == ask(PET, 1.5, seed=42), True)
    check("T=1.5 varies", lambda: distinct_answers(PET, 1.5, 5) > 1, True)
