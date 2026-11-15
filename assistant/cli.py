"""The chat you type into: read a line, handle commands, answer questions.

Start it from the repo root:
  uv run python -m assistant            (add --debug to see the log)

Commands: /reset forgets the chat; /exit or /quit ends it.
Tests: 02_llm_fundamentals/2_6_assistant_v1/exercises_2_6_3_cli.py
"""

import httpx  # httpx.HTTPError: Ollama down or a bad status

from assistant.chat_turn import answer_one_turn
from assistant.memory import ChatMemory
from lab_tools.log import debug, log

# Measured 2026-11-15, 5 tool questions x 2 runs: this (the 3.3 prompt) 5/5 both runs.
# Adding "Answer in 1 to 3 short sentences." -> 3/5: it said "I will look up ..." and called nothing.
SYSTEM_PROMPT = "You are a support assistant. Use a tool whenever one fits; never guess numbers, dates or order details."
# Estimated tokens (characters / 4). Real ones ran 1.2-2.2x more (2.6 part 1),
# so 2000 + a 300-token answer stays under NUM_CTX 4096.
MAX_HISTORY_TOKENS = 2000
EXIT_COMMANDS = ("/exit", "/quit")
RESET_COMMAND = "/reset"
INPUT_PROMPT = "you> "
BYTE_ORDER_MARK = "﻿"  # invisible; strip() keeps it, so "/exit" would not match (seen 2026-11-15)


@debug
def read_typed_line() -> str | None:
    """Wait for the user to type one line.

    Returns:
        The line without spaces at the ends, e.g. "hi".
        None at the end of input (Ctrl+Z on Windows, Ctrl+D elsewhere).
    """
    try:
        raw_line = input(INPUT_PROMPT)
    except EOFError:  # input() raises this when there is no more input
        log.debug("result: None (end of input)")
        return None
    typed_line = raw_line.strip()  # drop spaces and the line break at both ends
    typed_line = typed_line.removeprefix(BYTE_ORDER_MARK)  # a PowerShell pipe adds it to line 1
    log.debug("result: %r", typed_line)
    return typed_line


@debug
def answer_and_survive_errors(memory: ChatMemory, user_question: str) -> None:
    """Answer one question; if Ollama fails, say so and keep the chat running.

    Args:
        memory: the chat so far.
        user_question: e.g. "What is RAG?".
    """
    log.debug("start: user_question=%r", user_question)
    try:
        answer_one_turn(memory, user_question)
    except httpx.HTTPError as http_error:
        log.debug("http_error=%r", http_error)
        print(f"\nerror: {http_error}. Is Ollama running?")


@debug
def main() -> None:
    """Run the chat until /exit, /quit or the end of input.

    How, for each typed line:
        /exit or /quit -> stop
        /reset         -> forget the chat, print a note
        empty line     -> skip it (send nothing)
        anything else  -> answer it
    """
    log.debug("start: max_history_tokens=%d", MAX_HISTORY_TOKENS)
    memory = ChatMemory(SYSTEM_PROMPT, MAX_HISTORY_TOKENS)
    while True:
        typed_line = read_typed_line()
        if typed_line is None or typed_line in EXIT_COMMANDS:
            log.debug("result: chat ended by %r", typed_line)
            return
        if typed_line == RESET_COMMAND:
            memory.forget_chat()
            print("(chat forgotten)")
            continue
        if typed_line == "":  # Enter on an empty line
            continue
        answer_and_survive_errors(memory, typed_line)
