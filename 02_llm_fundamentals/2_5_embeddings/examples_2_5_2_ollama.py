"""Part 2 of 2: real embeddings from Ollama, then a tiny search engine.

Needs Ollama with nomic-embed-text (`ollama pull nomic-embed-text`).
Takes ~5 s (first call loads the model, ~1 s).

The whole file in one line (like a search engine, but by meaning):
  texts --embed()--> vectors --cosine()--> scores --max()--> best text
"""

import math  # math.sqrt. Java: Math.sqrt
import time  # time.perf_counter() = a stopwatch. Java: System.nanoTime()

import httpx  # HTTP client (lesson 1.7). Java: java.net.http.HttpClient

EMBED_URL = "http://127.0.0.1:11434/api/embed"  # not /api/chat
MODEL = "nomic-embed-text"  # an embedding model: text in, numbers out


def embed(texts: list[str]) -> list[list[float]]:
    """Turn each text into a vector (a list of 768 numbers).

    Sends ONE HTTP POST to Ollama with all texts (faster than 1 by 1).
    Java: List<double[]> embed(List<String> texts)

    Args:
        texts: the texts to embed, e.g. ["cat", "kitten"].

    Returns:
        One vector per text, in the same order:
        [[0.05, 0.06, ...],    <- vector of "cat",    768 numbers
         [0.04, 0.07, ...]]    <- vector of "kitten", 768 numbers
    """
    body = {"model": MODEL, "input": texts}  # request JSON. "input", not "messages"
    response = httpx.post(EMBED_URL, json=body, timeout=120.0)  # send, wait max 120 s
    reply = response.json()  # JSON -> dict: {"model": ..., "embeddings": [[...], [...]]}
    return reply["embeddings"]  # the list of vectors. Java: List<double[]>


def cosine(a: list[float], b: list[float]) -> float:
    """How alike two vectors are in direction (part 1, section 2).

    Args:
        a: first vector, e.g. embed(["cat"])[0] (768 numbers).
        b: second vector, same length as a.

    Returns:
        One number, -1 to 1. Higher = closer in meaning.
        Measured: cat vs kitten 0.84, cat vs invoice 0.40.
    """
    dot = sum(x * y for x, y in zip(a, b))  # a0*b0 + a1*b1 + ...
    length_a = math.sqrt(sum(x * x for x in a))  # arrow length of a (1.0 for nomic)
    length_b = math.sqrt(sum(y * y for y in b))  # arrow length of b
    return dot / (length_a * length_b)


# ---------- 1. What an embedding looks like ----------
# Input: 1 text. Output: a list with 1 vector. [0] takes that vector out.
vector = embed(["The cat sat on the mat."])[0]
print("numbers:", len(vector))  # 768 for this model, for ANY text length
# vector[:5] = first 5 items (a slice). Java: Arrays.copyOfRange(vector, 0, 5)
# [round(v, 3) for v in ...] = a new list, each rounded. Java: stream().map(...).toList()
print("first 5:", [round(v, 3) for v in vector[:5]])
print("length :", round(math.sqrt(sum(v * v for v in vector)), 3))  # 1.0 (nomic does this)

# ---------- 2. Scores between pairs ----------
# For each pair: 2 texts in -> 2 vectors out -> 1 cosine score.
PAIRS = [("cat", "kitten"), ("cat", "dog"), ("cat", "invoice"),
         ("I love this movie", "I hate this movie")]
for left, right in PAIRS:  # each item is a pair (tuple) -> unpacked into 2 names
    left_vec, right_vec = embed([left, right])  # list of 2 vectors, unpacked
    # !r = print with quotes. :<20 = pad to 20 chars, left-aligned. :.2f = 2 decimals.
    # Java: String.format("%-20s vs %-20s %.2f", ...)
    print(f"{left!r:<20} vs {right!r:<20} {cosine(left_vec, right_vec):.2f}")
# love vs hate scores HIGH: same topic (a movie review). Embeddings
# measure "what is it about", not "is it true" or "is it positive".

# ---------- 3. A tiny search engine ----------
# Input: a question + 5 notes. Output: the note closest in meaning.
NOTES = [
    "To reset your password, click 'Forgot password' on the login page.",
    "Ollama runs language models on your own computer.",
    "The office is closed on public holidays.",
    "Our cat sleeps on the sofa all afternoon.",
    "Invoices are sent by email at the end of each month.",
]
note_vecs = embed(NOTES)  # 5 notes in -> 5 vectors out. Done ONCE, reused below
for query in ["I can't log in to my account", "When do I get my bill?"]:
    query_vec = embed([query])[0]  # 1 question -> 1 vector
    # Score the question against every note: 5 numbers, same order as NOTES.
    scores = [cosine(query_vec, note_vec) for note_vec in note_vecs]
    # Index of the top score: try i = 0..4, compare them by scores[i].
    # Java: IntStream.range(0, n).boxed().max(Comparator.comparing(i -> scores[i])).get()
    best = max(range(len(NOTES)), key=lambda i: scores[i])
    print(f"\n{query!r}\n  scores {[round(s, 2) for s in scores]}\n  best   {NOTES[best]!r}")

# ---------- 4. One call for many texts is faster ----------
# Same 5 notes, embedded two ways. Output: seconds for each way.
start = time.perf_counter()
for note in NOTES:
    embed([note])  # 5 HTTP calls, 1 text each
one_by_one = time.perf_counter() - start
start = time.perf_counter()
embed(NOTES)  # 1 HTTP call, 5 texts
print(f"\n5 calls {one_by_one:.2f} s, 1 batch call {time.perf_counter() - start:.2f} s")
