"""Replace each `...` with code. Run until every line says PASS."""

import math  # math.ceil, math.exp
from collections import Counter  # Counter(...).most_common(1) -> [(item, count)]
from collections.abc import Callable  # type of a function, for check() below

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


def fit_context(
    messages: list[dict[str, str]], budget: int
) -> list[dict[str, str]]:
    """Always keep messages[0] (system). Then, going from NEWEST to oldest,
    keep messages while the estimate_tokens(content) total stays <= budget
    (the system message counts too). Stop at the first one that doesn't fit.
    Return the kept messages oldest first."""
    ...


# ---------- Test helper — no need to change anything below ----------
# run_test is a lambda (Java: () -> ...): a tiny function that calls YOUR
# function. check() calls it inside try, so an error in unfinished code
# prints FAIL instead of stopping the whole file.
# Callable[[], object] = takes nothing, returns anything. Java: Supplier<Object>
def check(label: str, run_test: Callable[[], object], expected: object) -> None:
    try:
        actual = run_test()  # call the lambda now -> what your code returned
        # {actual!r} prints the value in code form, e.g. 'abc' with quotes
        # --- explicit start ---
        if actual == expected:
            result = "PASS"
        else:
            result = f"FAIL (got {actual!r}, expected {expected!r})"
        # --- explicit end ---
        # concise: result = "PASS" if actual == expected else f"FAIL ..."
        #          Java: condition ? a : b
    except Exception as error:  # Java: catch (Exception error)
        # type(error).__name__ = the error class name, e.g. "KeyError"
        result = f"FAIL ({type(error).__name__}: {error})"
    print(f"{label:<16} {result}")  # :<16 = pad label to 16 chars, left-aligned


TEST_VOCAB = {"<unk>": 0, "a": 1, "b": 2}  # small vocabulary: token -> id
TEST_STORY = "the cat sat on the mat the cat ran"  # text for next_word
TEST_CHAT = [  # estimate_tokens of each content: 2, 2, 3, 1
    {"role": "system", "content": "be brief"},
    {"role": "user", "content": "aaaaaaaa"},
    {"role": "assistant", "content": "bbbbbbbbbbbb"},
    {"role": "user", "content": "cccc"},
]


def _roles(messages: list[dict[str, str]]) -> list[str]:
    """Just the roles, so a test can compare short lists: ['system', 'user']."""
    # --- explicit start ---
    roles: list[str] = []
    for message in messages:
        roles.append(message["role"])
    # --- explicit end ---
    # concise: return [message["role"] for message in messages]
    return roles


# Runs only when you run this file directly (like public static void main)
if __name__ == "__main__":
    check("build_vocab", lambda: build_vocab(["b", "a", "b"]), TEST_VOCAB)
    check("encode", lambda: encode(["a", "z", "b"], TEST_VOCAB), [1, 0, 2])
    check("decode", lambda: decode([2, 1, 0], TEST_VOCAB), "b a <unk>")
    check("common pair", lambda: most_common_pair(list("banana")), ("a", "n"))
    check("estimate", lambda: estimate_tokens("hello world"), 3)
    check("estimate empty", lambda: estimate_tokens(""), 0)
    check("next_word", lambda: next_word(TEST_STORY, "the"), "cat")
    check("next_word none", lambda: next_word(TEST_STORY, "ran"), None)
    check(
        "most_likely",
        lambda: most_likely({"cat": 2.0, "mat": 1.0, "rat": 0.5}),
        ("cat", 0.63),
    )
    check(
        "fit_context",
        lambda: _roles(fit_context(TEST_CHAT, 6)),
        ["system", "assistant", "user"],
    )
    check("fit tiny", lambda: _roles(fit_context(TEST_CHAT, 2)), ["system"])
