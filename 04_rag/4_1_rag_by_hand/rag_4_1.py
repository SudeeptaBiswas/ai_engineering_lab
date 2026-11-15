"""Lesson 4.1 exercises: RAG by hand. YOU fill the 6 functions that raise NotImplementedError.

Goal: answer a question from our own documents, in 3 steps: cut them into chunks,
find the chunks that fit the question, give only those to the model.
Fill the functions until every test in this folder passes:
  uv run pytest 04_rag/4_1_rag_by_hand -v          (Ollama off? add -m "not ollama")
Start with exercises_4_1_1_chunks.py (no Ollama), then exercises_4_1_2_search.py.
The settings at the top are given; don't change them. Style: docs/CODE_STYLE.md.
"""
# lesson-rules: user-code  (style problems here are shown as warnings, never block a commit)

import httpx  # pyright: ignore[reportUnusedImport] — until embed_texts uses it
import numpy as np
import numpy.typing as npt

from assistant.memory import Message
from lab_tools.log import cut_text, debug, log  # pyright: ignore[reportUnusedImport] — until your code logs

OLLAMA_URL = "http://127.0.0.1:11434"
CHAT_MODEL = "qwen3:1.7b"
EMBEDDING_MODEL = "nomic-embed-text"  # 768 numbers per text, each vector has length 1.0 (2.5)
HEADING_START = "## "  # a Markdown section heading; "### " (a sub-heading) does not match
CHUNK_SEPARATOR = "\n\n---\n\n"  # between chunks in the prompt, so the model sees where one ends
# Same words as examples_4_1_3_answer.py, where RAG got 11/12 right
RAG_SYSTEM_PROMPT = ("You are the support assistant for Lumen Notes. Answer in 1 to 2 sentences. "
                     "Use only the text below. If the text does not say, answer: I don't know.")
REQUEST_TIMEOUT_SECONDS = 300.0

EmbeddingMatrix = npt.NDArray[np.float64]  # one row per text, 768 columns (numbers)


@debug
def split_by_headings(document_text: str) -> list[str]:
    """Cut a Markdown document into chunks, one per "## " section, heading included.

    How:
        1. Go through the lines. A line starting with HEADING_START begins a new chunk.
        2. Text before the first heading is a chunk too (e.g. the title).
        3. Strip spaces and empty lines at both ends of each chunk; skip empty chunks.
    Args:
        document_text: e.g. "# Title\\n\\n## Refunds\\nWithin 14 days.\\n## Sync\\nEvery 60 s."
    Returns:
        e.g. ["# Title", "## Refunds\\nWithin 14 days.", "## Sync\\nEvery 60 s."]; [] for "".
    """
    raise NotImplementedError


@debug
def split_by_size(document_text: str, chunk_size: int, overlap: int) -> list[str]:
    """Cut a text into pieces of chunk_size characters; each piece repeats the last `overlap` characters.

    How:
        1. Check the numbers: chunk_size > 0 and 0 <= overlap < chunk_size.
        2. Take document_text[start : start + chunk_size]; move start on by chunk_size - overlap.
        3. Stop after the piece that reaches the end of the text.
    Args:
        document_text: e.g. "abcdefghij".
        chunk_size: characters per piece, e.g. 4.
        overlap: characters shared with the piece before, e.g. 1.
    Returns:
        e.g. ["abcd", "defg", "ghij"]; [] for "".
    Raises:
        ValueError: e.g. overlap 4 with chunk_size 4 (start would never move).
    """
    raise NotImplementedError


@debug
def embed_texts(texts: list[str]) -> EmbeddingMatrix:
    """Turn texts into vectors with one POST /api/embed (all texts in one call, 2.5).

    How:
        1. Empty list -> ValueError (nothing to embed).
        2. POST {"model": EMBEDDING_MODEL, "input": texts}; raise_for_status().
        3. reply["embeddings"] is a list of lists -> np.array(..., dtype=np.float64).
    Args:
        texts: e.g. ["Refunds within 14 days.", "Sync every 60 seconds."].
    Returns:
        A matrix with one row per text, e.g. shape (2, 768).
    Raises:
        ValueError: texts is empty.
        httpx.HTTPStatusError: bad status, e.g. 404 = model not pulled.
    """
    raise NotImplementedError


@debug
def find_top_chunks(question_vector: npt.NDArray[np.float64], chunk_vectors: EmbeddingMatrix,
                    top_k: int) -> list[int]:
    """Find the chunks closest in meaning to the question: their row numbers, best first.

    How:
        1. Scores: chunk_vectors @ question_vector = one dot product per chunk.
           The vectors have length 1, so dot = cosine (2.5).
        2. Sort best first: np.argsort(-scores, kind="stable") (equal scores keep their order).
        3. Keep the first top_k row numbers, as plain ints.
    Args:
        question_vector: shape (768,), from embed_texts([question])[0].
        chunk_vectors: shape (number of chunks, 768).
        top_k: how many to keep, e.g. 3. More than there are -> all; 0 or less -> [].
    Returns:
        e.g. [12, 3, 40].
    """
    raise NotImplementedError


@debug
def build_rag_messages(question: str, top_chunk_texts: list[str]) -> list[Message]:
    """Build the chat messages, so the model reads the found chunks before the question.

    How:
        1. Join the chunks with CHUNK_SEPARATOR.
        2. System message = RAG_SYSTEM_PROMPT, an empty line, then the joined chunks.
        3. User message = the question, alone.
    Args:
        question: e.g. "How long does the password reset link work?".
        top_chunk_texts: e.g. ["## Passwords and sign-in\\n...expires after 15 minutes..."].
    Returns:
        [{"role": "system", "content": RAG_SYSTEM_PROMPT + "\\n\\n" + the chunks joined by
          CHUNK_SEPARATOR}, {"role": "user", "content": question}].
    """
    raise NotImplementedError


@debug
def answer_question(question: str, chunk_texts: list[str], chunk_vectors: EmbeddingMatrix, top_k: int) -> str:
    """Answer a question from the documents: find the best chunks, then ask the model with them.

    How:
        1. Embed the question (embed_texts).
        2. Find the best rows (find_top_chunks) and take those chunk texts.
        3. Build the messages (build_rag_messages).
        4. POST /api/chat: model CHAT_MODEL, stream False, think False,
           options {"temperature": 0, "seed": 42, "num_predict": 200}; raise_for_status().
        5. Return reply["message"]["content"].
    Args:
        question: e.g. "How long does the password reset link work?".
        chunk_texts: all chunks, e.g. from split_by_headings.
        chunk_vectors: their vectors, same order, from embed_texts(chunk_texts).
        top_k: chunks to put in the prompt, e.g. 3.
    Returns:
        e.g. "The reset link expires after 15 minutes."
    """
    raise NotImplementedError

