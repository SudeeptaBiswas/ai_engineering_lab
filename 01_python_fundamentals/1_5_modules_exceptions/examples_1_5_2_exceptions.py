"""Part 2 of 2: exceptions, using the real errors from 1.7 and 2.3.

Needs Ollama running. No text is generated: about 2 s in total
(1 s of it is waiting on a dead port, on purpose).
"""

import json  # json.loads (1.7)
from typing import Any  # "any type". Java: Object

import httpx  # HTTP client (1.7)

OLLAMA_URL = "http://127.0.0.1:11434"
DEAD_URL = "http://127.0.0.1:1"  # nothing listens here = "Ollama is off"

# ---------- 1. An error, its type, its parents ----------
# A real Ollama reply when the model is missing (measured, 2.3 endpoint):
reply = {"error": "model 'no-such-model' not found"}
try:  # Java: try {
    content = reply["message"]  # no such key -> KeyError
except KeyError as error:  # Java: catch (KeyError error)
    print("1.", type(error).__name__, "| message:", error)
    # __mro__ = the class, then its parents, up to `object`. Java: getSuperclass()
    parent_names: list[str] = []
    for cls in type(error).__mro__:
        parent_names.append(cls.__name__)
    print("   parents:", parent_names)

# ---------- 2. try / except / else / finally ----------
body: dict[str, Any] = {"model": "no-such-model", "messages": [], "stream": False}
try:
    response = httpx.post(f"{OLLAMA_URL}/api/chat", json=body, timeout=10.0)
    response.raise_for_status()  # 4xx / 5xx -> HTTPStatusError (1.7)
except httpx.HTTPStatusError as error:
    # The error carries the response: status and Ollama's own message
    print("\n2. status", error.response.status_code, "|", error.response.json()["error"])
else:  # runs only if the try had NO error. Java has no twin
    print("\n2. ok")
finally:  # runs always, error or not. Java: finally
    print("   finally: runs either way")

# ---------- 3. Several except: the first match wins ----------
# ConnectTimeout is a child of TransportError (1.7, section 4).
# Put the child first: a parent first would catch everything.
try:
    httpx.get(f"{DEAD_URL}/api/version", timeout=1.0)
except httpx.ConnectError:  # "connection refused" (not what Windows gives here)
    print("\n3. refused")
except httpx.TransportError as error:  # parent: refused, timeout, ...
    print("\n3. caught by the parent:", type(error).__name__)


# ---------- 4. Your own error type + raise ... from ----------
class OllamaError(Exception):
    """Base for our errors. Java: class OllamaException extends RuntimeException"""


class OllamaDownError(OllamaError):  # (Parent) = extends
    """Nothing answers at the URL."""


def ollama_version(url: str) -> str:
    """GET /api/version. Turns httpx's low-level error into a clear one."""
    try:
        return httpx.get(f"{url}/api/version", timeout=1.0).json()["version"]
    except httpx.TransportError as error:
        # `from error` keeps the original as __cause__.
        # Java: throw new OllamaDownException("...", error)
        raise OllamaDownError(f"no Ollama at {url}") from error


print("\n4. up:", ollama_version(OLLAMA_URL))
try:
    ollama_version(DEAD_URL)
except OllamaError as error:  # catching the PARENT also catches the child
    print("   down:", type(error).__name__, "|", error)
    print("   cause:", type(error.__cause__).__name__)

# ---------- 5. Ask first, or just try? ----------
settings = {"model": "qwen3:1.7b"}
# "Look before you leap": check first. Java style.
if "temperature" in settings:
    temperature = settings["temperature"]
else:
    temperature = "0.6"
# "Easier to ask forgiveness": just try. Common Python style.
try:
    temperature = settings["temperature"]
except KeyError:
    temperature = "0.6"
# concise: temperature = settings.get("temperature", "0.6")
print("\n5. temperature:", temperature)

# ---------- 6. Don't catch what you can't fix ----------
# Broken JSON: no good default exists, so let it go up to the caller.
try:
    json.loads("{temperature: 0.2}")  # keys need "double quotes"
except json.JSONDecodeError as error:  # here only to print it
    print("\n6.", type(error).__name__, "|", error)
    # [1] = the direct parent: so `except ValueError` would catch it too
    print("   parent:", type(error).__mro__[1].__name__)
