"""YOUR module for exercises 1.5: exercises_1_5.py imports it.
Fix the two class parents and replace the `...`.

Errors for talking to Ollama. Back in 2.6: the chatbot shows a tip
("Start Ollama: ollama serve") instead of a stack trace.
"""

from typing import Any  # "any type". Java: Object


class OllamaError(Exception):
    """Base for every Ollama problem. Done for you.
    Java: class OllamaException extends RuntimeException {}"""


class ModelNotFoundError(Exception):
    """Ollama is up, but this model is not pulled (HTTP 404).
    TODO: make it a child of OllamaError, so `except OllamaError` catches it."""


class OllamaDownError(Exception):
    """Nothing answers at the Ollama URL (connect failed or timed out).
    TODO: make it a child of OllamaError."""


def answer_from(reply: dict[str, Any]) -> str:
    """The text of a /api/chat reply (2.3), .strip()-ed.
    Reply has an "error" key -> raise OllamaError with that text.
    Real one (measured): {"error": "model 'no-such-model' not found"}"""
    ...
