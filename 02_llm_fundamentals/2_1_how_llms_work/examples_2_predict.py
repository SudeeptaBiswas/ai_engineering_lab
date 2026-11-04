"""Part 2 of 2: next-token guessing, softmax, context window.

Same reading rule as part 1: code between "explicit start/end" is the long
way; the "# concise:" line right after it is the short Python way.
"""

import math  # math.exp for softmax. Java: Math.exp

TEXT = "the cat sat on the mat . the cat ate the rat ."
words = TEXT.split()


# ---------- 3. Next-token prediction ----------
# An LLM: tokens so far -> a score for every token in the vocab.
# Toy version: count which word follows which (a "bigram" model).
# --- explicit start ---
follows: dict[str, dict[str, int]] = {}
for i in range(len(words) - 1):
    a = words[i]
    b = words[i + 1]
    if a not in follows:
        follows[a] = {}
    if b not in follows[a]:
        follows[a][b] = 0
    follows[a][b] += 1
# --- explicit end ---
# concise: follows: dict[str, Counter] = {}
#          for a, b in zip(words, words[1:]):
#              follows.setdefault(a, Counter())[b] += 1
#          setdefault = Java computeIfAbsent
print("after 'the':", follows["the"])


def top(counts: dict[str, int]) -> str:
    """The key with the biggest count. A tie keeps the first one seen."""
    # --- explicit start ---
    best = None
    best_count = 0
    for key in counts:
        if counts[key] > best_count:
            best = key
            best_count = counts[key]
    # --- explicit end ---
    # concise: return Counter(counts).most_common(1)[0][0]
    return best


# Generate: take the most likely next word, append, repeat = "autoregressive".
out = ["the"]
for _ in range(5):  # _ = loop variable we don't use
    # --- explicit start ---
    last = out[len(out) - 1]
    # --- explicit end ---
    # concise: last = out[-1]   (a negative index counts from the end)
    out.append(top(follows[last]))
# join = Java String.join(" ", out). Greedy -> boring, repeats. Fix: sampling (2.4)
print("generated:", " ".join(out))


# ---------- 4. Scores -> probabilities (softmax) ----------
# Real models output raw scores ("logits"). Softmax makes them
# probabilities that add up to 1.
def softmax(scores: list[float]) -> list[float]:
    # --- explicit start ---
    exps = []
    for s in scores:
        exps.append(math.exp(s))  # exp makes every score positive
    total = sum(exps)
    probs = []
    for e in exps:
        probs.append(e / total)
    # --- explicit end ---
    # concise: exps = [math.exp(s) for s in scores]
    #          return [e / sum(exps) for e in exps]
    return probs


logits = {"cat": 2.0, "mat": 1.0, "rat": 0.5}
# --- explicit start ---
names = list(logits.keys())
probs = softmax(list(logits.values()))
for i in range(len(names)):
    print(f"  P({names[i]}) = {probs[i]:.2f}")  # :.2f = 2 decimals. Java: "%.2f"
# --- explicit end ---
# concise: for word, p in zip(logits, softmax(list(logits.values()))):
#              print(f"  P({word}) = {p:.2f}")
#          zip pairs up two lists: ("cat", 0.63), ("mat", 0.23), ...


# ---------- 5. Context window ----------
# The model sees at most WINDOW tokens per call: system + history + question
# + its own answer. It keeps NO memory between calls -- your code resends the
# history every time, and must drop old turns once it is too long.
WINDOW = 20  # pretend size. Real models: thousands to over a million.
chat = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is a token?"},
    {"role": "assistant", "content": "A small piece of text, often part of a word."},
    {"role": "user", "content": "And a context window?"},
]


def size(msgs: list[dict]) -> int:
    # --- explicit start ---
    total = 0
    for m in msgs:
        total += len(m["content"]) // 4  # ~4 chars per token; // = int division
    # --- explicit end ---
    # concise: return sum(len(m["content"]) // 4 for m in msgs)
    return total


print("tokens used:", size(chat), "of", WINDOW)
while size(chat) > WINDOW:
    dropped = chat.pop(1)  # drop the oldest turn; keep the system message at [0]
    print("  dropped:", dropped["content"])
# --- explicit start ---
roles = []
for m in chat:
    roles.append(m["role"])
# --- explicit end ---
# concise: roles = [m["role"] for m in chat]
print("left:", roles)
