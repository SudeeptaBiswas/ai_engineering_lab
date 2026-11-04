"""Replace each `...` with code. Run until every line says PASS."""

import math  # math.ceil, math.exp
from collections import Counter  # Counter(...).most_common(1) -> [(item, count)]

UNK = "<unk>"  # token for any word the vocab doesn't know


def build_vocab(words: list[str]) -> dict[str, int]:
    """UNK gets id 0. Other unique words get 1, 2, 3... in sorted order.
    Hint: enumerate(..., start=1)."""
    ...


def encode(words: list[str], vocab: dict[str, int]) -> list[int]:
    """Words -> ids. A word not in vocab gets the UNK id. Hint: dict.get."""
    ...


def decode(ids: list[int], vocab: dict[str, int]) -> str:
    """Ids -> words joined by single spaces. Hint: invert the vocab (1.3)."""
    ...


def most_common_pair(tokens: list[str]) -> tuple[str, str]:
    """The neighbour pair seen most often; first-seen wins a tie (BPE step)."""
    ...


def estimate_tokens(text: str) -> int:
    """Rule of thumb: 1 token per 4 characters, rounded UP. "" -> 0."""
    ...


def next_word(text: str, word: str) -> str | None:
    """Word that most often follows `word` in text (first-seen wins a tie).
    None if `word` is never followed by anything. `str | None` = may be None."""
    ...


def most_likely(logits: dict[str, float]) -> tuple[str, float]:
    """Softmax the scores. Return (best token, its probability rounded to 2)."""
    ...


def fit_context(messages: list[dict], budget: int) -> list[dict]:
    """Always keep messages[0] (system). Then, going from NEWEST to oldest,
    keep messages while the estimate_tokens(content) total stays <= budget
    (the system message counts too). Stop at the first one that doesn't fit.
    Return the kept messages oldest first."""
    ...


# ---------- Test helper — no need to change anything below ----------
# fn is a lambda (Java: () -> ...). It runs inside try, so an error in
# unfinished code prints FAIL instead of stopping the whole file.
def check(label: str, fn, expected) -> None:
    try:
        got = fn()  # call the lambda now
        # {got!r} prints the value in code form, e.g. 'abc' with quotes
        # --- explicit start ---
        if got == expected:
            status = "PASS"
        else:
            status = f"FAIL (got {got!r}, expected {expected!r})"
        # --- explicit end ---
        # concise: status = "PASS" if got == expected else f"FAIL ..."
        #          Java: cond ? a : b
    except Exception as e:  # Java: catch (Exception e)
        status = f"FAIL ({type(e).__name__}: {e})"
    print(f"{label:<16} {status}")  # :<16 = pad label to 16 chars, left-aligned


V = {"<unk>": 0, "a": 1, "b": 2}  # small vocab for the tests
STORY = "the cat sat on the mat the cat ran"
CHAT = [  # token estimates: 2, 2, 3, 1
    {"role": "system", "content": "be brief"},
    {"role": "user", "content": "aaaaaaaa"},
    {"role": "assistant", "content": "bbbbbbbbbbbb"},
    {"role": "user", "content": "cccc"},
]


def _roles(msgs: list[dict]) -> list[str]:  # just the roles, for short checks
    # --- explicit start ---
    roles = []
    for m in msgs:
        roles.append(m["role"])
    # --- explicit end ---
    # concise: return [m["role"] for m in msgs]
    return roles


# Runs only when you run this file directly (like public static void main)
if __name__ == "__main__":
    check("build_vocab", lambda: build_vocab("b a b".split()), V)
    check("encode", lambda: encode(["a", "z", "b"], V), [1, 0, 2])
    check("decode", lambda: decode([2, 1, 0], V), "b a <unk>")
    check("common pair", lambda: most_common_pair(list("banana")), ("a", "n"))
    check("estimate", lambda: estimate_tokens("hello world"), 3)
    check("estimate empty", lambda: estimate_tokens(""), 0)
    check("next_word", lambda: next_word(STORY, "the"), "cat")
    check("next_word none", lambda: next_word(STORY, "ran"), None)
    check("most_likely", lambda: most_likely({"cat": 2.0, "mat": 1.0, "rat": 0.5}), ("cat", 0.63))
    check("fit_context", lambda: _roles(fit_context(CHAT, 6)), ["system", "assistant", "user"])
    check("fit tiny", lambda: _roles(fit_context(CHAT, 2)), ["system"])
