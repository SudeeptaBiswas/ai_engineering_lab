"""Part 2 of 2: fake Ollama with monkeypatch, plus 1 real test with a marker.

Run all (needs Ollama for the last test):
  uv run pytest 01_python_fundamentals/1_9_pytest/examples_1_9_2_fakes.py -v
Skip the real one (Ollama off):
  uv run pytest 01_python_fundamentals/1_9_pytest/examples_1_9_2_fakes.py -v -m "not ollama"
"""

import httpx  # HTTP client (lesson 1.7)
import pytest

OLLAMA_URL = "http://127.0.0.1:11434"


# ---------- The code under test ----------
def model_names() -> list[str]:
    """Names of the models Ollama has, like `ollama list`.

    Returns:
        e.g. ["nomic-embed-text:latest", "qwen3:1.7b"].
    Raises:
        httpx.HTTPStatusError on a bad status (e.g. 500).
    """
    response = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=10.0)
    response.raise_for_status()
    names: list[str] = []
    for model in response.json()["models"]:  # [{"name": "qwen3:1.7b", ...}, ...]
        names.append(model["name"])
    return names


# ---------- 1. A fake reply, built by hand ----------
# httpx.Response(status, json=...) = the object httpx.get would return.
# request= is needed so raise_for_status() can say which URL failed.
def fake_reply(status: int, body: object) -> httpx.Response:
    """The reply a real Ollama would send, without calling Ollama.

    Args:
        status: HTTP status, e.g. 200 or 500.
        body: what .json() gives back, e.g. {"models": []}.
    Returns:
        A ready httpx.Response.
    """
    request = httpx.Request("GET", f"{OLLAMA_URL}/api/tags")
    return httpx.Response(status, json=body, request=request)


# ---------- 2. monkeypatch: swap a function for one test ----------
# monkeypatch.setattr(httpx, "get", fake_get) means: while this test runs,
# httpx.get IS fake_get. After the test, pytest puts the real one back.
# monkeypatch is a built-in fixture: just name it as a parameter.
# Java (Mockito): when(client.get(any())).thenReturn(fakeReply)
def test_model_names_fake(monkeypatch: pytest.MonkeyPatch) -> None:
    """2 models in the fake reply -> 2 names. No Ollama, no network.

    Args:
        monkeypatch: built-in pytest fixture that swaps things for one test.
    """
    def fake_get(url: str, timeout: float) -> httpx.Response:
        """Stands in for httpx.get: same parameters, no network.

        Args:
            url: what model_names() asked for (not used here).
            timeout: also not used.
        Returns:
            A 200 reply with 2 models.
        """
        return fake_reply(200, {"models": [{"name": "qwen3:1.7b"}, {"name": "qwen3:4b"}]})

    monkeypatch.setattr(httpx, "get", fake_get)
    assert model_names() == ["qwen3:1.7b", "qwen3:4b"]


# ---------- 3. Fakes make error cases easy ----------
# A real 500 needs a broken server. A fake needs one line.
def test_model_names_server_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """A 500 reply must raise HTTPStatusError (raise_for_status works).

    Args:
        monkeypatch: built-in pytest fixture.
    """
    def fake_get(url: str, timeout: float) -> httpx.Response:
        """Stands in for httpx.get: always a server error.

        Args:
            url: not used.
            timeout: not used.
        Returns:
            A 500 reply.
        """
        return fake_reply(500, {"error": "out of memory"})

    monkeypatch.setattr(httpx, "get", fake_get)
    with pytest.raises(httpx.HTTPStatusError):
        model_names()


# ---------- 4. One real test, with a marker ----------
# @pytest.mark.ollama = a label (declared in pyproject.toml).
# -m "not ollama" skips every test with that label. Java: @Tag("ollama")
# The fakes prove YOUR code; this one proves Ollama answers like the fake.
@pytest.mark.ollama
def test_model_names_real() -> None:
    """The real Ollama on this PC has the chat model from lesson 2.2."""
    assert "qwen3:1.7b" in model_names()
