"""Tests for rag_4_1.py, part 2: embed, search, prompt, answer. 9 without Ollama + 3 real.

  uv run pytest 04_rag/4_1_rag_by_hand/exercises_4_1_2_search.py -v
Ollama off? Add -m "not ollama".
"""

from pathlib import Path
from typing import Any, NamedTuple

import httpx
import numpy as np
import pytest

from lab_tools.log import cut_text, debug, log
from rag_4_1 import (CHUNK_SEPARATOR, EMBEDDING_MODEL, RAG_SYSTEM_PROMPT, EmbeddingMatrix, answer_question,
                     build_rag_messages, embed_texts, find_top_chunks, split_by_headings)

LESSON_FOLDER = Path(__file__).parent
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
    (-1, []),          # a negative number: nothing, not a crash
])
@debug
def test_find_top_chunks_gives_best_rows_first(top_k: int, expected_rows: list[int]) -> None:
    """Row numbers sorted by score (dot product), best first, at most top_k: the prompt gets the best chunks.

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
    """Two chunks with the same score stay in document order (a stable sort): same input, same answer."""
    twin_vectors = np.array([[0.0, 1.0], [1.0, 0.0], [1.0, 0.0]])  # rows 1 and 2 are equal
    top_rows = find_top_chunks(EAST_QUESTION, twin_vectors, 2)
    log.debug("expected=[1, 2] got=%s", top_rows)
    assert top_rows == [1, 2]


@debug
def test_build_rag_messages_puts_chunks_in_system_and_question_in_user() -> None:
    """Rules + chunks (with separators) in the system message, the question alone as user.

    Why: the model must see the rules and the documents before the question.
    """
    question = "How long does the reset link work?"
    passwords_chunk = "## Passwords\nExpires after 15 minutes."
    sign_up_chunk = "## Sign-up\nLink works 48 hours."
    expected_system_text = RAG_SYSTEM_PROMPT + "\n\n" + passwords_chunk + CHUNK_SEPARATOR + sign_up_chunk
    expected_messages = [{"role": "system", "content": expected_system_text}, {"role": "user", "content": question}]
    rag_messages = build_rag_messages(question, [passwords_chunk, sign_up_chunk])
    log.debug("expected=%s got=%s", expected_messages, rag_messages)
    assert rag_messages == expected_messages


@debug
def make_fake_embed_post(sent_request_bodies: list[Any]) -> Any:
    """Build a stand-in for httpx.post that answers /api/embed with 3-number vectors, one per text.

    Args:
        sent_request_bodies: an empty list; each call's json= body is added to it.
    Returns:
        A function used like httpx.post.
    """
    @debug
    def fake_post(url: str, **options: Any) -> httpx.Response:
        """Save the body; answer with vectors [1, 0, 0], [2, 0, 0], ...

        Args:
            url: e.g. "http://127.0.0.1:11434/api/embed".
            options: json=..., timeout=...
        Returns:
            A 200 response holding {"embeddings": [...]}.
        """
        request_body = options["json"]
        sent_request_bodies.append(request_body)
        fake_vectors: list[list[float]] = []
        for text_number in range(len(request_body["input"])):
            fake_vectors.append([float(text_number + 1), 0.0, 0.0])
        fake_request = httpx.Request("POST", url)  # raise_for_status needs to know the request
        fake_response = httpx.Response(200, json={"embeddings": fake_vectors}, request=fake_request)
        log.debug("result: %d fake vectors", len(fake_vectors))
        return fake_response
    return fake_post


@debug
def test_embed_texts_sends_all_texts_in_one_call(monkeypatch: pytest.MonkeyPatch) -> None:
    """One POST for all texts, the right model, and a float matrix back.

    Why: one call for 122 chunks is much faster than 122 calls (2.5: batch 3x faster).

    Args:
        monkeypatch: pytest's tool to swap httpx.post for a fake.
    """
    sent_request_bodies: list[Any] = []
    monkeypatch.setattr(httpx, "post", make_fake_embed_post(sent_request_bodies))
    embedding_matrix = embed_texts(["first text", "second text"])
    log.debug("sent=%s shape=%s", sent_request_bodies, embedding_matrix.shape)
    assert sent_request_bodies == [{"model": EMBEDDING_MODEL, "input": ["first text", "second text"]}]
    assert embedding_matrix.shape == (2, 3)
    assert embedding_matrix.dtype == np.float64
    assert embedding_matrix[1, 0] == 2.0


@debug
def test_embed_texts_rejects_an_empty_list() -> None:
    """No texts -> ValueError before any HTTP call: a clear error, not a strange reply from Ollama."""
    log.debug("expected=ValueError for an empty list")
    with pytest.raises(ValueError):
        embed_texts([])


# ---------- Real Ollama ----------
class EmbeddedHandbook(NamedTuple):
    """The handbook cut into chunks, and one vector per chunk (same order)."""

    chunk_texts: list[str]  # e.g. 14 texts
    chunk_vectors: EmbeddingMatrix  # e.g. shape (14, 768)


@pytest.fixture(scope="module")
@debug
def embedded_handbook() -> EmbeddedHandbook:
    """Cut the handbook by headings and embed every chunk, once for all real tests in this file.

    Returns:
        e.g. EmbeddedHandbook(chunk_texts=[14 texts], chunk_vectors=<(14, 768) matrix>).
    """
    handbook_path = LESSON_FOLDER / "handbook_4_1.md"
    handbook_text = handbook_path.read_text(encoding="utf-8")
    chunk_texts = split_by_headings(handbook_text)
    chunk_vectors = embed_texts(chunk_texts)
    handbook = EmbeddedHandbook(chunk_texts=chunk_texts, chunk_vectors=chunk_vectors)
    log.debug("result: %d chunks, vectors %s", len(chunk_texts), chunk_vectors.shape)
    return handbook


@pytest.mark.ollama
@debug
def test_real_vectors_have_length_one(embedded_handbook: EmbeddedHandbook) -> None:
    """768 numbers per chunk and length 1.0: then a dot product is the cosine, as find_top_chunks assumes (2.5).

    Args:
        embedded_handbook: the embedded handbook.
    """
    chunk_vectors = embedded_handbook.chunk_vectors
    vector_lengths = np.linalg.norm(chunk_vectors, axis=1)  # one length per row
    log.debug("expected=768 columns, length 1.0 got=%s, lengths %.4f-%.4f", chunk_vectors.shape,
              vector_lengths.min(), vector_lengths.max())
    assert chunk_vectors.shape[1] == 768
    assert np.allclose(vector_lengths, 1.0, atol=0.001)


@pytest.mark.ollama
@debug
def test_real_search_finds_the_refund_section(embedded_handbook: EmbeddedHandbook) -> None:
    """A question in other words than the text ("money back") still finds "## Refunds" first.

    Why: that is the point of search by meaning; a word search would miss it.

    Args:
        embedded_handbook: the embedded handbook.
    """
    question_vectors = embed_texts(["Can I get my money back?"])
    question_vector = question_vectors[0]  # [0] = the only row
    top_rows = find_top_chunks(question_vector, embedded_handbook.chunk_vectors, 1)
    best_row = top_rows[0]
    best_chunk = embedded_handbook.chunk_texts[best_row]
    log.debug("expected='## Refunds...' got=%s", cut_text(best_chunk))
    assert best_chunk.startswith("## Refunds")


@pytest.mark.ollama
@debug
def test_real_answer_uses_the_handbook(embedded_handbook: EmbeddedHandbook) -> None:
    """The whole RAG chain: the model alone said "10 minutes"; with the found chunks, "15 minutes".

    Args:
        embedded_handbook: the embedded handbook.
    """
    question = "How long does the password reset link work?"
    answer_text = answer_question(question, embedded_handbook.chunk_texts, embedded_handbook.chunk_vectors, 3)
    cleaned_answer = answer_text.lower().replace("-", " ")  # "15-Minute" -> "15 minute", as part 3 checks
    expected_words = "15 minutes"
    log.debug("expected=%r got=%r", expected_words, cleaned_answer)
    assert expected_words in cleaned_answer
