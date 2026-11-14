"""Tests for rag_4_1.py, part 2: embed, search, prompt, answer. 9 without Ollama + 3 real.

  uv run pytest 04_rag/4_1_rag_by_hand/exercises_4_1_2_search.py -v
Ollama off? Add -m "not ollama".
"""

from pathlib import Path
from typing import Any

import httpx
import numpy as np
import pytest

from lab_tools.log import debug, log
from rag_4_1 import (CHUNK_SEPARATOR, EMBEDDING_MODEL, RAG_SYSTEM_PROMPT, EmbeddingMatrix, answer_question,
                     build_rag_messages, embed_texts, find_top_chunks, split_by_headings)

FOLDER = Path(__file__).parent
# Toy 2-number vectors (2.5 part 2): [about animals, about money], length 1
TOY_CHUNK_VECTORS = np.array([[0.0, 1.0],     # row 0: "invoice"  -> points north
                              [1.0, 0.0],     # row 1: "animal"   -> points east
                              [0.8, 0.6]])    # row 2: "pet costs" -> in between
EAST_QUESTION = np.array([1.0, 0.0])          # a question about animals


@pytest.mark.parametrize(("top_k", "expected_rows"), [
    (1, [1]),          # the closest: "animal"
    (2, [1, 2]),       # then "pet costs" (0.8), not "invoice" (0.0)
    (3, [1, 2, 0]),    # all, best first
    (10, [1, 2, 0]),   # more than there are: all
    (0, []),           # nothing asked: nothing
])
@debug
def test_find_top_chunks_best_first(top_k: int, expected_rows: list[int]) -> None:
    """Checks: row numbers sorted by score (dot product), best first, at most top_k.

    Args:
        top_k: how many rows to ask for.
        expected_rows: the rows it should give.
    """
    top_rows = find_top_chunks(EAST_QUESTION, TOY_CHUNK_VECTORS, top_k)
    log.debug("expected=%s got=%s", expected_rows, top_rows)
    assert top_rows == expected_rows
    for row_number in top_rows:
        assert type(row_number) is int  # plain int, not numpy.int64 (prints and compares like Python)


@debug
def test_find_top_chunks_equal_scores_keep_their_order() -> None:
    """Checks: two chunks with the same score stay in document order (a stable sort)."""
    twin_vectors = np.array([[0.0, 1.0], [1.0, 0.0], [1.0, 0.0]])  # rows 1 and 2 are equal
    top_rows = find_top_chunks(EAST_QUESTION, twin_vectors, 2)
    log.debug("expected=[1, 2] got=%s", top_rows)
    assert top_rows == [1, 2]


@debug
def test_build_rag_messages() -> None:
    """Checks: rules + chunks (with separators) in the system message, the question alone as user."""
    question = "How long does the reset link work?"
    chunk_texts = ["## Passwords\nExpires after 15 minutes.", "## Sign-up\nLink works 48 hours."]
    expected_system_text = RAG_SYSTEM_PROMPT + "\n\n" + chunk_texts[0] + CHUNK_SEPARATOR + chunk_texts[1]
    rag_messages = build_rag_messages(question, chunk_texts)
    log.debug("got=%s", rag_messages)
    assert rag_messages == [{"role": "system", "content": expected_system_text},
                            {"role": "user", "content": question}]


def fake_embed_post(sent_bodies: list[Any]) -> Any:
    """Build a stand-in for httpx.post that answers /api/embed with 3-number vectors, one per text.

    Args:
        sent_bodies: an empty list; each call's json= body is added to it.
    Returns:
        A function used like httpx.post.
    """
    def fake_post(url: str, **options: Any) -> httpx.Response:
        """Save the body; answer with vectors [1, 0, 0], [2, 0, 0], ...

        Args:
            url: e.g. "http://127.0.0.1:11434/api/embed".
            options: json=..., timeout=...
        Returns:
            A 200 response holding {"embeddings": [...]}.
        """
        request_body = options["json"]
        sent_bodies.append(request_body)
        fake_vectors: list[list[float]] = []
        for text_number in range(len(request_body["input"])):
            fake_vectors.append([float(text_number + 1), 0.0, 0.0])
        fake_request = httpx.Request("POST", url)  # raise_for_status needs to know the request
        fake_response = httpx.Response(200, json={"embeddings": fake_vectors}, request=fake_request)
        return fake_response
    return fake_post


@debug
def test_embed_texts_sends_all_texts_in_one_call(monkeypatch: pytest.MonkeyPatch) -> None:
    """Checks: one POST for all texts (batching, 2.5), the right model, and a float matrix back.

    Args:
        monkeypatch: pytest's tool to swap httpx.post for a fake.
    """
    sent_bodies: list[Any] = []
    monkeypatch.setattr(httpx, "post", fake_embed_post(sent_bodies))
    embedding_matrix = embed_texts(["first text", "second text"])
    log.debug("sent=%s shape=%s", sent_bodies, embedding_matrix.shape)
    assert sent_bodies == [{"model": EMBEDDING_MODEL, "input": ["first text", "second text"]}]
    assert embedding_matrix.shape == (2, 3)
    assert embedding_matrix.dtype == np.float64
    assert embedding_matrix[1, 0] == 2.0


@debug
def test_embed_texts_rejects_an_empty_list() -> None:
    """Checks: no texts -> ValueError before any HTTP call."""
    with pytest.raises(ValueError):
        embed_texts([])


# ---------- Real Ollama ----------
@pytest.fixture(scope="module")
def handbook_chunks_and_vectors() -> tuple[list[str], EmbeddingMatrix]:
    """Cut the handbook by headings and embed every chunk, once for all real tests in this file.

    Returns:
        (chunk texts, their vectors), e.g. 14 texts and a (14, 768) matrix.
    """
    handbook_text = (FOLDER / "handbook_4_1.md").read_text(encoding="utf-8")
    chunk_texts = split_by_headings(handbook_text)
    chunk_vectors = embed_texts(chunk_texts)
    return (chunk_texts, chunk_vectors)


@pytest.mark.ollama
@debug
def test_real_vectors_have_length_one(handbook_chunks_and_vectors: tuple[list[str], EmbeddingMatrix]) -> None:
    """Checks: 768 numbers per chunk and length 1.0, so a dot product is the cosine (2.5).

    Args:
        handbook_chunks_and_vectors: the embedded handbook.
    """
    chunk_vectors = handbook_chunks_and_vectors[1]
    vector_lengths = np.linalg.norm(chunk_vectors, axis=1)  # one length per row
    log.debug("shape=%s lengths %.4f-%.4f", chunk_vectors.shape, vector_lengths.min(), vector_lengths.max())
    assert chunk_vectors.shape[1] == 768
    assert np.allclose(vector_lengths, 1.0, atol=0.001)


@pytest.mark.ollama
@debug
def test_real_search_finds_the_refund_section(handbook_chunks_and_vectors: tuple[list[str], EmbeddingMatrix]) -> None:
    """Checks: a question in other words than the text ("money back") still finds "## Refunds" first.

    Args:
        handbook_chunks_and_vectors: the embedded handbook.
    """
    chunk_texts = handbook_chunks_and_vectors[0]
    chunk_vectors = handbook_chunks_and_vectors[1]
    question_vectors = embed_texts(["Can I get my money back?"])
    top_rows = find_top_chunks(question_vectors[0], chunk_vectors, 1)
    best_chunk = chunk_texts[top_rows[0]]
    log.debug("best chunk=%r", best_chunk[:40])
    assert best_chunk.startswith("## Refunds")


@pytest.mark.ollama
@debug
def test_real_answer_uses_the_handbook(handbook_chunks_and_vectors: tuple[list[str], EmbeddingMatrix]) -> None:
    """Checks the whole RAG chain: the model alone said "10 minutes"; with the found chunks, "15 minutes".

    Args:
        handbook_chunks_and_vectors: the embedded handbook.
    """
    chunk_texts = handbook_chunks_and_vectors[0]
    chunk_vectors = handbook_chunks_and_vectors[1]
    answer_text = answer_question("How long does the password reset link work?", chunk_texts, chunk_vectors, 3)
    log.debug("expected '15 minutes' in %r", answer_text)
    assert "15 minutes" in answer_text
