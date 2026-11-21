"""Tests for chunking_4_3.py, part 2: paragraphs, recursive, by meaning, the real handbook. No Ollama.

  uv run pytest 04_rag/4_3_chunking/exercises_4_3_2_chunks.py -v
"""

from pathlib import Path

import pytest

from chunking_4_3 import (MAX_CHUNK_CHARACTERS, RECURSIVE_SEPARATORS, chunk_by_meaning, chunk_by_paragraphs,
                          chunk_by_sentences, chunk_recursively, is_heading, split_into_paragraphs,
                          split_into_sentences)
from lab_tools.log import debug, log

HANDBOOK_PATH = Path(__file__).parent / "handbook_4_3.txt"  # the 4.2 clean handbook text
NO_TEXTS: list[str] = []  # typed empty values, so pyright knows what the rows hold
NO_SIMILARITIES: list[float] = []


@pytest.fixture(scope="module")
@debug
def handbook_text() -> str:
    """Read the handbook once for all tests in this file (a "module" fixture, 1.9).

    Returns:
        The clean handbook text, e.g. 6 131 characters.
    """
    document_text = HANDBOOK_PATH.read_text(encoding="utf-8")
    log.debug("result: %d characters", len(document_text))
    return document_text


@pytest.mark.parametrize(("document_text", "max_characters", "expected_chunks"), [
    # each heading goes in front of its paragraph; 28 + 2 + 23 > 30, so two chunks
    ("Refunds\n\nAsk within 14 days.\n\nSync\n\nEvery 60 seconds.", 30,
     ["Refunds\n\nAsk within 14 days.", "Sync\n\nEvery 60 seconds."]),
    # a big max: both sections in one chunk, joined by an empty line
    ("Refunds\n\nAsk within 14 days.\n\nSync\n\nEvery 60 seconds.", 500,
     ["Refunds\n\nAsk within 14 days.\n\nSync\n\nEvery 60 seconds."]),
    # two headings in a row both wait for the next paragraph
    ("Billing\n\nRefunds\n\nAsk within 14 days.", 500, ["Billing\n\nRefunds\n\nAsk within 14 days."]),
    # a heading at the very end has no paragraph after it: it stays alone
    ("Ask within 14 days.\n\nSync", 10, ["Ask within 14 days.", "Sync"]),
    # empty text: no chunks
    ("", 500, NO_TEXTS),
])
@debug
def test_chunk_by_paragraphs_keeps_heading_with_its_paragraph(document_text: str, max_characters: int,
                                                              expected_chunks: list[str]) -> None:
    """A heading alone at the end of a chunk is noise there and missing where its section is.

    Args:
        document_text: a small text with headings.
        max_characters: the biggest chunk allowed.
        expected_chunks: the chunks that should come back.
    """
    got_chunks = chunk_by_paragraphs(document_text, max_characters)
    log.debug("expected=%r got=%r", expected_chunks, got_chunks)
    assert got_chunks == expected_chunks


@pytest.mark.parametrize(("document_text", "max_characters", "expected_chunks"), [
    # fits already: one chunk, unchanged
    ("Aa bb. Cc dd.", 50, ["Aa bb. Cc dd."]),
    # too long, no "\n\n": cut at ". ", the ". " stays with the first piece
    ("Aa bb. Cc dd.", 8, ["Aa bb. ", "Cc dd."]),
    # paragraphs first: each paragraph fits, they don't fit together
    ("Aa bb.\n\nCc dd.", 8, ["Aa bb.\n\n", "Cc dd."]),
    # a sentence too long: cut at spaces, then pack the words
    ("aa bb cc dd", 6, ["aa bb ", "cc dd"]),
    # one long word, no separator left: cut every 4 characters
    ("abcdefghij", 4, ["abcd", "efgh", "ij"]),
    # empty text: no chunks
    ("", 8, NO_TEXTS),
])
@debug
def test_chunk_recursively_uses_the_biggest_boundary_that_fits(document_text: str, max_characters: int,
                                                               expected_chunks: list[str]) -> None:
    """Paragraph before sentence before word: the bigger the boundary, the more meaning stays together.

    Args:
        document_text: a small text.
        max_characters: the biggest chunk allowed.
        expected_chunks: the chunks that should come back.
    """
    got_chunks = chunk_recursively(document_text, max_characters, RECURSIVE_SEPARATORS)
    log.debug("expected=%r got=%r", expected_chunks, got_chunks)
    assert got_chunks == expected_chunks


@pytest.mark.parametrize(("neighbor_similarities", "cut_below", "max_characters", "expected_chunks"), [
    # 0.42 < 0.5: the topic changes before the third sentence
    ([0.81, 0.42], 0.5, 500, ["Ask within 14 days. No refund after.", "Sync runs every minute."]),
    # all alike: one chunk
    ([0.81, 0.77], 0.5, 500, ["Ask within 14 days. No refund after. Sync runs every minute."]),
    # exactly cut_below is NOT below: no cut
    ([0.5, 0.5], 0.5, 500, ["Ask within 14 days. No refund after. Sync runs every minute."]),
    # all alike, but the max is reached: cut by size ("Ask within 14 days. No refund after." is 36)
    ([0.81, 0.77], 0.5, 36, ["Ask within 14 days. No refund after.", "Sync runs every minute."]),
])
@debug
def test_chunk_by_meaning_cuts_where_the_topic_changes(neighbor_similarities: list[float], cut_below: float,
                                                       max_characters: int, expected_chunks: list[str]) -> None:
    """A low similarity between two sentences in a row = a new topic = a new chunk.

    Args:
        neighbor_similarities: one per pair of sentences in a row.
        cut_below: below this, start a new chunk.
        max_characters: the biggest chunk allowed.
        expected_chunks: the chunks that should come back.
    """
    sentences = ["Ask within 14 days.", "No refund after.", "Sync runs every minute."]
    got_chunks = chunk_by_meaning(sentences, neighbor_similarities, cut_below, max_characters)
    log.debug("expected=%r got=%r", expected_chunks, got_chunks)
    assert got_chunks == expected_chunks


@debug
def test_chunk_by_meaning_with_no_sentences_gives_no_chunks() -> None:
    """An empty page gives no sentences: that must be no chunks, not a crash."""
    got_chunks = chunk_by_meaning(NO_TEXTS, NO_SIMILARITIES, 0.5, 500)
    log.debug("expected=[] got=%r", got_chunks)
    assert got_chunks == NO_TEXTS


@debug
def test_chunk_by_meaning_rejects_the_wrong_number_of_similarities() -> None:
    """3 sentences have 2 pairs in a row; 3 similarities means they don't belong together."""
    with pytest.raises(ValueError):
        chunk_by_meaning(["A.", "B.", "C."], [0.9, 0.8, 0.7], 0.5, 500)
    log.debug("ValueError raised, as expected")


@debug
def test_handbook_by_paragraphs_has_no_heading_alone_at_a_chunk_end(handbook_text: str) -> None:
    """On the real handbook, 14 headings: each one must start a chunk's section, never end a chunk.

    Args:
        handbook_text: the fixture above.
    """
    chunks = chunk_by_paragraphs(handbook_text, MAX_CHUNK_CHARACTERS)
    ends_on_heading_count = 0
    for chunk in chunks:
        last_paragraph = split_into_paragraphs(chunk)[-1]  # [-1] = the last one
        if is_heading(last_paragraph):
            ends_on_heading_count += 1
    log.debug("expected=16 chunks, 0 end on a heading got=%d chunks, %d", len(chunks), ends_on_heading_count)
    assert len(chunks) == 16
    assert ends_on_heading_count == 0


@debug
def test_handbook_by_sentences_keeps_all_93_sentences_whole(handbook_text: str) -> None:
    """Every sentence of the handbook is found whole inside one chunk: nothing cut, nothing lost.

    Args:
        handbook_text: the fixture above.
    """
    sentences = split_into_sentences(handbook_text)
    chunks = chunk_by_sentences(handbook_text, MAX_CHUNK_CHARACTERS)
    missing_sentences: list[str] = []
    for sentence in sentences:
        is_in_a_chunk = False
        for chunk in chunks:
            if sentence in chunk:
                is_in_a_chunk = True
        if not is_in_a_chunk:
            missing_sentences.append(sentence)
    log.debug("expected=93 sentences, 0 missing got=%d, %r", len(sentences), missing_sentences)
    assert len(sentences) == 93
    assert missing_sentences == NO_TEXTS


@debug
def test_handbook_recursively_loses_nothing_and_stays_small(handbook_text: str) -> None:
    """Joined back, the chunks are the handbook exactly, and none is over the max.

    Args:
        handbook_text: the fixture above.
    """
    chunks = chunk_recursively(handbook_text, MAX_CHUNK_CHARACTERS, RECURSIVE_SEPARATORS)
    longest_chunk_length = 0
    for chunk in chunks:
        longest_chunk_length = max(longest_chunk_length, len(chunk))
    joined_text = "".join(chunks)
    log.debug("expected=<= %d got=%d chunks, longest %d", MAX_CHUNK_CHARACTERS, len(chunks), longest_chunk_length)
    assert joined_text == handbook_text
    assert longest_chunk_length <= MAX_CHUNK_CHARACTERS
