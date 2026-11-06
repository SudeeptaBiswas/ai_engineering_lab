"""Replace each `...` with code. Run until every line says PASS."""

def squares_of_evens(nums: list[int]) -> list[int]:
    """Squares of the even numbers, in order. Use a comprehension."""
    return [num * num for num in nums if num % 2 == 0]


def word_freq(text: str) -> dict[str, int]:
    """Count each word, lowercased. Split on whitespace with text.split()."""
    word_counts: dict[str, int] = {}
    for word in text.split():
        word = word.lower()
        word_counts[word] = word_counts.get(word, 0) + 1
    return word_counts
    


def top_k(scores: dict[str, float], k: int) -> list[str]:
    """Keys of the k highest scores, highest first."""
    return sorted(
        scores,
        key=lambda key: scores[key],
        reverse=True
    )[:k]


def unique_sorted(tags: list[str]) -> list[str]:
    """Drop duplicates (case-insensitive), return lowercased and sorted."""
    return sorted(set(i.lower() for i in tags))


# [T] = any item type, like Java <T>. Same T in, same T out.
def chunk[T](items: list[T], size: int) -> list[list[T]]:
    """Split into pieces of `size`; last piece may be shorter. (RAG chunking!)"""
    return [
        items[i:i + size]
        for i in range(0, len(items), size)
    ]



def invert(d: dict[str, str]) -> dict[str, str]:
    """Swap keys and values. Use a dict comprehension."""
    return {value: key for key, value in d.items()}


def merge_counts(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    """Add counts from both dicts. Missing keys count as 0."""
    """keys = a.keys() | b.keys()
    return {
        key: a.get(key, 0) + b.get(key, 0)
        for key in keys
    }"""
    result: dict[str, int] = {}
    for key in a.keys() | b.keys():
        result[key] = a.get(key, 0) + b.get(key, 0)
    return result


# ---------- Test helper — no need to change anything below ----------
def check(label: str, got: object, expected: object) -> None:
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
    check("chunk empty", chunk(list[int](), 3), [])  # list[int]() = typed []
    check("invert", invert({"py": "python", "js": "javascript"}), {"python": "py", "javascript": "js"})
    check("merge_counts", merge_counts({"a": 1, "b": 2}, {"b": 3, "c": 4}), {"a": 1, "b": 5, "c": 4})
