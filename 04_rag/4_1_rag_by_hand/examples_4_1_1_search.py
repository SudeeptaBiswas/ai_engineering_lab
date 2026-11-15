"""Part 1 of 3: cut the documents into chunks, embed them, search with numpy. Needs Ollama + nomic-embed-text.

Run (~15 s):
  uv run python 04_rag/4_1_rag_by_hand/examples_4_1_1_search.py

  1. documents : how big are the handbook + release notes?
  2. chunks    : cut by "## " headings vs every 500 characters
  3. search    : 3 questions -> the 3 best chunks, with scores
"""

import time  # time.perf_counter() = a stopwatch
from dataclasses import dataclass
from pathlib import Path

import httpx
import numpy as np
import numpy.typing as npt

from lab_tools.log import cut_text, debug, log

OLLAMA_URL = "http://127.0.0.1:11434"
EMBEDDING_MODEL = "nomic-embed-text"
LESSON_FOLDER = Path(__file__).parent  # this file's folder
DOCUMENT_FILE_NAMES = ["handbook_4_1.md", "release_notes_4_1.md"]
CHARACTERS_PER_TOKEN = 4  # rough rule (2.1); real counts were ~1.1x more here
SEARCH_QUESTIONS = ["Can I get my money back?", "In which app version did dark mode arrive?",
                    "How long does the password reset link work?"]
TOP_K = 3  # how many chunks to keep per question

EmbeddingMatrix = npt.NDArray[np.float64]  # one row per text, 768 columns (numbers)


@dataclass
class ScoredChunk:
    """One search hit: how close it is to the question, and its first line."""

    score: float  # dot product with the question vector, e.g. 0.64
    first_line: str  # e.g. "## Refunds"


@debug
def load_documents() -> str:
    """Read both Markdown files and join them into one text.

    Returns:
        The handbook, an empty line, then the release notes (~26 000 characters).
    """
    document_texts: list[str] = []
    for file_name in DOCUMENT_FILE_NAMES:
        file_path = LESSON_FOLDER / file_name  # / joins path parts
        file_text = file_path.read_text(encoding="utf-8")
        document_texts.append(file_text)
    documents_text = "\n\n".join(document_texts)
    log.debug("result: %d characters", len(documents_text))
    return documents_text


@debug
def chunk_by_headings(documents_text: str) -> list[str]:
    """Cut the text into chunks, one per "## " section, so each chunk is about one topic.

    How:
        1. Go through the lines and collect them.
        2. A line starting with "## " closes the chunk so far and starts a new one.
        3. After the last line, close the last chunk.
    Args:
        documents_text: e.g. load_documents().
    Returns:
        e.g. ["# Lumen Notes support handbook ...", "## Accounts and sign-up ...", ...].
    """
    log.debug("start: %d characters", len(documents_text))
    chunks: list[str] = []
    current_lines: list[str] = []
    for line in documents_text.split("\n"):
        starts_new_section = line.startswith("## ")
        if starts_new_section and len(current_lines) > 0:
            chunk_text = "\n".join(current_lines)  # lines -> one text
            chunks.append(chunk_text.strip())
            current_lines = []
        current_lines.append(line)
    last_chunk_text = "\n".join(current_lines)
    chunks.append(last_chunk_text.strip())
    log.debug("result: %d chunks", len(chunks))
    return chunks


@debug
def chunk_by_size(documents_text: str, chunk_size: int, overlap: int) -> list[str]:
    """Cut the text into pieces of chunk_size characters; each piece repeats the last `overlap` characters.

    How:
        1. Take the characters from start to start + chunk_size.
        2. Move start on by chunk_size - overlap.
        3. Stop after the piece that reaches the end of the text.
    Args:
        documents_text: e.g. load_documents().
        chunk_size: e.g. 500.
        overlap: e.g. 100, so a sentence cut at a border is whole in one of the two pieces.
    Returns:
        e.g. 65 pieces of up to 500 characters.
    """
    log.debug("start: %d characters, chunk_size=%d overlap=%d", len(documents_text), chunk_size, overlap)
    chunks: list[str] = []
    start = 0
    while start < len(documents_text):
        end = start + chunk_size
        chunks.append(documents_text[start:end])
        if end >= len(documents_text):  # this piece reached the end: no extra piece
            break
        start = start + chunk_size - overlap
    log.debug("result: %d chunks", len(chunks))
    return chunks


@debug
def embed_texts(texts: list[str]) -> EmbeddingMatrix:
    """Turn many texts into vectors with ONE call (batching, 2.5).

    Args:
        texts: e.g. 122 chunks.
    Returns:
        A matrix, one row per text, e.g. shape (122, 768).
    """
    log.debug("start: %d texts, first %s", len(texts), cut_text(texts[0]))
    request_body = {"model": EMBEDDING_MODEL, "input": texts}
    response = httpx.post(f"{OLLAMA_URL}/api/embed", json=request_body, timeout=300.0)
    response.raise_for_status()
    reply_json = response.json()
    embeddings = reply_json["embeddings"]  # a list of lists of numbers
    embedding_matrix = np.array(embeddings, dtype=np.float64)  # list of lists -> a 2-D numpy array
    log.debug("result: shape %s", embedding_matrix.shape)
    return embedding_matrix


@debug
def find_top_rows(question_vector: npt.NDArray[np.float64], chunk_vectors: EmbeddingMatrix,
                  top_k: int) -> list[int]:
    """Find the chunks closest in meaning to the question: their row numbers, best first.

    How:
        1. Score every chunk in one step: chunk_vectors @ question_vector.
        2. Sort the row numbers, highest score first.
        3. Keep the first top_k.
    Args:
        question_vector: shape (768,).
        chunk_vectors: shape (number of chunks, 768).
        top_k: e.g. 3.
    Returns:
        Row numbers, best first, e.g. [7, 2, 30].
    """
    log.debug("start: %d chunks, top_k=%d", chunk_vectors.shape[0], top_k)
    scores = chunk_vectors @ question_vector  # @ = matrix times vector: one dot product per row
    best_first = np.argsort(-scores)  # argsort sorts low -> high; minus flips it to high -> low
    top_rows: list[int] = []
    for row_number in best_first[:top_k]:
        top_rows.append(int(row_number))  # numpy.int64 -> plain int
    log.debug("result: %s", top_rows)
    return top_rows


@debug
def search_chunks(question: str, chunk_texts: list[str], chunk_vectors: EmbeddingMatrix) -> list[ScoredChunk]:
    """Find the TOP_K chunks for one question, with their scores, for printing.

    How:
        1. Embed the question.
        2. Find the best rows (find_top_rows).
        3. For each row: its score and the chunk's first line.
    Args:
        question: e.g. "Can I get my money back?".
        chunk_texts: the chunks.
        chunk_vectors: their vectors, same order.
    Returns:
        e.g. [ScoredChunk(0.64, "## Refunds"), ScoredChunk(0.55, "## Billing"), ...].
    """
    log.debug("start: question=%r", question)
    question_vectors = embed_texts([question])
    question_vector = question_vectors[0]  # [0] = the only row
    top_rows = find_top_rows(question_vector, chunk_vectors, TOP_K)
    scored_chunks: list[ScoredChunk] = []
    for row_number in top_rows:
        chunk_vector = chunk_vectors[row_number]
        score = float(chunk_vector @ question_vector)  # dot product; numpy number -> float
        chunk_lines = chunk_texts[row_number].split("\n")
        scored_chunks.append(ScoredChunk(score=score, first_line=chunk_lines[0]))
    log.debug("result: %s", scored_chunks)
    return scored_chunks


if __name__ == "__main__":
    documents_text = load_documents()
    estimated_tokens = len(documents_text) // CHARACTERS_PER_TOKEN
    print(f"1. documents: {len(documents_text)} characters, ~{estimated_tokens} tokens (estimate)\n")
    heading_chunks = chunk_by_headings(documents_text)
    size_chunks = chunk_by_size(documents_text, 500, 100)
    print(f"2. chunks: by heading {len(heading_chunks)}, by 500/100 characters {len(size_chunks)}")
    embed_start = time.perf_counter()
    heading_vectors = embed_texts(heading_chunks)
    embed_seconds = time.perf_counter() - embed_start
    print(f"   embedded {len(heading_chunks)} chunks in {embed_seconds:.1f} s (once, then reused)\n")
    print("3. search (chunks by heading):")
    for search_question in SEARCH_QUESTIONS:
        print(f"  {search_question}")
        for scored_chunk in search_chunks(search_question, heading_chunks, heading_vectors):
            print(f"    {scored_chunk.score:.2f}  {scored_chunk.first_line[:60]}")
