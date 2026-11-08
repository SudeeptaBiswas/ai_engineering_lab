"""Part 1 of 2: why word matching fails, and cosine similarity by hand.

No Ollama needed. Vectors here have 2 numbers so you can picture them as
arrows on a map. Real embeddings have 768 (part 2). Same maths.

The whole file in one line:
  question + notes --shared_words()--> fails; vectors --cosine()--> works
"""

import math  # math.sqrt. Java: Math.sqrt

# ---------- 1. Keyword search misses the right note ----------
NOTES = [
    "To reset your password, click 'Forgot password' on the login page.",
    "Invoices are sent by email at the end of each month.",
]
QUERY = "I can't log in to my account"


def shared_words(a: str, b: str) -> set[str]:
    """Words found in both texts.

    Lower-case, split on spaces, then `&` = intersection of two sets.
    Java: Set<String> s = new HashSet<>(a); s.retainAll(b);

    Args:
        a: first text, e.g. "I can't log in to my account".
        b: second text, e.g. "To reset your password, ...".

    Returns:
        The shared words, e.g. {"to"} (a set: no order, no duplicates).
    """
    return set(a.lower().split()) & set(b.lower().split())


for note in NOTES:
    # note[:28] = first 28 chars (a slice). Java: note.substring(0, 28)
    # !r = print with quotes, so you see where the text starts and ends.
    print(f"shared with {note[:28]!r}...: {shared_words(QUERY, note)}")
# Only "to" is shared with the password note: "log in" vs "login",
# "account" vs "password". Same meaning, different words. Embeddings fix this.

# ---------- 2. A vector = an arrow; similar meaning = same direction ----------
# Toy 2-number "embeddings": [how much about animals, how much about money]
ANIMAL = [0.9, 0.1]  # mostly animals -> arrow points east
KITTEN = [0.8, 0.2]  # also animals  -> nearly the same way
INVOICE = [0.1, 0.9]  # mostly money -> arrow points north


def dot(a: list[float], b: list[float]) -> float:
    """Multiply pair by pair, add up.

    zip pairs the items: (a0, b0), (a1, b1), ...
    Java: for (int i = 0; i < a.length; i++) total += a[i] * b[i];

    Args:
        a: first vector, e.g. [0.9, 0.1].
        b: second vector, e.g. [0.8, 0.2].

    Returns:
        The sum, e.g. 0.9*0.8 + 0.1*0.2 = 0.74.
    """
    return sum(x * y for x, y in zip(a, b))


def norm(a: list[float]) -> float:
    """Length of the arrow (Pythagoras).

    Args:
        a: a vector, e.g. [3, 4].

    Returns:
        Its length, e.g. sqrt(3*3 + 4*4) = 5.0.
    """
    return math.sqrt(dot(a, a))  # sqrt(x*x + y*y + ...)


def cosine(a: list[float], b: list[float]) -> float:
    """How alike two directions are, ignoring HOW LONG the arrows are.

    Args:
        a: first vector, e.g. ANIMAL = [0.9, 0.1].
        b: second vector, same length, e.g. KITTEN = [0.8, 0.2].

    Returns:
        1 = same way, 0 = right angle, -1 = opposite.
        ANIMAL vs KITTEN -> 0.99, ANIMAL vs INVOICE -> 0.22.
    """
    return dot(a, b) / (norm(a) * norm(b))


print(f"\nanimal vs kitten : {cosine(ANIMAL, KITTEN):.2f}")  # close to 1
print(f"animal vs invoice: {cosine(ANIMAL, INVOICE):.2f}")  # much lower

# ---------- 3. Length does not matter, direction does ----------
# A long note and a short note on the same topic point the same way.
LONG_KITTEN = [8.0, 2.0]  # 10x longer arrow, same direction as KITTEN
print(f"kitten vs long kitten: {cosine(KITTEN, LONG_KITTEN):.2f}")  # 1.00
print(f"dot instead: {dot(ANIMAL, KITTEN):.2f} vs {dot(ANIMAL, LONG_KITTEN):.2f}")
# dot changes with length; cosine does not. That is why we divide.

# ---------- 4. Search = score every note, sort, keep the top k ----------
# Input: a query arrow + 3 note arrows. Output: note names, best first.
query = [0.6, 0.4]  # "my kitten naps a lot", as a toy arrow
library = {"cat note": ANIMAL, "kitten note": KITTEN, "bill note": INVOICE}
# {key: value for ...} = build a new dict in one line. Java: Map + a for loop
scores = {name: cosine(query, vec) for name, vec in library.items()}
# items() = (name, score) pairs. Sort by item[1] (the score), biggest first.
# Java: list.sort(Comparator.comparing(Entry::getValue).reversed())
ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
print("\nranked:", [(name, round(score, 2)) for name, score in ranked])
# ranked[:2] = first 2. `_` = "a value I don't need" (here: the score).
print("top 2 :", [name for name, _ in ranked[:2]])  # same idea as top_k in 2.4
