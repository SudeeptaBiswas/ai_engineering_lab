"""Part 1 of 2: cut the documents into chunks, embed them, search with numpy. Needs Ollama + nomic-embed-text.

Run (~15 s):
  uv run python 04_rag/4_1_rag_by_hand/examples_4_1_1_search.py

  1. documents : how big are the handbook + release notes?
  2. chunks    : cut by "## " headings vs every 500 characters
  3. search    : 3 questions -> the 3 best chunks, with scores
  4. speed     : numpy vs a Python loop, 122 and 20 000 chunks
"""

import time  # time.perf_counter() = a stopwatch
from pathlib import Path

import httpx
import numpy as np
import numpy.typing as npt

from lab_tools.log import cut_text, debug, log

OLLAMA_URL = "http://127.0.0.1:11434"
EMBEDDING_MODEL = "nomic-embed-text"
FOLDER = Path(__file__).parent  # this file's folder
DOCUMENT_FILE_NAMES = ["handbook_4_1.md", "release_notes_4_1.md"]
CHARACTERS_PER_TOKEN = 4  # rough rule (2.1); real counts were ~1.1x more here
SEARCH_QUESTIONS = ["Can I get my money back?", "In which app version did dark mode arrive?",
                    "How long does the password reset link work?"]
TOP_K = 3

Matrix = npt.NDArray[np.float64]  # rows = texts, columns = numbers


@debug
def load_documents() -> str:
    """Read both Markdown files and join them into one text.

    Returns:
        The handbook, an empty line, then the release notes (~26 000 characters).
    """
    document_texts: list[str] = []
    for file_name in DOCUMENT_FILE_NAMES:
        file_path = FOLDER / file_name  # / joins path parts
        document_texts.append(file_path.read_text(encoding="utf-8"))
    all_text = "\n\n".join(document_texts)
    log.debug("result: %d characters", len(all_text))
    return all_text


def chunk_by_headings(document_text: str) -> list[str]:
    """Cut the text before every line that starts with "## ", so each section is one chunk.

    Args:
        document_text: e.g. load_documents().
    Returns:
        e.g. ["# Lumen Notes support handbook ...", "## Accounts and sign-up ...", ...].
    """
    chunks: list[str] = []
    current_lines: list[str] = []
    for line in document_text.split("\n"):
        starts_new_section = line.startswith("## ")
        if starts_new_section and len(current_lines) > 0:
            chunks.append("\n".join(current_lines).strip())
            current_lines = []
        current_lines.append(line)
    chunks.append("\n".join(current_lines).strip())
    return chunks


def chunk_by_size(document_text: str, chunk_size: int, overlap: int) -> list[str]:
    """Cut the text every chunk_size characters; each piece repeats the last `overlap` characters.

    Args:
        document_text: e.g. load_documents().
        chunk_size: e.g. 500.
        overlap: e.g. 100, so a sentence cut at a border is whole in one of the two pieces.
    Returns:
        e.g. 65 pieces of up to 500 characters.
    """
    chunks: list[str] = []
    start = 0
    while start < len(document_text):
        end = start + chunk_size
        chunks.append(document_text[start:end])
        if end >= len(document_text):  # this piece reached the end: no extra piece
            break
        start = start + chunk_size - overlap
    return chunks


@debug
def embed_texts(texts: list[str]) -> Matrix:
    """Turn many texts into vectors with ONE call (batching, 2.5).

    Args:
        texts: e.g. 122 chunks.
    Returns:
        A matrix, one row per text, e.g. shape (122, 768).
    """
    request_body = {"model": EMBEDDING_MODEL, "input": texts}
    response = httpx.post(f"{OLLAMA_URL}/api/embed", json=request_body, timeout=300.0)
    response.raise_for_status()
    embeddings = response.json()["embeddings"]  # a list of lists of numbers
    embedding_matrix = np.array(embeddings, dtype=np.float64)  # list of lists -> a 2-D numpy array
    log.debug("result: shape %s", embedding_matrix.shape)
    return embedding_matrix


@debug
def top_rows_by_score(question_vector: npt.NDArray[np.float64], chunk_vectors: Matrix, top_k: int) -> list[int]:
    """Score every chunk against the question in one step, then keep the best row numbers.

    Args:
        question_vector: shape (768,).
        chunk_vectors: shape (number of chunks, 768).
        top_k: e.g. 3.
    Returns:
        Row numbers, best first, e.g. [7, 2, 30].
    """
    scores = chunk_vectors @ question_vector  # @ = matrix times vector: one dot product per row
    best_first = np.argsort(-scores)  # argsort sorts low -> high; minus flips it to high -> low
    top_rows: list[int] = []
    for row_number in best_first[:top_k]:
        top_rows.append(int(row_number))  # numpy.int64 -> plain int
    log.debug("result: %s", top_rows)
    return top_rows


def show_search(question: str, chunk_texts: list[str], chunk_vectors: Matrix) -> None:
    """Print the top chunks for one question: score + first line of each.

    Args:
        question: e.g. "Can I get my money back?".
        chunk_texts: the chunks.
        chunk_vectors: their vectors, same order.
    """
    question_vectors = embed_texts([question])
    question_vector = question_vectors[0]  # [0] = the only row
    top_rows = top_rows_by_score(question_vector, chunk_vectors, TOP_K)
    print(f"  {question}")
    for row_number in top_rows:
        score = float(chunk_vectors[row_number] @ question_vector)
        first_line = chunk_texts[row_number].split("\n")[0]
        print(f"    {score:.2f}  {first_line[:60]}")


def python_loop_scores(question_vector: list[float], chunk_vectors: list[list[float]]) -> list[float]:
    """The same scores without numpy: a dot product per chunk, written as loops (2.5).

    Args:
        question_vector: 768 numbers.
        chunk_vectors: one list of 768 numbers per chunk.
    Returns:
        One score per chunk.
    """
    scores: list[float] = []
    for chunk_vector in chunk_vectors:
        total = 0.0
        for position in range(len(question_vector)):
            total += question_vector[position] * chunk_vector[position]
        scores.append(total)
    return scores


def compare_speed(chunk_count: int) -> None:
    """Time numpy vs the Python loop on random unit vectors (no Ollama needed).

    Args:
        chunk_count: e.g. 122 or 20000.
    """
    random_generator = np.random.default_rng(42)  # seed 42: same numbers every run
    chunk_vectors = random_generator.normal(size=(chunk_count, 768))
    chunk_vectors = chunk_vectors / np.linalg.norm(chunk_vectors, axis=1, keepdims=True)  # length 1 each
    question_vector = chunk_vectors[0]
    start = time.perf_counter()
    top_rows_by_score(question_vector, chunk_vectors, TOP_K)
    numpy_seconds = time.perf_counter() - start
    start = time.perf_counter()
    python_loop_scores(question_vector.tolist(), chunk_vectors.tolist())
    loop_seconds = time.perf_counter() - start
    print(f"  {chunk_count:>6} chunks: numpy {numpy_seconds * 1000:.1f} ms, Python loop {loop_seconds * 1000:.0f} ms")


if __name__ == "__main__":
    all_text = load_documents()
    print(f"1. documents: {len(all_text)} characters, ~{len(all_text) // CHARACTERS_PER_TOKEN} tokens (estimate)\n")
    heading_chunks = chunk_by_headings(all_text)
    size_chunks = chunk_by_size(all_text, 500, 100)
    print(f"2. chunks: by heading {len(heading_chunks)}, by 500/100 characters {len(size_chunks)}")
    start = time.perf_counter()
    heading_vectors = embed_texts(heading_chunks)
    print(f"   embedded {len(heading_chunks)} chunks in {time.perf_counter() - start:.1f} s (once, then reused)\n")
    print("3. search (chunks by heading):")
    for search_question in SEARCH_QUESTIONS:
        show_search(search_question, heading_chunks, heading_vectors)
    print("\n4. speed:")
    compare_speed(len(heading_chunks))
    compare_speed(20000)
    log.debug("done; first chunk %s", cut_text(heading_chunks[0]))
