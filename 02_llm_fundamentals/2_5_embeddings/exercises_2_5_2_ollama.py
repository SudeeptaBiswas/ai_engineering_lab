"""Part 2 of 2: real embeddings + search. Needs Ollama with nomic-embed-text.
Replace each `...` with code. Run until every line says PASS.
Uses cosine + top_matches from part 1 (import a sibling file: lesson 1.5)."""

import httpx  # pyright: ignore[reportUnusedImport] — until you use it

from exercises_2_5_1_cosine import Vector, cosine, error_of  # part 1 file (1.5)
from exercises_2_5_1_cosine import top_matches  # pyright: ignore[reportUnusedImport]
from lab_tools.check import check  # numbered PASS/FAIL + path:line links
from lab_tools.log import debug, log  # pyright: ignore[reportUnusedImport]

OLLAMA_URL = "http://127.0.0.1:11434"  # not "localhost": 2 s slower on Windows
EMBED_MODEL = "nomic-embed-text"  # text in, 768 numbers out
CHAT_MODEL = "qwen3:1.7b"  # can NOT embed (measured: HTTP 501)


def embed(texts: list[str], model: str = EMBED_MODEL) -> list[Vector]:
    """Turn each text into a vector, with ONE HTTP call for all texts.

    POST {OLLAMA_URL}/api/embed, JSON {"model": model, "input": texts},
    timeout 120. Return reply["embeddings"].
    Args:
        texts: e.g. ["cat", "kitten"]. Empty list -> [].
        model: an embedding model. A chat model fails (HTTP 501).
    Returns:
        One vector (768 numbers) per text, same order:
        [[0.05, 0.06, ...], [0.04, 0.07, ...]].
    Raises:
        httpx.HTTPStatusError on a bad status (404 no model, 501 chat
        model): call response.raise_for_status().
    """
    body = {"model": model, "input": texts}  # request JSON. "input", not "messages"
    response = httpx.post(f"{OLLAMA_URL}/api/embed", json=body, timeout=120.0)  # send, wait max 120 s
    response.raise_for_status()
    reply = response.json()  # JSON -> dict: {"model": ..., "embeddings": [[...], [...]]}
    return reply["embeddings"]  # the list of vectors. Java: List<double[]>
    ...


def search(query: str, notes: list[str], k: int) -> list[str]:
    """Find the k notes closest in meaning to the query, best first.

    ONE embed call: vecs = embed([query] + notes). vecs[0] is the query,
    vecs[1:] are the notes (same order). Then top_matches.
    Args:
        query: e.g. "I can't log in to my account".
        notes: the texts to search, e.g. NOTES below.
        k: how many notes to return.
    Returns:
        Note texts only, no scores, e.g. ["To reset your password, ..."].
    """
    query_embed_vec:list[Vector] = embed([query], EMBED_MODEL)
    notes_embed_vec: list[Vector] = embed(notes, EMBED_MODEL)

    score = [cosine(query_embed_vec[0], v) for v in notes_embed_vec]
    pairs = list(zip(notes, score))
    top_matches_list =  sorted(pairs, key=lambda p: p[1], reverse=True)[:k]
    return [i[0] for i in top_matches_list]
    
    ...


# ---------- Test helper (done for you) ----------
def cat_closer_to_kitten() -> bool:
    """One embed call for 3 words. Returns True if cat is nearer kitten than invoice."""
    cat, kitten, invoice = embed(["cat", "kitten", "invoice"])  # unpack 3
    return cosine(cat, kitten) > cosine(cat, invoice)


NOTES = [
    "To reset your password, click 'Forgot password' on the login page.",
    "Ollama runs language models on your own computer.",
    "The office is closed on public holidays.",
    "Our cat sleeps on the sofa all afternoon.",
    "Invoices are sent by email at the end of each month.",
]

if __name__ == "__main__":
    check("embed size", lambda: len(embed(["cat"])[0]), 768)
    check("embed batch", lambda: len(embed(["a", "b", "c"])), 3)
    check("embed none", lambda: embed([]), [])
    # .split(":")[0] keeps the error type: "HTTPStatusError: ..." -> "HTTPStatusError"
    check("chat model", lambda: error_of(
        lambda: embed(["cat"], model=CHAT_MODEL)).split(":")[0], "HTTPStatusError")
    check("kitten > invoice", cat_closer_to_kitten, True)
    check("search login", lambda: search("I can't log in to my account", NOTES, 1),
          [NOTES[0]])
    check("search kitten", lambda: search("my kitten naps a lot", NOTES, 2)[0], NOTES[3])
