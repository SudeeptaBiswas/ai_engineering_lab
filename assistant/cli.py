"""The chat loop you type into. Start it from the repo root:

  uv run python -m assistant

YOUR PART: replace each `raise NotImplementedError` with code.
Spec = 02_llm_fundamentals/2_6_assistant_v1/exercises_2_6_3_cli.py
"""

import httpx  # pyright: ignore[reportUnusedImport] — httpx.HTTPError in main()

from assistant.memory import ChatMemory
from assistant.ollama_client import stream_chat  # pyright: ignore[reportUnusedImport]

SYSTEM_PROMPT = "You are a helpful assistant. Answer in 1 to 3 short sentences."
# Estimated tokens (chars / 4). Real ones ran 1.2-2.2x more (2.6 part 1),
# so 2000 + a 300-token answer stays under NUM_CTX 4096.
MAX_HISTORY_TOKENS = 2000
EXIT_COMMANDS = ("/exit", "/quit")
RESET_COMMAND = "/reset"


def answer(memory: ChatMemory, user_text: str) -> str:
    """One turn: remember the question, stream the reply to the screen,
    remember the reply, return it.

    Steps: memory.add("user", ...) -> print("bot> ", end="", flush=True) ->
    for each chunk of stream_chat(memory.messages()): print it the same way
    and keep it -> print() -> join the chunks -> memory.add("assistant", ...).
    Args:
        memory: the chat so far.
        user_text: e.g. "What is RAG?".
    Returns:
        The full reply, e.g. "RAG stands for ...".
    Raises:
        httpx.HTTPError: from stream_chat (main() catches it).
    """
    raise NotImplementedError("2.6: write answer()")


def main() -> None:
    """Read lines until /exit, /quit or end of input; answer each one.

    Per line, after .strip():
      /exit or /quit -> return
      /reset         -> memory.reset(), print a note, next line
      empty          -> next line (send nothing)
      anything else  -> answer(memory, line)
    input("you> ") raises EOFError on Ctrl+Z (Windows) / Ctrl+D: return.
    httpx.HTTPError from answer(): print a line with "error" and go on.
    Java: while (true) { String line = scanner.nextLine(); ... }
    """
    raise NotImplementedError("2.6: write main()")
