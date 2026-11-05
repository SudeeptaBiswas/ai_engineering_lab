"""Replace each `...` with code. Run until every line says PASS."""

from collections.abc import Callable  # type of a function, for check() below


def split_model_name(name: str) -> tuple[str, str]:
    """"qwen3:4b" -> ("qwen3", "4b"). No ":" -> tag is "latest" (Ollama's rule).
    Hint: str.partition(":") -> (before, ":", after); after is "" if no ":"."""
    ...


def size_gb(params_billion: float, bits: float) -> float:
    """File size in GB = params_billion x bits / 8, rounded to 1 decimal."""
    ...


def fits_in_ram(file_gb: float, free_ram_gb: float) -> bool:
    """True if file size x 1.3 (working memory) is <= free RAM."""
    ...


def biggest_that_fits(models: dict[str, float], free_ram_gb: float) -> str | None:
    """Name of the BIGGEST model (by GB) that fits_in_ram. None if none fits."""
    ...


def parse_stat(verbose_text: str, name: str) -> float:
    """Read one number from `ollama run --verbose` output.
    parse_stat(text, "eval rate") -> 7.1 from the line "eval rate:  7.10 tokens/s".
    Careful: "eval count" must NOT match the line "prompt eval count".
    Hint: splitlines(), strip(), partition(":"), split()[0], float(...)."""
    ...


def answer_seconds(
    output_tokens: int, tokens_per_second: float, load_seconds: float
) -> float:
    """Time to load the model + generate all tokens, rounded to 1 decimal."""
    ...


def thinking_share(total_tokens: int, answer_tokens: int) -> int:
    """Percent of tokens spent thinking (not in the answer). round() to int.
    0 tokens in total -> 0 (do not divide by zero)."""
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
        if actual == expected:
            result = "PASS"
        else:
            result = f"FAIL (got {actual!r}, expected {expected!r})"
    except Exception as error:  # Java: catch (Exception error)
        # type(error).__name__ = the error class name, e.g. "KeyError"
        result = f"FAIL ({type(error).__name__}: {error})"
    print(f"{label:<16} {result}")  # :<16 = pad label to 16 chars, left-aligned


TEST_MODELS = {"qwen3:1.7b": 1.4, "qwen3:4b": 2.5, "qwen3:8b": 5.2}  # name -> GB
# Real `ollama run qwen3:4b --verbose` output (10284Sudee, 2026-11-05)
TEST_VERBOSE = """total duration:       33.4080277s
load duration:        9.1925ms
prompt eval count:    22 token(s)
prompt eval rate:     7.43 tokens/s
eval count:           236 token(s)
eval rate:            7.10 tokens/s"""


# Runs only when you run this file directly (like public static void main)
if __name__ == "__main__":
    check("split", lambda: split_model_name("qwen3:4b"), ("qwen3", "4b"))
    check("split latest", lambda: split_model_name("llama3"), ("llama3", "latest"))
    check("size fp16", lambda: size_gb(8.0, 16), 16.0)
    check("size q4", lambda: size_gb(4.0, 5.0), 2.5)
    check("fits no", lambda: fits_in_ram(2.5, 3.0), False)
    check("fits yes", lambda: fits_in_ram(2.5, 4.0), True)
    check("biggest", lambda: biggest_that_fits(TEST_MODELS, 4.0), "qwen3:4b")
    check("biggest none", lambda: biggest_that_fits(TEST_MODELS, 1.0), None)
    check("stat rate", lambda: parse_stat(TEST_VERBOSE, "eval rate"), 7.1)
    check("stat count", lambda: parse_stat(TEST_VERBOSE, "eval count"), 236.0)
    check("seconds", lambda: answer_seconds(210, 7.0, 9.4), 39.4)
    check("think share", lambda: thinking_share(200, 50), 75)
    check("think zero", lambda: thinking_share(0, 0), 0)
