"""Replace each `...` with code. Run until every line says PASS."""


def squares_of_evens(nums: list[int]) -> list[int]:
    """Squares of the even numbers, in order. Use a comprehension."""
    ...


def word_freq(text: str) -> dict[str, int]:
    """Count each word, lowercased. Split on whitespace with text.split()."""
    ...


def top_k(scores: dict[str, float], k: int) -> list[str]:
    """Keys of the k highest scores, highest first."""
    ...


def unique_sorted(tags: list[str]) -> list[str]:
    """Drop duplicates (case-insensitive), return lowercased and sorted."""
    ...


def chunk(items: list, size: int) -> list[list]:
    """Split into pieces of `size`; last piece may be shorter. (RAG chunking!)"""
    ...


def invert(d: dict[str, str]) -> dict[str, str]:
    """Swap keys and values. Use a dict comprehension."""
    ...


def merge_counts(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    """Add counts from both dicts. Missing keys count as 0."""
    ...


# ---------- Test helper — no need to change anything below ----------
def check(label: str, got, expected) -> None:
    # {got!r} prints the value in code form, e.g. 'abc' with quotes
    status = "PASS" if got == expected else f"FAIL (got {got!r}, expected {expected!r})"
    print(f"{label:<16} {status}")  # :<16 = pad label to 16 chars, left-aligned


# Runs only when you run this file directly (like public static void main)
if __name__ == "__main__":
    check("squares_evens", squares_of_evens([1, 2, 3, 4, 5, 6]), [4, 16, 36])
    check("word_freq", word_freq("RAG and rag and MCP"), {"rag": 2, "and": 2, "mcp": 1})
    check("top_k", top_k({"a": 0.2, "b": 0.9, "c": 0.5}, 2), ["b", "c"])
    check("unique_sorted", unique_sorted(["MCP", "rag", "RAG", "agent"]), ["agent", "mcp", "rag"])
    check("chunk", chunk([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]])
    check("chunk empty", chunk([], 3), [])
    check("invert", invert({"py": "python", "js": "javascript"}), {"python": "py", "javascript": "js"})
    check("merge_counts", merge_counts({"a": 1, "b": 2}, {"b": 3, "c": 4}), {"a": 1, "b": 5, "c": 4})
