"""How an LLM sees text: tokens, next-token guessing, context window.

Pure Python, no model yet (Ollama comes in 2.2). Run it, then read each block.
"""

import math  # math.exp for softmax. Java: Math.exp
from collections import Counter  # a dict that counts. Java: Map<K,Integer> + merge()

TEXT = "the cat sat on the mat . the cat ate the rat ."


# ---------- 1. Tokens: text -> pieces -> ids ----------
# A model never sees letters. It sees integer ids, one per token.
chars = list("cat sat")  # character tokens: tiny vocab, very long sequences
words = TEXT.split()  # word tokens: short sequences, but huge vocab + unknown words
print("chars:", chars)
print("words:", words[:6], "...")

# Vocabulary = token -> id. sorted(set(...)) = unique tokens in a stable order.
# enumerate gives (index, item) pairs. Java: for (int i = 0; ...) + list.get(i)
vocab = {tok: i for i, tok in enumerate(sorted(set(words)))}
ids = [vocab[w] for w in words]  # encode = look each token up
print("vocab:", vocab)
print("ids:  ", ids)


# ---------- 2. BPE: how real tokenizers pick sub-word pieces ----------
# Start from characters, merge the most frequent neighbour pair, repeat.
# Real tokenizers do tens of thousands of merges on huge text; we do 4.
def pair_counts(tokens: list[str]) -> Counter:
    # zip(a, a[1:]) walks neighbours: (t0,t1), (t1,t2), ...
    return Counter(zip(tokens, tokens[1:]))


def merge(tokens: list[str], pair: tuple[str, str]) -> list[str]:
    out, i = [], 0  # two assignments in one line (tuple unpacking)
    while i < len(tokens):
        if i + 1 < len(tokens) and (tokens[i], tokens[i + 1]) == pair:
            out.append(tokens[i] + tokens[i + 1])  # glue the pair into one token
            i += 2  # skip both halves
        else:
            out.append(tokens[i])
            i += 1
    return out


tokens = list("the cat sat on the mat")  # spaces are tokens too
for step in range(4):
    # most_common(1) -> [(pair, count)]; [0][0] takes the pair
    best = pair_counts(tokens).most_common(1)[0][0]
    tokens = merge(tokens, best)
    print(f"merge {step + 1}: {best!r:12} -> {len(tokens)} tokens")
print("after BPE:", tokens)


# ---------- 3. Next-token prediction ----------
# An LLM: tokens so far -> a score for every token in the vocab.
# Toy version: count which word follows which (a "bigram" model).
follows: dict[str, Counter] = {}
for a, b in zip(words, words[1:]):
    follows.setdefault(a, Counter())[b] += 1  # setdefault = computeIfAbsent
print("after 'the':", dict(follows["the"]))

# Generate: take the most likely next word, append, repeat = "autoregressive".
out = ["the"]
for _ in range(5):  # _ = loop variable we don't use
    out.append(follows[out[-1]].most_common(1)[0][0])  # out[-1] = last item
print("generated:", " ".join(out))  # greedy -> boring, repeats. Fix: sampling (2.4)


# ---------- 4. Scores -> probabilities (softmax) ----------
# Real models output raw scores ("logits"). Softmax makes them
# probabilities that add up to 1.
def softmax(scores: list[float]) -> list[float]:
    exps = [math.exp(s) for s in scores]  # exp makes every score positive
    total = sum(exps)
    return [e / total for e in exps]


logits = {"cat": 2.0, "mat": 1.0, "rat": 0.5}
for word, p in zip(logits, softmax(list(logits.values()))):
    print(f"  P({word}) = {p:.2f}")  # :.2f = 2 decimals. Java: "%.2f"


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
    return sum(len(m["content"]) // 4 for m in msgs)  # ~4 chars per token


print("tokens used:", size(chat), "of", WINDOW)
while size(chat) > WINDOW:
    dropped = chat.pop(1)  # drop the oldest turn; keep the system message at [0]
    print("  dropped:", dropped["content"])
print("left:", [m["role"] for m in chat])
