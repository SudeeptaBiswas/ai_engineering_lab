"""Part 1 of 2: write pytest tests for YOUR 2.5 part 1 code. No Ollama.

Replace each `pytest.fail(...)` line with test code. Run until all pass:
  uv run pytest 01_python_fundamentals/1_9_pytest/exercises_1_9_1_cosine.py -v
Why pytest.fail and not `...`: a test with no assert PASSES. An empty test
that says PASS is worse than no test.
"""

import pytest

# Found via pyproject.toml (pythonpath + extraPaths): the 2.5 folder.
from exercises_2_5_1_cosine import COMPASS, COMPASS_VECS, cosine, dot, top_matches  # pyright: ignore[reportUnusedImport]


def test_dot_simple() -> None:
    """dot([1, 2, 3], [4, 5, 6]) is 32. A plain assert is enough (whole numbers)."""
    assert dot([1, 2, 3], [4, 5, 6]) == 32


def test_dot_lengths_differ() -> None:
    """dot([1, 2, 3], [1, 2]) raises ValueError with "lengths differ" in it.

    Use: with pytest.raises(..., match=...).
    """
    with pytest.raises(ValueError, match="lengths differ"):
        dot([1, 2, 3], [1, 2])


@pytest.mark.parametrize(
    ("vector_a", "vector_b", "expected"),
    [
        ([1.0, 2.0], [2.0, 4.0], 1.0),  # same way
        ([1.0, 0], [-1.0, 0], -1.0),
        ([1.0, 0], [0, 1.0], 0.0)
        # add 2 rows: opposite ([1, 0] vs [-1, 0]) and right angle ([1, 0] vs [0, 1])
    ],
)
def test_cosine_cases(vector_a: list[float], vector_b: list[float], expected: float) -> None:
    """Each row: cosine(vector_a, vector_b) is about `expected`.

    Floats: compare with pytest.approx, not ==.
    Args:
        vector_a: from one row, e.g. [1.0, 2.0].
        vector_b: from the same row, e.g. [2.0, 4.0].
        expected: from the same row, e.g. 1.0.
    """
    assert cosine(vector_a, vector_b) == pytest.approx(expected)


def test_cosine_zero_vector() -> None:
    """cosine([0, 0], [1, 2]) raises ValueError("zero vector")."""
    with pytest.raises(ValueError, match="zero vector"):
        cosine([0, 0], [1, 2])


def test_top_matches_top_2() -> None:
    """top_matches([1, 0], COMPASS_VECS, COMPASS, 2) gives east, then north-east.

    Check 2 things:
      1. the names, in order: ["east", "north-east"]
      2. the first score is about 0.995: pytest.approx(0.995, abs=0.001)
         (abs = allowed error; 0.995 is rounded, so the default is too strict)
    """
    result = top_matches([1, 0], COMPASS_VECS, COMPASS, 2)
    assert result[0][0] == "east"
    assert result[1][0] == "north-east"
    
    assert result[0][1] == pytest.approx(0.995, abs=0.001)
    assert result[1][1] == pytest.approx(0.707, abs=0.001)



@pytest.mark.parametrize("bad_k", [0, -1])
def test_top_matches_bad_k(bad_k: int) -> None:
    """k of 0 or less gives [] (no crash, no matches).

    Args:
        bad_k: from the list above, 0 then -1.
    """
    result = top_matches([1, 0], COMPASS_VECS, COMPASS, bad_k)
    assert result == []
