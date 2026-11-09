"""Part 1 of 2: pytest basics: assert, approx, raises, parametrize, fixture.

No Ollama needed. Run from the repo root:
  uv run pytest 01_python_fundamentals/1_9_pytest/examples_1_9_1_basics.py -v
pytest runs every function whose name starts with test_.
Java: JUnit runs every method marked @Test.
"""

import pytest  # the test runner. Java: JUnit 5


# ---------- The code under test (normally in its own file) ----------
def average(numbers: list[float]) -> float:
    """The mean of the numbers.

    Args:
        numbers: e.g. [1.0, 2.0, 3.0]. Must not be empty.
    Returns:
        e.g. 2.0.
    Raises:
        ValueError("empty list") if numbers is empty (would divide by 0).
    """
    if len(numbers) == 0:
        raise ValueError("empty list")
    return sum(numbers) / len(numbers)


def word_count(text: str) -> int:
    """How many words, split on any run of spaces.

    Args:
        text: e.g. "the cat sat".
    Returns:
        e.g. 3. "" -> 0.
    """
    return len(text.split())  # split() with no argument drops extra spaces


# ---------- 1. A test = a function named test_... with an assert ----------
# assert <condition>: nothing happens if True. If False, the test FAILs and
# pytest prints both sides. Java: assertEquals(2.0, average(...)).
def test_average_of_three() -> None:
    """The mean of 1, 2, 3 is 2."""
    assert average([1.0, 2.0, 3.0]) == 2.0


# ---------- 2. Floats: pytest.approx ----------
# (0.1 + 0.2) / 2 is 0.15000000000000002 in binary, so "== 0.15" is False.
# approx(0.15) allows a tiny error (1 millionth of the value by default).
# Java: assertEquals(0.15, actual, 1e-6) - the delta argument.
def test_average_float() -> None:
    """Float maths is never exact: compare with approx, not ==."""
    assert average([0.1, 0.2]) != 0.15  # proof: plain == fails
    assert average([0.1, 0.2]) == pytest.approx(0.15)


# ---------- 3. Errors: pytest.raises ----------
# The test passes only if the code inside the `with` raises that error.
# match= is a regex searched in the message.
# Java: assertThrows(IllegalArgumentException.class, () -> average(empty))
def test_average_empty_raises() -> None:
    """An empty list must raise ValueError("empty list")."""
    with pytest.raises(ValueError, match="empty list"):
        average([])


# ---------- 4. One test, many rows: parametrize ----------
# pytest runs the test once per row and reports each row on its own line:
# test_word_count[the cat sat-3] PASSED, ...
# Java: @ParameterizedTest + @CsvSource({"the cat sat,3", ...})
@pytest.mark.parametrize(
    ("text", "expected_count"),  # names = the test's parameters
    [
        ("the cat sat", 3),
        ("", 0),  # edge case: empty text
        ("  extra   spaces  ", 2),  # edge case: spaces everywhere
    ],
)
def test_word_count(text: str, expected_count: int) -> None:
    """Each row: word_count(text) gives expected_count.

    Args:
        text: from one row of the table, e.g. "the cat sat".
        expected_count: from the same row, e.g. 3.
    """
    assert word_count(text) == expected_count


# ---------- 5. Shared test data: a fixture ----------
# A fixture is a function pytest calls BEFORE a test. Its return value is
# passed to every test that has a parameter with the fixture's name.
# Java: a @BeforeEach method that fills a field.
@pytest.fixture
def exam_scores() -> list[float]:
    """Sample scores, made fresh for each test that asks for them.

    Returns:
        [70.0, 80.0, 90.0].
    """
    return [70.0, 80.0, 90.0]


def test_average_of_exam_scores(exam_scores: list[float]) -> None:
    """pytest sees the name exam_scores, calls the fixture, passes the list.

    Args:
        exam_scores: from the fixture above (matched by name).
    """
    assert average(exam_scores) == 80.0
