"""Given helper for part 1: measure chunks. How many, how long, how many end badly.

A chunk "ends badly" when it stops mid-sentence ("...expires after 15 minu") or on a
heading whose text went to the next chunk ("...Nothing is deleted.\\n\\nRefunds").
"""

from dataclasses import dataclass

from lab_tools.log import debug, log

SENTENCE_END_MARKS = (".", "!", "?", '"', ")")  # a chunk ending on one of these ends a sentence


@dataclass
class ChunkStats:
    """What one way of cutting gave: how many chunks, how big, how many end badly."""

    chunk_count: int  # e.g. 16
    average_length: int  # characters, e.g. 381
    longest_length: int  # e.g. 488
    ends_mid_sentence: int  # e.g. 14: "...expires after 15 minu"
    ends_on_heading: int  # e.g. 10: "...Nothing is deleted.\n\nRefunds"


@debug
def measure_chunks(chunks: list[str], headings: list[str]) -> ChunkStats:
    """Count what makes a chunk bad: cut mid-sentence, or a heading cut off from its text.

    Args:
        chunks: e.g. cut_at_sentences(handbook, 500).
        headings: the document's headings, e.g. ["Refunds", "Sync", ...].
    Returns:
        e.g. ChunkStats(chunk_count=14, average_length=434, longest_length=486, ...).
    """
    log.debug("start: %d chunks", len(chunks))
    total_length = 0
    longest_length = 0
    ends_mid_sentence = 0
    ends_on_heading = 0
    for chunk in chunks:
        stripped_chunk = chunk.strip()
        total_length += len(stripped_chunk)
        longest_length = max(longest_length, len(stripped_chunk))
        if stripped_chunk.endswith(tuple(headings)):  # a tuple = any of these
            ends_on_heading += 1
        elif not stripped_chunk.endswith(SENTENCE_END_MARKS):
            ends_mid_sentence += 1
    chunk_stats = ChunkStats(len(chunks), total_length // len(chunks), longest_length, ends_mid_sentence,
                             ends_on_heading)
    log.debug("result: %s", chunk_stats)
    return chunk_stats
