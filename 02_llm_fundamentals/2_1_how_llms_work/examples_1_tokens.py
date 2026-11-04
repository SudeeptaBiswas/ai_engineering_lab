"""Part 1 of 2: how an LLM sees text — tokens and BPE.

Pure Python, no model yet (Ollama comes in 2.2). Run it, then read each block.
How to read: code between "explicit start/end" is the long, step-by-step way.
The "# concise:" line right after it does the same in short Python style.
"""

TEXT = "the cat sat on the mat . the cat ate the rat ."


# ---------- 1. Tokens: text -> pieces -> ids ----------
# A model never sees letters. It sees integer ids, one per token.
chars = list("cat sat")  # character tokens: tiny vocab, very long sequences
words = TEXT.split()  # word tokens: short sequences, but huge vocab + unknown words
print("chars:", chars)
print("words:", words[:6], "...")  # [:6] = first 6 items. Java: subList(0, 6)

# Vocabulary = token -> id. Unique tokens, sorted, numbered 0, 1, 2...
# --- explicit start ---
unique = sorted(set(words))  # set() drops duplicates, sorted() fixes the order
vocab = {}
for i in range(len(unique)):
    vocab[unique[i]] = i
# --- explicit end ---
# concise: vocab = {tok: i for i, tok in enumerate(sorted(set(words)))}
#          enumerate gives (index, item) pairs; {k: v for ...} builds a dict

# Encode = look each token up.
# --- explicit start ---
ids = []
for w in words:
    ids.append(vocab[w])
# --- explicit end ---
# concise: ids = [vocab[w] for w in words]
print("vocab:", vocab)
print("ids:  ", ids)


# ---------- 2. BPE: how real tokenizers pick sub-word pieces ----------
# Start from characters, merge the most frequent neighbour pair, repeat.
# Real tokenizers do tens of thousands of merges on huge text; we do 4.
def pair_counts(tokens: list[str]) -> dict[tuple[str, str], int]:
    """How often each neighbour pair appears: (t0,t1), (t1,t2), ..."""
    # --- explicit start ---
    counts = {}
    for i in range(len(tokens) - 1):
        pair = (tokens[i], tokens[i + 1])
        if pair not in counts:
            counts[pair] = 0
        counts[pair] += 1
    # --- explicit end ---
    # concise: return Counter(zip(tokens, tokens[1:]))
    #          zip(a, a[1:]) walks neighbours; Counter (collections) counts them
    return counts


def merge(tokens: list[str], pair: tuple[str, str]) -> list[str]:
    """Glue every place where `pair` appears into one token."""
    # --- explicit start ---
    out = []
    i = 0
    # --- explicit end ---
    # concise: out, i = [], 0   (two assignments in one line)
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
    counts = pair_counts(tokens)
    # Find the pair with the biggest count. A tie keeps the first one seen.
    # --- explicit start ---
    best = None
    best_count = 0
    for pair in counts:  # a dict keeps insertion order
        if counts[pair] > best_count:
            best = pair
            best_count = counts[pair]
    # --- explicit end ---
    # concise: best = Counter(...).most_common(1)[0][0]
    #          most_common(1) -> [(pair, count)]; [0][0] takes the pair
    tokens = merge(tokens, best)
    # !r = show in code form (with quotes); :12 = pad to 12 chars
    print(f"merge {step + 1}: {best!r:12} -> {len(tokens)} tokens")
print("after BPE:", tokens)
