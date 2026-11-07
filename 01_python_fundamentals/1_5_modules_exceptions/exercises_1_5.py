"""Replace each `...` with code. Run until every line says PASS.
Fill in chat_errors_1_5.py first (same folder): this file imports it.
Checks 1-11 need nothing. Checks 12-16 need Ollama with qwen3:1.7b.
Checks 14 + 15 wait ~1 s each: they call a dead port on purpose."""

import json  # pyright: ignore[reportUnusedImport] — json.loads
import tempfile  # temporary folder for the settings tests
from collections.abc import Callable  # type of a function (lab_tools/check.py)
from pathlib import Path
from typing import Any  # "any type". Java: Object

import httpx  # pyright: ignore[reportUnusedImport] — until you use it

from lab_tools.check import check  # numbered PASS/FAIL + path:line links
from lab_tools.log import debug, log  # pyright: ignore[reportUnusedImport]

# Your own module, next to this file (lesson, section 4: why this works).
# ( ... ) lets one import go over several lines.
from chat_errors_1_5 import (  # pyright: ignore[reportUnusedImport]
    ModelNotFoundError, OllamaDownError, OllamaError, answer_from)

OLLAMA_URL = "http://127.0.0.1:11434"  # not "localhost": 2 s slower on Windows
DEAD_URL = "http://127.0.0.1:1"  # nothing listens here = "Ollama is off"
MODEL = "qwen3:1.7b"
# 120 s to answer (slow CPU), but only 1 s to connect: "off" fails fast
TIMEOUT = httpx.Timeout(120.0, connect=1.0)
DEFAULTS: dict[str, Any] = {"model": MODEL, "temperature": 0.6}  # qwen3 (2.4)


# ---------- Raise your own errors ----------
def parse_temperature(text: str) -> float:
    """"0.7" -> 0.7. For the 2.6 chatbot command `/temp 0.7`.
    Not a number -> raise ValueError(f"not a number: {text!r}") FROM the
    error float() raised. Below 0 -> raise ValueError("must be 0 or more")."""
    ...


# ---------- Catch only what you can fix ----------
def load_settings(path: Path) -> dict[str, Any]:
    """A NEW dict: DEFAULTS, then the keys from the JSON file at `path` on top.
    No file -> just the defaults (the chatbot's first run).
    Broken JSON -> do NOT catch it: no good fix exists, let it go up.
    Hint: dict(DEFAULTS) = a copy. Java: new HashMap<>(DEFAULTS)"""
    ...


# ---------- Turn low-level errors into clear ones ----------
def ask(prompt: str, model: str = MODEL, url: str = OLLAMA_URL) -> str:
    """POST {url}/api/chat: one user message, stream False, think False,
    options num_predict 10, timeout=TIMEOUT. Then:
    - can't connect (httpx.TransportError) -> raise
      OllamaDownError(f"no Ollama at {url}") from that error
    - status 404 -> raise ModelNotFoundError(model)
    - otherwise -> answer_from(the reply as dict)"""
    ...


def ask_or_tip(prompt: str, model: str = MODEL, url: str = OLLAMA_URL) -> str:
    """ask(), but never raises those two errors. Returns a tip instead:
    model missing -> f"Run: ollama pull {model}"
    Ollama down   -> "Start Ollama: ollama serve" """
    ...


# ---------- Test helpers (done for you) ----------
def error_of(run: Callable[[], object]) -> str:
    """Run it. Return "ErrorType: message", or "no error"."""
    try:
        run()
    except Exception as error:  # Java: catch (Exception error)
        return f"{type(error).__name__}: {error}"
    return "no error"


def cause_of(run: Callable[[], object]) -> str:
    """Run it. Return the type of the error's __cause__ (set by `raise ... from`).
    No cause -> "NoneType". No error -> "no error"."""
    try:
        run()
    except Exception as error:
        return type(error.__cause__).__name__
    return "no error"


def _load_from(path: Path, text: str) -> dict[str, Any]:
    """Write `text` to `path`, then load_settings (a lambda holds one expression)."""
    path.write_text(text, encoding="utf-8")
    return load_settings(path)


if __name__ == "__main__":
    check("temp ok", lambda: parse_temperature("0.7"), 0.7)
    check("temp text", lambda: error_of(lambda: parse_temperature("hot")),
          "ValueError: not a number: 'hot'")
    check("temp cause", lambda: cause_of(lambda: parse_temperature("hot")), "ValueError")
    check("temp below 0", lambda: error_of(lambda: parse_temperature("-1")),
          "ValueError: must be 0 or more")
    # __base__ = the direct parent class. Java: getSuperclass()
    check("error family", lambda: (ModelNotFoundError.__base__, OllamaDownError.__base__),
          (OllamaError, OllamaError))
    check("answer ok", lambda: answer_from(
        {"message": {"role": "assistant", "content": " Hi "}}), "Hi")
    check("answer error", lambda: error_of(lambda: answer_from(
        {"error": "model 'x' not found"})), "OllamaError: model 'x' not found")
    with tempfile.TemporaryDirectory() as temp_name:  # deleted at the end
        temp = Path(temp_name)
        check("no settings", lambda: load_settings(temp / "none.json"), DEFAULTS)
        check("settings", lambda: _load_from(temp / "s.json", '{"temperature": 0.2}'),
              {"model": MODEL, "temperature": 0.2})
        check("defaults kept", lambda: DEFAULTS["temperature"], 0.6)
        check("broken json", lambda: error_of(
            lambda: _load_from(temp / "b.json", "{temperature: 0.2}")).split(":")[0],
              "JSONDecodeError")
    check("ask ok", lambda: len(ask("Say hi.")) > 0, True)
    check("ask no model", lambda: error_of(lambda: ask("hi", model="no-such-model")),
          "ModelNotFoundError: no-such-model")
    check("ask down", lambda: error_of(lambda: ask("hi", url=DEAD_URL)),
          f"OllamaDownError: no Ollama at {DEAD_URL}")
    check("tip down", lambda: ask_or_tip("hi", url=DEAD_URL), "Start Ollama: ollama serve")
    check("tip no model", lambda: ask_or_tip("hi", model="no-such-model"),
          "Run: ollama pull no-such-model")
