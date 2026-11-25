"""Tests for chroma_store_4_4.py, part 1: distances, missing ids, store each chunk once. No Ollama.

  uv run pytest 04_rag/4_4_chroma/exercises_4_4_1_store.py -v
"""

from collections.abc import Iterator

import pytest
from chromadb import Collection

from chroma_store_4_4 import add_missing_chunks, distance_to_similarity, find_missing_ids
from fakes_4_4 import PLANS_CHUNK, REFUND_CHUNK, SYNC_CHUNK, TEST_CHUNKS, FakeEmbedder, make_empty_collection
from lab_tools.log import debug, log

NO_IDS: list[str] = []  # a typed empty value, so pyright knows what the row holds


@pytest.fixture
@debug
def empty_collection() -> Iterator[Collection]:
    """A new empty collection for each test, deleted after it (yield = "run the test here", 1.9).

    Returns:
        An empty in-memory collection, measured by cosine.
    """
    client, collection = make_empty_collection()
    yield collection
    client.delete_collection(collection.name)
    log.debug("result: %s deleted", collection.name)


@pytest.mark.parametrize(("distance", "distance_space", "expected_similarity"), [
    # cosine: distance 0 = same direction = similarity 1
    (0.0, "cosine", 1.0),
    # cosine: similarity = 1 - distance
    (0.29, "cosine", 0.71),
    # cosine: distance 1 = at a right angle = similarity 0 (nothing in common)
    (1.0, "cosine", 0.0),
    # l2 squared, vectors of length 1.0: distance = 2 - 2 * similarity
    (0.58, "l2", 0.71),
    # l2: distance 0 = the same vector
    (0.0, "l2", 1.0),
])
@debug
def test_distance_to_similarity_undoes_what_chroma_did(distance: float, distance_space: str,
                                                       expected_similarity: float) -> None:
    """Chroma reports a distance; we compare with the similarities of 2.5-4.3, so it must convert back.

    Args:
        distance: what Chroma returned.
        distance_space: how the collection measures.
        expected_similarity: the cosine similarity it stands for.
    """
    got_similarity = distance_to_similarity(distance, distance_space)
    log.debug("expected=%r got=%r", expected_similarity, got_similarity)
    assert got_similarity == pytest.approx(expected_similarity)  # approx: 1 - 0.29 is 0.71000000000001


@debug
def test_distance_to_similarity_rejects_an_unknown_space() -> None:
    """"ip" (inner product) is not handled: a silent wrong number would be worse than an error."""
    with pytest.raises(ValueError):
        distance_to_similarity(0.3, "ip")
    log.debug("ValueError raised, as expected")


@debug
def test_find_missing_ids_in_an_empty_collection_gives_all(empty_collection: Collection) -> None:
    """First run: nothing stored, so every id must come back, in order, or some chunk is never embedded.

    Args:
        empty_collection: the fixture above.
    """
    got_missing_ids = find_missing_ids(empty_collection, ["sync-0", "refunds-0"])
    log.debug("expected=['sync-0', 'refunds-0'] got=%r", got_missing_ids)
    assert got_missing_ids == ["sync-0", "refunds-0"]


@debug
def test_find_missing_ids_skips_the_stored_ones(empty_collection: Collection) -> None:
    """Only the ids Chroma does not hold come back, so only they get embedded.

    Args:
        empty_collection: the fixture above.
    """
    empty_collection.add(ids=["refunds-0"], embeddings=[[1.0, 0.0, 0.0]], documents=["Refunds"])
    got_missing_ids = find_missing_ids(empty_collection, ["refunds-0", "sync-0", "plans-0"])
    log.debug("expected=['sync-0', 'plans-0'] got=%r", got_missing_ids)
    assert got_missing_ids == ["sync-0", "plans-0"]


@debug
def test_find_missing_ids_with_all_stored_gives_none(empty_collection: Collection) -> None:
    """All stored: an empty list, so a re-run costs no embed call at all.

    Args:
        empty_collection: the fixture above.
    """
    empty_collection.add(ids=["refunds-0"], embeddings=[[1.0, 0.0, 0.0]], documents=["Refunds"])
    got_missing_ids = find_missing_ids(empty_collection, ["refunds-0"])
    log.debug("expected=[] got=%r", got_missing_ids)
    assert got_missing_ids == NO_IDS


@debug
def test_add_missing_chunks_stores_all_with_one_embed_call(empty_collection: Collection) -> None:
    """First run: all 3 chunks stored, embedded in ONE call (one request to Ollama, not 3).

    Args:
        empty_collection: the fixture above.
    """
    fake_embedder = FakeEmbedder()
    added_count = add_missing_chunks(empty_collection, TEST_CHUNKS, fake_embedder)
    log.debug("expected=3 added, 1 call, 3 stored got=%d, %d, %d", added_count, len(fake_embedder.calls),
              empty_collection.count())
    assert added_count == 3
    assert len(fake_embedder.calls) == 1
    assert empty_collection.count() == 3


@debug
def test_add_missing_chunks_twice_embeds_nothing_the_second_time(empty_collection: Collection) -> None:
    """Second run: everything is stored already, so no embed call at all. This is the time we save.

    Args:
        empty_collection: the fixture above.
    """
    add_missing_chunks(empty_collection, TEST_CHUNKS, FakeEmbedder())
    second_embedder = FakeEmbedder()
    added_count = add_missing_chunks(empty_collection, TEST_CHUNKS, second_embedder)
    log.debug("expected=0 added, 0 calls got=%d, %d", added_count, len(second_embedder.calls))
    assert added_count == 0
    assert second_embedder.calls == []


@debug
def test_add_missing_chunks_embeds_only_the_new_chunk(empty_collection: Collection) -> None:
    """A new section was written: only its chunk is embedded, the 2 old ones are not sent again.

    Args:
        empty_collection: the fixture above.
    """
    add_missing_chunks(empty_collection, [REFUND_CHUNK, SYNC_CHUNK], FakeEmbedder())
    fake_embedder = FakeEmbedder()
    added_count = add_missing_chunks(empty_collection, TEST_CHUNKS, fake_embedder)
    expected_calls = [[PLANS_CHUNK.text]]  # one call, with the plans text only
    log.debug("expected=1 added, calls %r got=%d, %r", expected_calls, added_count, fake_embedder.calls)
    assert added_count == 1
    assert fake_embedder.calls == expected_calls


@debug
def test_add_missing_chunks_keeps_text_and_heading(empty_collection: Collection) -> None:
    """Search returns what we stored: the text to show and the heading to filter by and cite (4.10).

    Args:
        empty_collection: the fixture above.
    """
    add_missing_chunks(empty_collection, TEST_CHUNKS, FakeEmbedder())
    stored_rows = empty_collection.get(ids=["sync-0"], include=["documents", "metadatas"])
    expected_metadatas = [{"heading": "Sync", "position": 1}]
    log.debug("expected=%r %r got=%r %r", [SYNC_CHUNK.text], expected_metadatas, stored_rows["documents"],
              stored_rows["metadatas"])
    assert stored_rows["documents"] == [SYNC_CHUNK.text]
    assert stored_rows["metadatas"] == expected_metadatas
