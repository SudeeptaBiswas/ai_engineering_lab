"""Part 2 of 2: test YOUR 2.5 part 2 code (embed, search): 4 fakes + 1 real.

Replace each `pytest.fail(...)` line with test code. Run until all pass:
  uv run pytest 01_python_fundamentals/1_9_pytest/exercises_1_9_2_ollama.py -v
Ollama off? Add -m "not ollama" to skip the real test.
"""

import httpx  # pyright: ignore[reportUnusedImport] — until you use it
import pytest

import exercises_2_5_2_ollama as search_module  # pyright: ignore[reportUnusedImport]
from exercises_2_5_2_ollama import NOTES, embed, search  # pyright: ignore[reportUnusedImport]

LOGIN_QUERY = "I can't log in to my account"

# ---------- Fake embeddings (done for you) ----------
# 2 numbers per text instead of 768: [about logging in, about other things].
FAKE_VECTORS: dict[str, list[float]] = {
    LOGIN_QUERY: [1.0, 0.0],
    NOTES[0]: [0.9, 0.1],  # password note: nearest to the login query
    NOTES[1]: [0.3, 0.7],
    NOTES[2]: [0.2, 0.8],
    NOTES[3]: [0.0, 1.0],
    NOTES[4]: [0.5, 0.5],
}


def fake_embed(texts: list[str], model: str = "any") -> list[list[float]]:
    """Stands in for embed(): looks each text up in FAKE_VECTORS.

    Args:
        texts: e.g. [LOGIN_QUERY]. Each must be a key of FAKE_VECTORS.
        model: not used (same parameters as the real embed).
    Returns:
        One fake vector per text, same order.
    """
    vectors: list[list[float]] = []
    for text in texts:
        vectors.append(FAKE_VECTORS[text])
    return vectors


# ---------- Your tests ----------
def test_search_login_fake(monkeypatch: pytest.MonkeyPatch) -> None:
    """search(LOGIN_QUERY, NOTES, 1) gives [NOTES[0]], using fake_embed.

    Swap embed INSIDE your 2.5 module, where search() looks it up:
      monkeypatch.setattr(search_module, "embed", fake_embed)
    Args:
        monkeypatch: built-in pytest fixture.
    """
    monkeypatch.setattr(search_module, "embed", fake_embed)

    result = search(LOGIN_QUERY, NOTES, 1)
    assert result == [NOTES[0]]


def test_search_k_2_fake(monkeypatch: pytest.MonkeyPatch) -> None:
    """With fake_embed, k=2 for LOGIN_QUERY gives NOTES[0], then NOTES[4].

    Args:
        monkeypatch: built-in pytest fixture.
    """
    monkeypatch.setattr(search_module, "embed", fake_embed)
    result = search(LOGIN_QUERY, NOTES, 2)
    assert result == [NOTES[0], NOTES[4]]


def test_embed_sends_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """embed(["cat"], model="qwen3:1.7b") must SEND "qwen3:1.7b".

    (The bug you fixed in 2.5: line 32 always sent EMBED_MODEL.)
    Write a fake_post(url: str, json: dict[str, object], timeout: float)
    that saves `json` in a list, then returns
      httpx.Response(200, json={"embeddings": [[0.0]]},
                     request=httpx.Request("POST", url))
    Swap it in with monkeypatch.setattr(httpx, "post", fake_post).
    Assert the saved body's "model" is "qwen3:1.7b".
    Args:
        monkeypatch: built-in pytest fixture.
    """
    sent_bodies: list[dict[str, object]] = []

    def fake_post(url: str, json: dict[str, object], timeout: float) -> httpx.Response:
        sent_bodies.append(json)  # write down what embed() sent
        return httpx.Response(200, json={"embeddings": [[0.0]]},
                            request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)
    embed(["cat"], model="qwen3:1.7b")
    assert len(sent_bodies) == 1  # 5. exactly one HTTP call
    assert sent_bodies[0]["model"] == "qwen3:1.7b"  # 6. the model it sent


def test_embed_bad_status(monkeypatch: pytest.MonkeyPatch) -> None:
    """A 501 reply makes embed raise httpx.HTTPStatusError.

    Same idea as above: a fake_post that returns status 501.
    Args:
        monkeypatch: built-in pytest fixture.
    """
    def fake_post(url: str, json: dict[str, object], timeout: float) -> httpx.Response:
        """Stands in for httpx.post: always 501, like a chat model on /api/embed."""
        return httpx.Response(501, json={"error": "does not support embeddings"},
                            request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)
    with pytest.raises(httpx.HTTPStatusError):
        embed(["cat"], model="qwen3:1.7b")


@pytest.mark.ollama
def test_search_real() -> None:
    """Real Ollama: search("my kitten naps a lot", NOTES, 1) gives [NOTES[3]].

    No fakes: this one proves the real model agrees with your code.
    """
    result = search("my kitten naps a lot", NOTES, 1)
    assert result == [NOTES[3]]
