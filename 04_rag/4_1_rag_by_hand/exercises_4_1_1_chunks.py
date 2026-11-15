"""Tests for rag_4_1.py, part 1: cutting documents into chunks. No Ollama.

  uv run pytest 04_rag/4_1_rag_by_hand/exercises_4_1_1_chunks.py -v
"""

from pathlib import Path

import pytest

from lab_tools.log import debug, log
from rag_4_1 import HEADING_START, split_by_headings, split_by_size

HANDBOOK_PATH = Path(__file__).parent / "handbook_4_1.md"  # next to this file
HANDBOOK_SECTION_COUNT = 13  # "## " headings in handbook_4_1.md
HANDBOOK_CHUNK_SIZE = 500  # the size compared in the lesson (section 2)
HANDBOOK_OVERLAP = 100


@pytest.mark.parametrize(("document_text", "expected_chunks"), [
    # the basic case: one chunk per "## " section, heading included
    ("## Refunds\nWithin 14 days.\n## Sync\nEvery 60 s.", ["## Refunds\nWithin 14 days.", "## Sync\nEvery 60 s."]),
    # text before the first heading (the title) is a chunk too
    ("# Title\n\n## Refunds\nWithin 14 days.", ["# Title", "## Refunds\nWithin 14 days."]),
    # empty lines at the ends of a section are stripped
    ("## Refunds\n\nWithin 14 days.\n\n\n## Sync\nEvery 60 s.\n", ["## Refunds\n\nWithin 14 days.", "## Sync\nEvery 60 s."]),
    # a "### " sub-heading stays inside its section
    ("## Plans\nFree.\n### Plus\n6 euros.", ["## Plans\nFree.\n### Plus\n6 euros."]),
    # no heading at all: the whole text is one chunk
    ("Just one paragraph.", ["Just one paragraph."]),
    # nothing in, nothing out
    ("", []),
    # only empty lines and spaces: no empty chunk
    ("\n\n  \n", []),
])
@debug
def test_split_by_headings_gives_one_chunk_per_section(document_text: str, expected_chunks: list[str]) -> None:
    """One chunk per section, nothing lost, nothing empty: an empty chunk would waste a top-3 place.

    Args:
        document_text: a small Markdown text.
        expected_chunks: the chunks it should give.
    """
    chunks = split_by_headings(document_text)
    log.debug("expected=%r got=%r", expected_chunks, chunks)
    assert chunks == expected_chunks


@debug
def test_split_by_headings_keeps_every_handbook_section() -> None:
    """The real handbook gives the title + 13 sections, each starting with its heading.

    Why: the heading is often the best match for a question ("## Refunds").
    """
    handbook_text = HANDBOOK_PATH.read_text(encoding="utf-8")
    chunks = split_by_headings(handbook_text)
    expected_chunk_count = HANDBOOK_SECTION_COUNT + 1  # + 1 = the title chunk before the first heading
    log.debug("expected=%d got=%d", expected_chunk_count, len(chunks))
    assert len(chunks) == expected_chunk_count
    section_chunks = chunks[1:]  # all but the title
    for section_chunk in section_chunks:
        assert section_chunk.startswith(HEADING_START)


@pytest.mark.parametrize(("document_text", "chunk_size", "overlap", "expected_chunks"), [
    ("abcdefghij", 4, 1, ["abcd", "defg", "ghij"]),      # each piece repeats 1 character
    ("abcdefghij", 4, 0, ["abcd", "efgh", "ij"]),        # no overlap; the last piece is shorter
    ("abcdefghij", 5, 2, ["abcde", "defgh", "ghij"]),    # stops at the piece that reaches the end
    ("abc", 4, 1, ["abc"]),                              # shorter than one piece
    ("", 4, 1, []),                                      # nothing in, nothing out
])
@debug
def test_split_by_size_cuts_pieces_with_overlap(document_text: str, chunk_size: int, overlap: int,
                                               expected_chunks: list[str]) -> None:
    """Fixed-size pieces, each repeating the end of the one before, and no extra piece at the end.

    Why: the overlap keeps a sentence cut at a border whole in one of the two pieces.

    Args:
        document_text: the text to cut.
        chunk_size: characters per piece.
        overlap: characters shared with the piece before.
        expected_chunks: the pieces it should give.
    """
    chunks = split_by_size(document_text, chunk_size, overlap)
    log.debug("expected=%r got=%r", expected_chunks, chunks)
    assert chunks == expected_chunks


@pytest.mark.parametrize(("chunk_size", "overlap"), [
    (4, 4),    # overlap = size: start would never move (endless loop)
    (4, 5),    # overlap bigger than the piece
    (0, 0),    # empty pieces
    (4, -1),   # negative overlap
])
@debug
def test_split_by_size_rejects_bad_numbers(chunk_size: int, overlap: int) -> None:
    """Numbers that would loop forever or make no sense raise ValueError, instead of hanging.

    Args:
        chunk_size: characters per piece.
        overlap: characters shared with the piece before.
    """
    log.debug("expected=ValueError for chunk_size=%d overlap=%d", chunk_size, overlap)
    with pytest.raises(ValueError):
        split_by_size("abcdefghij", chunk_size, overlap)


@debug
def test_split_by_size_on_the_handbook_loses_nothing() -> None:
    """On the real handbook: no piece over 500 characters, and gluing the pieces back gives the handbook.

    Why: a lost character could be the one fact a question needs.
    """
    handbook_text = HANDBOOK_PATH.read_text(encoding="utf-8")
    chunks = split_by_size(handbook_text, chunk_size=HANDBOOK_CHUNK_SIZE, overlap=HANDBOOK_OVERLAP)
    rebuilt_text = chunks[0]
    for chunk in chunks[1:]:
        rebuilt_text = rebuilt_text + chunk[HANDBOOK_OVERLAP:]  # skip the characters already there
    log.debug("%d chunks; expected=%d got=%d characters", len(chunks), len(handbook_text), len(rebuilt_text))
    for chunk in chunks:
        assert len(chunk) <= HANDBOOK_CHUNK_SIZE
    assert rebuilt_text == handbook_text
