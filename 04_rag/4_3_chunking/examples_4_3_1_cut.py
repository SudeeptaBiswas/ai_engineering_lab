"""Part 1 of 3: cut the handbook 4 ways and look at the chunks. No Ollama.

Run (~1 s):
  uv run python 04_rag/4_3_chunking/examples_4_3_1_cut.py

  1. count : per way, how many chunks, how long, how many end mid-sentence or on a heading
  2. look  : where the "Refunds" section lands, cut by characters vs by paragraphs
"""

import re
from pathlib import Path

from chunk_stats_4_3 import measure_chunks
from lab_tools.log import cut_text, debug, log

HANDBOOK_PATH = Path(__file__).parent / "handbook_4_3.txt"  # the 4.2 clean handbook, pages joined
MAX_CHARACTERS = 500  # the 4.1 / 4.2 chunk size
OVERLAP_CHARACTERS = 100  # 4.1: each piece repeats the end of the one before
HEADING_MAX_CHARACTERS = 60
SENTENCE_END_REGEX = r"(?<=[.!?])\s+"  # the spaces right after . ! or ?
SEPARATORS_BIGGEST_FIRST = ["\n\n", ". ", " "]  # paragraph, sentence, word


@debug
def cut_every_n_characters(document_text: str, chunk_size: int, overlap: int) -> list[str]:
    """Cut by size only, as in 4.1: blind to words, sentences and headings.

    Args:
        document_text: e.g. the handbook.
        chunk_size: e.g. 500.
        overlap: e.g. 100; 0 = no overlap.
    Returns:
        e.g. 16 pieces of up to 500 characters.
    """
    log.debug("start: %d characters, size %d, overlap %d", len(document_text), chunk_size, overlap)
    chunks: list[str] = []
    start = 0
    while start < len(document_text):
        end = start + chunk_size
        chunks.append(document_text[start:end])
        if end >= len(document_text):  # this piece reached the end
            break
        start = end - overlap
    log.debug("result: %d chunks", len(chunks))
    return chunks


@debug
def fill_chunks(pieces: list[str], max_characters: int, joiner: str) -> list[str]:
    """Add whole pieces to a chunk while it fits; then start the next chunk.

    Args:
        pieces: sentences or paragraphs, in order.
        max_characters: e.g. 500.
        joiner: e.g. " " between sentences, "\\n\\n" between paragraphs.
    Returns:
        e.g. 14 chunks; a piece longer than the max is its own chunk.
    """
    log.debug("start: %d pieces", len(pieces))
    chunks: list[str] = []
    current_chunk = ""
    for piece in pieces:
        joined_chunk = current_chunk + joiner + piece
        if current_chunk == "":
            current_chunk = piece
        elif len(joined_chunk) <= max_characters:
            current_chunk = joined_chunk
        else:
            chunks.append(current_chunk)
            current_chunk = piece
    if current_chunk != "":
        chunks.append(current_chunk)
    log.debug("result: %d chunks", len(chunks))
    return chunks


@debug
def find_paragraphs(document_text: str) -> list[str]:
    """Paragraphs = text between empty lines (4.2 made each one a single line).

    Args:
        document_text: e.g. the handbook.
    Returns:
        e.g. 38 paragraphs, 14 of them headings.
    """
    log.debug("start: %s", cut_text(document_text))
    paragraphs: list[str] = []
    for paragraph in document_text.split("\n\n"):
        if paragraph.strip() != "":
            paragraphs.append(paragraph.strip())
    log.debug("result: %d paragraphs", len(paragraphs))
    return paragraphs


def looks_like_heading(paragraph: str) -> bool:
    """A heading is short and has no end mark: "Refunds", "Plans and prices".

    No own log lines: runs once per paragraph; its callers log the totals.
    Args:
        paragraph: e.g. "Refunds".
    Returns:
        e.g. True.
    """
    stripped_paragraph = paragraph.strip()
    is_short = 0 < len(stripped_paragraph) <= HEADING_MAX_CHARACTERS
    has_end_mark = stripped_paragraph.endswith((".", "!", "?", ":"))
    return is_short and not has_end_mark


@debug
def cut_at_sentences(document_text: str, max_characters: int) -> list[str]:
    """Cut only between sentences: no sentence is ever split.

    Args:
        document_text: e.g. the handbook.
        max_characters: e.g. 500.
    Returns:
        e.g. 14 chunks.
    """
    log.debug("start: max %d", max_characters)
    sentences: list[str] = []
    for paragraph in find_paragraphs(document_text):
        sentences.extend(re.split(SENTENCE_END_REGEX, paragraph))
    chunks = fill_chunks(sentences, max_characters, " ")
    log.debug("result: %d sentences -> %d chunks", len(sentences), len(chunks))
    return chunks


@debug
def cut_at_paragraphs(document_text: str, max_characters: int, keep_heading_with_text: bool) -> list[str]:
    """Cut only between paragraphs; optionally glue each heading to the paragraph after it.

    Args:
        document_text: e.g. the handbook.
        max_characters: e.g. 500.
        keep_heading_with_text: True = "Refunds" goes in front of its paragraph.
    Returns:
        e.g. 16 chunks.
    """
    log.debug("start: max %d, keep_heading_with_text=%s", max_characters, keep_heading_with_text)
    sections: list[str] = []
    waiting_heading = ""
    for paragraph in find_paragraphs(document_text):
        if keep_heading_with_text and looks_like_heading(paragraph):
            waiting_heading = (waiting_heading + "\n\n" + paragraph).strip()  # strip: no "\n\n" in front of the first
            continue
        if waiting_heading != "":
            paragraph = waiting_heading + "\n\n" + paragraph
            waiting_heading = ""
        sections.append(paragraph)
    if waiting_heading != "":  # a heading at the very end
        sections.append(waiting_heading)
    chunks = fill_chunks(sections, max_characters, "\n\n")
    log.debug("result: %d chunks", len(chunks))
    return chunks


@debug
def cut_at_biggest_boundary(document_text: str, max_characters: int, separators: list[str]) -> list[str]:
    """Recursive: cut at paragraphs; a piece still too big is cut at sentences, then words, then characters.

    Args:
        document_text: e.g. the handbook.
        max_characters: e.g. 500.
        separators: e.g. SEPARATORS_BIGGEST_FIRST; each call uses the first and passes on the rest.
    Returns:
        e.g. 16 chunks; "".join(chunks) == document_text.
    """
    log.debug("start: %d characters, separators=%r", len(document_text), separators)
    if len(document_text) <= max_characters:
        log.debug("result: fits, 1 chunk")
        return [document_text]
    if len(separators) == 0:  # nothing left to cut at: cut by size
        size_chunks = cut_every_n_characters(document_text, max_characters, 0)
        log.debug("result: no separator left, %d chunks by size", len(size_chunks))
        return size_chunks
    separator = separators[0]
    pieces = document_text.split(separator)
    small_pieces: list[str] = []
    for piece_number in range(len(pieces)):
        piece = pieces[piece_number]
        if piece_number < len(pieces) - 1:  # put the separator back: no character lost
            piece = piece + separator
        if len(piece) <= max_characters:
            small_pieces.append(piece)
        else:
            small_pieces.extend(cut_at_biggest_boundary(piece, max_characters, separators[1:]))
    chunks = fill_chunks(small_pieces, max_characters, "")
    log.debug("result: %d chunks", len(chunks))
    return chunks


if __name__ == "__main__":
    handbook_text = HANDBOOK_PATH.read_text(encoding="utf-8")
    ways_to_cut = {
        "characters 500, overlap 100": cut_every_n_characters(handbook_text, MAX_CHARACTERS, OVERLAP_CHARACTERS),
        "sentences": cut_at_sentences(handbook_text, MAX_CHARACTERS),
        "paragraphs": cut_at_paragraphs(handbook_text, MAX_CHARACTERS, False),
        "paragraphs + headings": cut_at_paragraphs(handbook_text, MAX_CHARACTERS, True),
        "recursive": cut_at_biggest_boundary(handbook_text, MAX_CHARACTERS, SEPARATORS_BIGGEST_FIRST),
    }
    handbook_headings: list[str] = []
    for handbook_paragraph in find_paragraphs(handbook_text):
        if looks_like_heading(handbook_paragraph):
            handbook_headings.append(handbook_paragraph)
    print(f"1. the handbook ({len(handbook_text)} characters), max {MAX_CHARACTERS} per chunk:")
    for way_name in ways_to_cut:
        stats = measure_chunks(ways_to_cut[way_name], handbook_headings)
        print(f"   {way_name:28} {stats.chunk_count:2} chunks, average {stats.average_length}, "
              f"longest {stats.longest_length}, end mid-sentence {stats.ends_mid_sentence:2}, "
              f"end on a heading {stats.ends_on_heading:2}")

    print('\n2. the first chunk with the heading "Refunds", around the heading ([ = chunk start, ] = end):')
    for way_name in ("characters 500, overlap 100", "paragraphs", "paragraphs + headings"):
        for chunk in ways_to_cut[way_name]:
            shown_part = "[" + chunk + "]"  # mark both ends of the chunk
            heading_match = re.search(r"Refunds(\n|\])", shown_part)  # the heading: a line break or "]" next
            if heading_match is not None:
                shown_start = max(0, heading_match.start() - 30)  # 30 characters before the heading, if there are
                print(f"   {way_name:28} ...{ascii(shown_part[shown_start:shown_start + 70])}...")
                break
