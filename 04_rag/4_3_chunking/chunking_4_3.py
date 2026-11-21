"""Lesson 4.3 exercises: cut a document into chunks, 4 ways. YOU fill the 6 functions that raise NotImplementedError.

Goal: chunks that hold whole sentences and whole sections, so search (4.1) finds the
chunk with the full answer. No Ollama needed for any test here: chunk_by_meaning gets
the similarities as numbers, the examples compute them.
Fill the functions until every test in this folder passes:
  uv run pytest 04_rag/4_3_chunking -v
Start with exercises_4_3_1_pieces.py, then exercises_4_3_2_chunks.py.
The settings, is_heading and split_into_paragraphs are given; don't change them.
Style: docs/CODE_STYLE.md.
"""
# lesson-rules: user-code  (style problems here are shown as warnings, never block a commit)

import re  # pyright: ignore[reportUnusedImport]  (used once split_into_sentences is filled)

from lab_tools.log import cut_text, debug, log

MAX_CHUNK_CHARACTERS = 500  # LESSON section 5: at 500, paragraphs + headings found 12/12
HEADING_MAX_CHARACTERS = 60  # a heading is short: "Refunds", "Plans and prices"
SENTENCE_END_REGEX = r"(?<=[.!?])\s+"  # the spaces right after . ! or ? ((?<=...) = "after this")
RECURSIVE_SEPARATORS = ["\n\n", ". ", " "]  # paragraph, then sentence, then word; then characters


def is_heading(paragraph: str) -> bool:
    """Given: is this paragraph a heading? Short, and no end mark like a sentence has.

    No own log lines: runs once per paragraph; its callers log the totals.
    Args:
        paragraph: e.g. "Refunds" or "You can ask for a full refund within 14 days of a payment."
    Returns:
        e.g. True for "Refunds", False for the sentence.
    """
    stripped_paragraph = paragraph.strip()
    is_short = 0 < len(stripped_paragraph) <= HEADING_MAX_CHARACTERS
    has_end_mark = stripped_paragraph.endswith((".", "!", "?", ":"))  # a tuple = any of these
    is_heading_paragraph = is_short and not has_end_mark
    return is_heading_paragraph


@debug
def split_into_paragraphs(document_text: str) -> list[str]:
    """Given: cut a text at its empty lines; each paragraph is one line after 4.2 cleaning.

    Args:
        document_text: e.g. "Refunds\\n\\nYou can ask...\\n\\n\\nStorage".
    Returns:
        e.g. ["Refunds", "You can ask...", "Storage"]: spaces at both ends removed, empty ones dropped.
    """
    log.debug("start: %s", cut_text(document_text))
    paragraphs: list[str] = []
    for paragraph in document_text.split("\n\n"):
        stripped_paragraph = paragraph.strip()
        if stripped_paragraph != "":
            paragraphs.append(stripped_paragraph)
    log.debug("result: %d paragraphs", len(paragraphs))
    return paragraphs


@debug
def split_into_sentences(document_text: str) -> list[str]:
    """Cut a text into sentences, so no chunk has to start or end in the middle of one.

    How:
        1. Cut the text into paragraphs (split_into_paragraphs): a heading becomes its own piece.
        2. Cut each paragraph at SENTENCE_END_REGEX with re.split.
        3. Strip each sentence; drop empty ones.
    Args:
        document_text: e.g. "Refunds\\n\\nAsk within 14 days. After that, no refund."
    Returns:
        e.g. ["Refunds", "Ask within 14 days.", "After that, no refund."].
    """
    raise NotImplementedError("Lesson 4.3, exercise 1: split_into_sentences")


@debug
def pack_pieces(pieces: list[str], max_characters: int, joiner: str) -> list[str]:
    """Put pieces together, in order, into chunks of at most max_characters: few chunks, no piece cut.

    How:
        1. max_characters < 1 -> ValueError.
        2. Start with an empty chunk "".
        3. For each piece:
           - chunk is empty -> the piece becomes the chunk (no joiner in front).
           - chunk + joiner + piece fits (<= max_characters) -> that is the new chunk.
           - else -> close the chunk (add it to the list), start a new one with this piece.
           So a piece longer than max_characters becomes its own chunk (never cut here).
        4. After the loop, close the last chunk if it is not empty. No pieces -> [].
    Args:
        pieces: e.g. ["Ask within 14 days.", "After that, no refund."].
        max_characters: e.g. 30.
        joiner: what goes between two pieces in a chunk, e.g. " " or "\\n\\n".
    Returns:
        e.g. ["Ask within 14 days.", "After that, no refund."] (19 + 1 + 22 = 42 > 30).
    Raises:
        ValueError: max_characters is 0 or less.
    """
    raise NotImplementedError("Lesson 4.3, exercise 2: pack_pieces")


@debug
def chunk_by_sentences(document_text: str, max_characters: int) -> list[str]:
    """Cut a text into chunks of whole sentences.

    How:
        1. split_into_sentences.
        2. pack_pieces with joiner " ".
    Args:
        document_text: e.g. "A b. C d. E f."
        max_characters: e.g. 9.
    Returns:
        e.g. ["A b. C d.", "E f."].
    """
    raise NotImplementedError("Lesson 4.3, exercise 3: chunk_by_sentences")


@debug
def chunk_by_paragraphs(document_text: str, max_characters: int) -> list[str]:
    """Cut a text into chunks of whole paragraphs, each heading kept with the paragraph after it.

    How:
        1. split_into_paragraphs.
        2. A heading (is_heading) waits, and goes in front of the next paragraph,
           joined by "\\n\\n". Two headings in a row both wait. A heading at the very end
           (no paragraph after it) becomes its own piece; packing may still add it to the chunk before.
        3. pack_pieces with joiner "\\n\\n".
    Args:
        document_text: e.g. "Refunds\\n\\nAsk within 14 days.\\n\\nSync\\n\\nEvery 60 seconds."
        max_characters: e.g. 30.
    Returns:
        e.g. ["Refunds\\n\\nAsk within 14 days.", "Sync\\n\\nEvery 60 seconds."].
    """
    raise NotImplementedError("Lesson 4.3, exercise 4: chunk_by_paragraphs")


@debug
def chunk_recursively(document_text: str, max_characters: int, separators: list[str]) -> list[str]:
    """Cut at the biggest boundary that works: paragraphs, else sentences, else words, else characters.

    How:
        1. Empty text -> []. Text fits in max_characters -> [document_text].
        2. No separators left -> cut every max_characters characters.
        3. Split at separators[0]. Put the separator back at the end of every piece but the
           last, so no character is lost.
        4. A piece still too long -> chunk_recursively(piece, max_characters, separators[1:]).
        5. pack_pieces(all small pieces, max_characters, joiner "").
    Args:
        document_text: e.g. "Aa bb. Cc dd."
        max_characters: e.g. 8.
        separators: e.g. RECURSIVE_SEPARATORS.
    Returns:
        e.g. ["Aa bb. ", "Cc dd."]: "".join(chunks) gives back document_text exactly.
    """
    raise NotImplementedError("Lesson 4.3, exercise 5: chunk_recursively")


@debug
def chunk_by_meaning(sentences: list[str], neighbor_similarities: list[float], cut_below: float,
                     max_characters: int) -> list[str]:
    """Start a new chunk where the topic changes: where two sentences in a row are not alike.

    How:
        1. No sentences -> [] (check this first: then there are 0 similarities, too).
        2. len(neighbor_similarities) != len(sentences) - 1 -> ValueError.
        3. Start the first chunk with sentence 0.
        4. For sentence n (n >= 1): neighbor_similarities[n - 1] compares it with sentence n - 1.
           Below cut_below, or chunk + " " + sentence too long -> close the chunk, start a new one.
           Else add it with " ".
    Args:
        sentences: e.g. ["Ask within 14 days.", "No refund after.", "Sync runs every minute."].
        neighbor_similarities: one per pair in a row, e.g. [0.81, 0.42].
        cut_below: e.g. 0.5.
        max_characters: e.g. 500.
    Returns:
        e.g. ["Ask within 14 days. No refund after.", "Sync runs every minute."].
    Raises:
        ValueError: neighbor_similarities is not one shorter than sentences.
    """
    raise NotImplementedError("Lesson 4.3, exercise 6: chunk_by_meaning")
