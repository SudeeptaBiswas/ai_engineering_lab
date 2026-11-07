"""Part 1 of 2: sampling by hand: temperature, top_k, top_p, seed.

No Ollama needed. Same reading rule as 2.1: code between "explicit start/end"
is the long way; the "# concise:" line right after it is the short Python way.
"""

import math  # math.exp. Java: Math.exp
import random  # random.Random(seed) = Java new Random(seed)

# Scores a model might give the word after "the" (same as 2.1 part 3).
word_to_logit = {"cat": 2.0, "mat": 1.0, "rat": 0.5}


# ---------- 1. Temperature: divide every score by T, then softmax ----------
# T < 1 -> big scores get bigger: the top word wins more often (safe, boring).
# T > 1 -> scores move closer: rare words get picked more (creative, risky).
def softmax_with_temperature(word_to_score: dict[str, float], temperature: float) -> dict[str, float]:
    """{'cat': 2.0, 'mat': 1.0, 'rat': 0.5}, T=1  ->  {'cat': 0.63, 'mat': 0.23, 'rat': 0.14}"""
    # --- explicit start ---
    word_to_exp: dict[str, float] = {}
    for word in word_to_score:
        word_to_exp[word] = math.exp(word_to_score[word] / temperature)  # the only new part
    exp_total = sum(word_to_exp.values())
    word_to_prob: dict[str, float] = {}
    for word in word_to_exp:
        word_to_prob[word] = word_to_exp[word] / exp_total
    # --- explicit end ---
    # concise: exps = {w: math.exp(s / temperature) for w, s in word_to_score.items()}
    #          return {w: e / sum(exps.values()) for w, e in exps.items()}
    #          {k: v for ...} = a "dict comprehension": builds a dict in one line
    return word_to_prob


def show(title: str, word_to_prob: dict[str, float]) -> None:
    # :<14 = pad to 14 chars; :.2f = 2 decimals. Java: String.format("%-14s", ...)
    parts = [f"{word} {prob:.2f}" for word, prob in word_to_prob.items()]
    print(f"{title:<14}", "   ".join(parts))


for temperature in [0.2, 0.5, 1.0, 2.0]:
    show(f"T = {temperature}", softmax_with_temperature(word_to_logit, temperature))
# T = 0 would divide by zero. Ollama treats 0 as "always take the top word"
# (greedy), the same as 2.1's most_frequent.

probs = softmax_with_temperature(word_to_logit, 1.0)


# ---------- 2. top_k: keep only the k most likely words ----------
def top_k(word_to_prob: dict[str, float], k: int) -> dict[str, float]:
    """Keep the k biggest, then rescale so they add up to 1 again."""
    # sorted(..., key=..., reverse=True) = biggest first.
    # Java: list.sort(Comparator.comparing(...).reversed())
    ranked_words = sorted(word_to_prob, key=lambda word: word_to_prob[word], reverse=True)
    kept_words = ranked_words[:k]  # [:k] = first k items. Java: subList(0, k)
    kept_total = sum(word_to_prob[word] for word in kept_words)
    return {word: word_to_prob[word] / kept_total for word in kept_words}


show("top_k = 2", top_k(probs, 2))  # 'rat' can never be picked now


# ---------- 3. top_p: keep the smallest top group that covers p ----------
# Also called "nucleus sampling". Unlike top_k, the group size changes:
# one sure word -> group of 1; many close words -> big group.
def top_p(word_to_prob: dict[str, float], p: float) -> dict[str, float]:
    """Add words, biggest first, until their total reaches p. Rescale."""
    ranked_words = sorted(word_to_prob, key=lambda word: word_to_prob[word], reverse=True)
    # --- explicit start ---
    kept_words: list[str] = []
    running_total = 0.0
    for word in ranked_words:
        kept_words.append(word)
        running_total += word_to_prob[word]
        if running_total >= p:  # covered enough: stop
            break
    # --- explicit end ---
    return {word: word_to_prob[word] / running_total for word in kept_words}


show("top_p = 0.8", top_p(probs, 0.8))  # cat 0.63 < 0.8, + mat = 0.86: stop
show("top_p = 0.5", top_p(probs, 0.5))  # cat alone covers 0.5


# ---------- 4. Sampling: a weighted random pick ----------
# rng.choices(words, weights) picks by weight: cat ~63% of the time.
# Java: no built-in; you'd walk the cumulative sums with nextDouble().
def pick(word_to_prob: dict[str, float], rng: random.Random) -> str:
    words = list(word_to_prob)
    weights = list(word_to_prob.values())
    return rng.choices(words, weights=weights)[0]  # choices returns a list of 1


rng = random.Random(42)  # a seed: the same "random" numbers every run
word_to_count = {"cat": 0, "mat": 0, "rat": 0}
for _ in range(1000):
    word_to_count[pick(probs, rng)] += 1
print("\n1000 picks at T = 1.0:", word_to_count)  # close to 630 / 230 / 140

# Same seed -> same picks. That is how Ollama's "seed" option makes answers
# repeatable (part 2). Java: new Random(42) gives the same sequence too.
def eight_picks(seed: int) -> list[str]:
    seeded_rng = random.Random(seed)  # a fresh generator, started from `seed`
    return [pick(probs, seeded_rng) for _ in range(8)]


draws_a = eight_picks(7)
draws_b = eight_picks(7)
print("seed 7, run A:", draws_a)
print("seed 7, run B:", draws_b, "-> same:", draws_a == draws_b)
