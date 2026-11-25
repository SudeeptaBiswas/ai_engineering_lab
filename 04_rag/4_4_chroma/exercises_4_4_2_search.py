"""Tests for chroma_store_4_4.py, part 2: search, filter by heading, replace a chunk, the real handbook.

  uv run pytest 04_rag/4_4_chroma/exercises_4_4_2_search.py -v     (Ollama off? add -m "not ollama")
"""

from collections.abc import Iterator

import pytest
from chromadb import Collection

from chroma_store_4_4 import add_missing_chunks, replace_chunk_text, search_chunks
from fakes_4_4 import SYNC_CHUNK, SYNC_VECTOR, TEST_CHUNKS, FakeEmbedder, make_empty_collection
from handbook_4_4 import EVAL_QUESTIONS, embed_texts, load_handbook_chunks
from lab_tools.log import debug, log

REFUND_AND_SYNC_QUESTION_VECTOR = [0.9, 0.436, 0.0]  # mostly refund, a bit sync; 0.81 + 0.19 = 1, so length 1.0
TOP_K = 3


@pytest.fixture
@debug
def stored_collection() -> Iterator[Collection]:
    """A collection holding the 3 TEST_CHUNKS, deleted after the test.

    Returns:
        A collection with refunds-0, sync-0, plans-0.
    """
    client, collection = make_empty_collection()
    add_missing_chunks(collection, TEST_CHUNKS, FakeEmbedder())
    yield collection
    client.delete_collection(collection.name)
    log.debug("result: %s deleted", collection.name)


@debug
def test_search_chunks_puts_the_closest_first(stored_collection: Collection) -> None:
    """Best first, with the similarity we know from 2.5: refunds 0.9, sync 0.436, plans 0.

    Args:
        stored_collection: the fixture above.
    """
    search_hits = search_chunks(stored_collection, REFUND_AND_SYNC_QUESTION_VECTOR, TOP_K, None)
    got_ids: list[str] = []
    got_similarities: list[float] = []
    for search_hit in search_hits:
        got_ids.append(search_hit.chunk_id)
        got_similarities.append(search_hit.similarity)
    log.debug("expected=['refunds-0', 'sync-0', 'plans-0'] [0.9, 0.436, 0.0] got=%r %r", got_ids, got_similarities)
    assert got_ids == ["refunds-0", "sync-0", "plans-0"]
    assert got_similarities == pytest.approx([0.9, 0.436, 0.0], abs=1e-4)  # Chroma keeps float32: ~7 digits


@debug
def test_search_chunks_returns_text_and_heading(stored_collection: Collection) -> None:
    """A hit carries what the prompt needs (the text) and what a citation needs (the heading).

    Args:
        stored_collection: the fixture above.
    """
    best_hit = search_chunks(stored_collection, SYNC_VECTOR, 1, None)[0]
    log.debug("expected=sync-0 'Sync' %r got=%s %r %r", SYNC_CHUNK.text, best_hit.chunk_id, best_hit.heading,
              best_hit.chunk_text)
    assert best_hit.chunk_id == "sync-0"
    assert best_hit.heading == "Sync"
    assert best_hit.chunk_text == SYNC_CHUNK.text


@debug
def test_search_chunks_gives_at_most_top_k(stored_collection: Collection) -> None:
    """3 chunks stored, top_k 2: only 2 come back, so the prompt stays small.

    Args:
        stored_collection: the fixture above.
    """
    search_hits = search_chunks(stored_collection, REFUND_AND_SYNC_QUESTION_VECTOR, 2, None)
    log.debug("expected=2 got=%d", len(search_hits))
    assert len(search_hits) == 2


@debug
def test_search_chunks_with_heading_filter_stays_in_that_section(stored_collection: Collection) -> None:
    """Filter "Sync": the refund chunk is closer, but it is not in that section, so it must not come back.

    Args:
        stored_collection: the fixture above.
    """
    search_hits = search_chunks(stored_collection, REFUND_AND_SYNC_QUESTION_VECTOR, TOP_K, "Sync")
    got_ids: list[str] = []
    for search_hit in search_hits:
        got_ids.append(search_hit.chunk_id)
    log.debug("expected=['sync-0'] got=%r", got_ids)
    assert got_ids == ["sync-0"]


@debug
def test_search_chunks_with_unknown_heading_finds_nothing(stored_collection: Collection) -> None:
    """No section with that heading: an empty list, not a crash.

    Args:
        stored_collection: the fixture above.
    """
    search_hits = search_chunks(stored_collection, REFUND_AND_SYNC_QUESTION_VECTOR, TOP_K, "Billing")
    log.debug("expected=[] got=%r", search_hits)
    assert search_hits == []


@debug
def test_replace_chunk_text_changes_text_and_vector_but_keeps_heading(stored_collection: Collection) -> None:
    """New text needs a new vector too, or search keeps finding the chunk by its old meaning.

    Args:
        stored_collection: the fixture above.
    """
    new_text = "Sync\n\nNow every 30 seconds."  # the fake embedder gives SYNC_VECTOR, not REFUND_VECTOR
    replace_chunk_text(stored_collection, "refunds-0", new_text, FakeEmbedder())
    stored_rows = stored_collection.get(ids=["refunds-0"], include=["documents", "metadatas"])
    search_hits = search_chunks(stored_collection, SYNC_VECTOR, 2, None)
    got_ids: list[str] = []
    for search_hit in search_hits:
        got_ids.append(search_hit.chunk_id)
    log.debug("expected=%r, heading Refunds, both sync-like got=%r %r %r", new_text, stored_rows["documents"],
              stored_rows["metadatas"], got_ids)
    assert stored_rows["documents"] == [new_text]
    assert stored_rows["metadatas"] == [{"heading": "Refunds", "position": 0}]
    assert sorted(got_ids) == ["refunds-0", "sync-0"]  # both now have SYNC_VECTOR


@debug
def test_replace_chunk_text_with_unknown_id_raises_and_embeds_nothing(stored_collection: Collection) -> None:
    """Chroma's update ignores an unknown id silently; ours must say so, before paying for an embed.

    Args:
        stored_collection: the fixture above.
    """
    fake_embedder = FakeEmbedder()
    with pytest.raises(KeyError):
        replace_chunk_text(stored_collection, "billing-0", "Billing\n\nNew text.", fake_embedder)
    log.debug("expected=KeyError, 0 calls got=KeyError, %d", len(fake_embedder.calls))
    assert fake_embedder.calls == []
    assert stored_collection.count() == 3


@pytest.mark.ollama
@debug
def test_handbook_in_chroma_finds_the_answer_first_for_12_of_12() -> None:
    """Real handbook, real nomic vectors, stored and searched by Chroma: the best chunk holds the answer 12/12."""
    client, collection = make_empty_collection()
    add_missing_chunks(collection, load_handbook_chunks(), embed_texts)
    question_texts: list[str] = []
    for eval_question in EVAL_QUESTIONS:
        question_texts.append(eval_question.question)
    question_vectors = embed_texts(question_texts)
    right_first = 0
    for question_number in range(len(EVAL_QUESTIONS)):
        best_hit = search_chunks(collection, question_vectors[question_number], 1, None)[0]
        answer_sentence = EVAL_QUESTIONS[question_number].answer_sentence
        if answer_sentence in best_hit.chunk_text:
            right_first += 1
    client.delete_collection(collection.name)
    log.debug("expected=12 got=%d", right_first)
    assert right_first == 12
