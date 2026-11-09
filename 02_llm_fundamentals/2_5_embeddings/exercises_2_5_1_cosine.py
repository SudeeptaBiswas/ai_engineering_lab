"""Part 1 of 2: similarity by hand. No Ollama needed.
Replace each `...` with code. Run until every line says PASS.
Docstrings: Args = Java @param, Returns = @return, Raises = @throws."""

import math  # pyright: ignore[reportUnusedImport] — math.sqrt
from collections.abc import Callable  # type of a function (lab_tools/check.py)

from lab_tools.check import check  # numbered PASS/FAIL + path:line links
from lab_tools.log import debug, log  # pyright: ignore[reportUnusedImport]

Vector = list[float]  # one embedding. Java: double[]


def dot(a: Vector, b: Vector) -> float:
    """Multiply pair by pair, add up.

    Args:
        a: e.g. [1, 2, 3].
        b: e.g. [4, 5, 6]. Must be the same length as a.
    Returns:
        e.g. 1*4 + 2*5 + 3*6 = 32.
    Raises:
        ValueError(f"lengths differ: {len(a)} vs {len(b)}") if lengths differ.
        Why: zip() silently stops at the shorter list -> a wrong score.
    """
    if len(a) != len(b):
        raise ValueError(f"lengths differ: {len(a)} vs {len(b)}")
    return sum(x * y for x, y in zip(a, b))
    ...


def norm(a: Vector) -> float:
    """Length of the arrow: sqrt of (a dot a).

    Args:
        a: e.g. [3, 4].
    Returns:
        e.g. sqrt(3*3 + 4*4) = 5.0.
    """
    return math.sqrt(dot(a, a))  # sqrt(x*x + y*y + ...)
    ...


def cosine(a: Vector, b: Vector) -> float:
    """How alike two directions are: dot / (norm(a) * norm(b)).

    Args:
        a: e.g. [1, 0].
        b: e.g. [0, 1].
    Returns:
        1.0 same way ([1, 2] vs [2, 4]), 0.0 right angle, -1.0 opposite.
    Raises:
        ValueError("zero vector") if a or b is all zeros (no direction,
        would divide by 0).
    """
    if all(x == 0 for x in a) or all(x == 0 for x in b):
        raise ValueError("zero vector")
    return dot(a, b) / (norm(a) * norm(b))
    ...


def top_matches(query: Vector, doc_vecs: list[Vector], docs: list[str],
                k: int) -> list[tuple[str, float]]:
    """Rank docs by how close their vector is to the query vector.

    Args:
        query: the question's vector, e.g. [1, 0] (points east).
        doc_vecs: one vector per doc. doc_vecs[i] belongs to docs[i].
        docs: the doc texts, e.g. ["east", "north", "west", "north-east"].
        k: how many to keep. Bigger than len(docs) -> all. 0 or less -> [].
    Returns:
        (doc, cosine score) pairs, best first, e.g.
        [("east", 0.995), ("north-east", 0.707)] for k = 2.
    Hint: list(zip(docs, scores)), then sorted(..., key=..., reverse=True).
    """
    # Handle invalid k
    if k <= 0:
        return []

    score = [cosine(query, v) for v in doc_vecs]
    pairs = list(zip(docs, score))
    return sorted(pairs, key=lambda p: p[1], reverse=True)[:k]
    ...


# ---------- Test helpers (done for you) ----------
def error_of(run: Callable[[], object]) -> str:
    """Run it. Returns "ErrorType: message", or "no error" (lesson 1.5).
    e.g. error_of(lambda: 1 / 0) -> "ZeroDivisionError: division by zero"."""
    try:
        run()
    except Exception as error:
        return f"{type(error).__name__}: {error}"
    return "no error"


def rounded(pairs: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """Round each score to 2 decimals, so checks can use ==.
    e.g. [("east", 0.995)] -> [("east", 1.0)]."""
    return [(doc, round(score, 2)) for doc, score in pairs]


# Toy 2-number vectors: [east, north]. Same maths as 768 numbers.
# east is [1.0, 0.1], not [1, 0], on purpose: like real search, no doc is
# an exact copy of the query. Its score vs [1, 0] is 0.995 -> rounds to 1.0.
COMPASS = ["east", "north", "west", "north-east"]
COMPASS_VECS = [[1.0, 0.1], [0.0, 1.0], [-1.0, 0.0], [1.0, 1.0]]

if __name__ == "__main__":
    check("dot", lambda: dot([1, 2, 3], [4, 5, 6]), 32)
    check("dot lengths", lambda: error_of(lambda: dot([1, 2, 3], [4, 5])),
          "ValueError: lengths differ: 3 vs 2")
    check("norm", lambda: norm([3, 4]), 5.0)
    check("cos same way", lambda: round(cosine([1, 2], [2, 4]), 2), 1.0)
    check("cos opposite", lambda: round(cosine([1, 0], [-1, 0]), 2), -1.0)
    check("cos right angle", lambda: round(cosine([1, 0], [0, 1]), 2), 0.0)
    check("cos zero", lambda: error_of(lambda: cosine([0, 0], [1, 2])),
          "ValueError: zero vector")
    check("top 2", lambda: rounded(top_matches([1, 0], COMPASS_VECS, COMPASS, 2)),
          [("east", 1.0), ("north-east", 0.71)])
    check("top too many", lambda: [d for d, _ in top_matches([1, 0], COMPASS_VECS, COMPASS, 9)],
          ["east", "north-east", "north", "west"])
    check("top 0", lambda: top_matches([1, 0], COMPASS_VECS, COMPASS, 0), [])
