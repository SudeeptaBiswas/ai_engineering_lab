"""Given helper for lesson 4.4: the handbook cut into chunks, the 12 questions, and the embed call.

The text is the 4.3 handbook (the 4.2 clean PDF text). Each chunk is one section, or part
of one when the section is over 500 characters, and starts with its heading. So every
chunk knows its heading: Chroma stores it next to the text as metadata (LESSON section 1).
"""

from dataclasses import dataclass
from pathlib import Path

import httpx

from lab_tools.log import debug, log

HANDBOOK_PATH = Path(__file__).parent.parent / "4_3_chunking" / "handbook_4_3.txt"  # the 4.3 text, not copied
OLLAMA_URL = "http://127.0.0.1:11434"
EMBEDDING_MODEL = "nomic-embed-text"  # as in 4.1-4.3: 768 numbers per text
MAX_CHUNK_CHARACTERS = 500  # 4.3 section 5: 500 found 12/12
HEADING_MAX_CHARACTERS = 60  # a heading is short: "Refunds", "Plans and prices"


@dataclass
class HandbookChunk:
    """One piece of the handbook, with what Chroma stores next to it."""

    chunk_id: str  # unique name in the collection, e.g. "refunds-1"
    heading: str  # the section it comes from, e.g. "Refunds"
    position: int  # 0 for the first chunk of the handbook, 1 for the next, ...
    text: str  # heading + paragraphs, e.g. "Refunds\n\nYou can ask for a full refund within 14 days..."


@dataclass
class EvalQuestion:
    """A handbook question and the whole sentence that answers it (same 12 as 4.3)."""

    question: str  # e.g. "How long does the password reset link work?"
    answer_sentence: str  # e.g. "The reset link we send expires after 15 minutes and can be used only once"


EVAL_QUESTIONS = [  # copied from 4.3 part 2, so the scores compare
    EvalQuestion("How long does the password reset link work?",
                 "The reset link we send expires after 15 minutes and can be used only once"),
    EvalQuestion("My account got locked after wrong passwords. How long until I can try again?",
                 "After 5 wrong passwords in a row, the account is locked for 30 minutes"),
    EvalQuestion("How much does the Plus plan cost per year?", "6 euros per month or 60 euros per year"),
    EvalQuestion("I paid three weeks ago. Can I still get a refund?", "After 14 days we do not refund"),
    EvalQuestion("How long do deleted notes stay in the trash?", "Deleted notes stay in the Trash for 30 days"),
    EvalQuestion("What happens if I edit the same note on two devices while offline?",
                 'the second one is saved as a copy with "(conflict)" in its title'),
    EvalQuestion("How many requests per minute can one API key make?", "Each API key may make 600 requests per minute"),
    EvalQuestion("How long is the download link for a full account export valid?", "the link stays valid for 7 days"),
    EvalQuestion("What is the biggest attachment I can add?", "Each attachment can be at most 200 MB"),
    EvalQuestion("What happens when my payment fails three times?",
                 "After the third failed try, the account moves back to the Free plan"),
    EvalQuestion("I lost my phone and my backup codes. How do I get into my account?",
                 "support can turn two-step sign-in off, but only after an identity check"),
    EvalQuestion("How many members can a shared notebook have?",
                 "A shared notebook (Team only) can have at most 50 members"),
]


def is_heading(paragraph: str) -> bool:
    """Is this paragraph a heading? Short, and no end mark like a sentence has (4.3 rule).

    No own log lines: runs once per paragraph; load_handbook_chunks logs the total.
    Args:
        paragraph: e.g. "Refunds" or "You can ask for a full refund within 14 days of a payment."
    Returns:
        e.g. True for "Refunds", False for the sentence.
    """
    is_short = 0 < len(paragraph) <= HEADING_MAX_CHARACTERS
    has_end_mark = paragraph.endswith((".", "!", "?", ":"))  # a tuple = any of these
    is_heading_paragraph = is_short and not has_end_mark
    return is_heading_paragraph


@debug
def load_handbook_chunks() -> list[HandbookChunk]:
    """Cut the handbook so every chunk stays inside one section and starts with its heading.

    How:
        1. Cut the text at empty lines into paragraphs.
        2. A heading starts a new section; the paragraphs after it belong to it.
        3. Inside a section, add paragraphs to the chunk while heading + text <= 500.
        4. Name each chunk after its section: "refunds-0", "refunds-1", ...
    Returns:
        e.g. 18 chunks; HandbookChunk("refunds-0", "Refunds", 10, "Refunds\\n\\nYou can ask...").
    """
    handbook_text = HANDBOOK_PATH.read_text(encoding="utf-8")
    log.debug("start: %d characters", len(handbook_text))
    chunks: list[HandbookChunk] = []
    heading = ""
    chunk_text = ""
    number_in_section = 0
    for raw_paragraph in handbook_text.split("\n\n"):
        paragraph = raw_paragraph.strip()
        if paragraph == "":
            continue
        if is_heading(paragraph):
            if chunk_text != "":  # close the last chunk of the section before
                chunks.append(make_chunk(heading, number_in_section, len(chunks), chunk_text))
            heading = paragraph
            chunk_text = ""
            number_in_section = 0
            continue
        if chunk_text == "":  # first paragraph of a chunk: the heading goes in front
            longer_text = f"{heading}\n\n{paragraph}"
        else:
            longer_text = f"{chunk_text}\n\n{paragraph}"
        if len(longer_text) <= MAX_CHUNK_CHARACTERS or chunk_text == "":
            chunk_text = longer_text
        else:  # full: close it, start the next chunk of the same section
            chunks.append(make_chunk(heading, number_in_section, len(chunks), chunk_text))
            number_in_section += 1
            chunk_text = f"{heading}\n\n{paragraph}"
    if chunk_text != "":
        chunks.append(make_chunk(heading, number_in_section, len(chunks), chunk_text))
    log.debug("result: %d chunks", len(chunks))
    return chunks


def make_chunk(heading: str, number_in_section: int, position: int, chunk_text: str) -> HandbookChunk:
    """Build one HandbookChunk with an id made from its heading.

    No own log lines: runs once per chunk; load_handbook_chunks logs the total.
    Args:
        heading: e.g. "Plans and prices".
        number_in_section: 0 for the first chunk of that section, 1 for the next.
        position: where the chunk is in the handbook, e.g. 6.
        chunk_text: e.g. "Plans and prices\\n\\nThere are three plans..."
    Returns:
        e.g. HandbookChunk("plans-and-prices-0", "Plans and prices", 6, "Plans and prices\\n\\n...").
    """
    id_start = heading.lower().replace(" ", "-")  # "Plans and prices" -> "plans-and-prices"
    handbook_chunk = HandbookChunk(f"{id_start}-{number_in_section}", heading, position, chunk_text)
    return handbook_chunk


@debug
def embed_texts(texts: list[str]) -> list[list[float]]:
    """Turn texts into vectors in one call (2.5), as plain lists: the shape Chroma takes.

    Args:
        texts: e.g. 18 chunks, or 1 question.
    Returns:
        One list of 768 numbers per text, each of length 1.0.
    """
    log.debug("start: %d texts", len(texts))
    request_body = {"model": EMBEDDING_MODEL, "input": texts}
    response = httpx.post(f"{OLLAMA_URL}/api/embed", json=request_body, timeout=600.0)
    response.raise_for_status()
    vectors: list[list[float]] = response.json()["embeddings"]
    log.debug("result: %d vectors", len(vectors))
    return vectors
