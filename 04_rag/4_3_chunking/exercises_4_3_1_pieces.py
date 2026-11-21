"""Tests for chunking_4_3.py, part 1: sentences and packing. Small texts, no Ollama.

  uv run pytest 04_rag/4_3_chunking/exercises_4_3_1_pieces.py -v
"""

import pytest

from chunking_4_3 import chunk_by_sentences, pack_pieces, split_into_sentences
from lab_tools.log import debug, log

NO_TEXTS: list[str] = []  # a typed empty list, so pyright knows what the rows hold


@pytest.mark.parametrize(("document_text", "expected_sentences"), [
    # two sentences in one paragraph: cut after the "."
    ("Ask within 14 days. After that, no refund.", ["Ask within 14 days.", "After that, no refund."]),
    # a heading is its own piece, even with no end mark
    ("Refunds\n\nAsk within 14 days.", ["Refunds", "Ask within 14 days."]),
    # "?" and "!" end a sentence too
    ("Locked out? Wait 30 minutes! Then retry.", ["Locked out?", "Wait 30 minutes!", "Then retry."]),
    # a "." with no space after it is not an end: version 7.2, Settings > Profile.
    ("Sync needs version 7.2 or newer. Older ones stop.", ["Sync needs version 7.2 or newer.", "Older ones stop."]),
    # extra empty lines and spaces are dropped, nothing empty comes back
    ("\n\n  One.  \n\n\n\nTwo.\n\n", ["One.", "Two."]),
    # empty text: no sentences
    ("", NO_TEXTS),
])
@debug
def test_split_into_sentences_cuts_after_end_marks(document_text: str, expected_sentences: list[str]) -> None:
    """Sentences are the smallest piece we never cut, so where one ends must be right.

    Args:
        document_text: a small text.
        expected_sentences: the sentences that should come back.
    """
    got_sentences = split_into_sentences(document_text)
    log.debug("expected=%r got=%r", expected_sentences, got_sentences)
    assert got_sentences == expected_sentences


@pytest.mark.parametrize(("pieces", "max_characters", "joiner", "expected_chunks"), [
    # 19 + 1 + 22 = 42 > 30: two chunks
    (["Ask within 14 days.", "After that, no refund."], 30, " ", ["Ask within 14 days.", "After that, no refund."]),
    # 19 + 1 + 22 = 42 fits in 50: one chunk
    (["Ask within 14 days.", "After that, no refund."], 50, " ", ["Ask within 14 days. After that, no refund."]),
    # exactly max_characters fits: "aa bb" is 5
    (["aa", "bb", "cc"], 5, " ", ["aa bb", "cc"]),
    # the joiner counts toward the length: "aa\n\nbb" is 6 > 5
    (["aa", "bb"], 5, "\n\n", ["aa", "bb"]),
    # a piece longer than the max is never cut: it becomes its own chunk
    (["aa", "a much too long piece", "bb"], 5, " ", ["aa", "a much too long piece", "bb"]),
    # no pieces: no chunks
    (NO_TEXTS, 5, " ", NO_TEXTS),
])
@debug
def test_pack_pieces_fills_chunks_in_order(pieces: list[str], max_characters: int, joiner: str,
                                           expected_chunks: list[str]) -> None:
    """Packing decides chunk size for sentences AND paragraphs: full chunks, order kept, no piece cut.

    Args:
        pieces: sentences or paragraphs, in order.
        max_characters: the biggest chunk allowed.
        joiner: what goes between two pieces.
        expected_chunks: the chunks that should come back.
    """
    got_chunks = pack_pieces(pieces, max_characters, joiner)
    log.debug("expected=%r got=%r", expected_chunks, got_chunks)
    assert got_chunks == expected_chunks


@debug
def test_pack_pieces_rejects_a_max_below_one() -> None:
    """A max of 0 could never hold any text: say so loudly instead of giving odd chunks."""
    with pytest.raises(ValueError):
        pack_pieces(["aa"], 0, " ")
    log.debug("ValueError raised, as expected")


@pytest.mark.parametrize(("document_text", "max_characters", "expected_chunks"), [
    # 4 + 1 + 4 = 9 fits, the third sentence does not
    ("A b. C d. E f.", 9, ["A b. C d.", "E f."]),
    # a big max: everything in one chunk, joined by spaces
    ("Refunds\n\nAsk within 14 days.", 500, ["Refunds Ask within 14 days."]),
    # a small max: one sentence per chunk, none cut
    ("Ask within 14 days. After that, no refund.", 10, ["Ask within 14 days.", "After that, no refund."]),
])
@debug
def test_chunk_by_sentences_keeps_sentences_whole(document_text: str, max_characters: int,
                                                  expected_chunks: list[str]) -> None:
    """Chunks made of whole sentences: an answer sentence is never split over two chunks.

    Args:
        document_text: a small text.
        max_characters: the biggest chunk allowed.
        expected_chunks: the chunks that should come back.
    """
    got_chunks = chunk_by_sentences(document_text, max_characters)
    log.debug("expected=%r got=%r", expected_chunks, got_chunks)
    assert got_chunks == expected_chunks
