"""Lesson 4.2 exercises: PDF -> clean text. YOU fill the 7 functions that raise NotImplementedError.

Goal: read a PDF and give back clean text per page, so search (4.1) and exact-word
search (4.7) find what is really there. No Ollama needed for any test here.
Fill the functions until every test in this folder passes:
  uv run pytest 04_rag/4_2_pdf_loading -v
Start with exercises_4_2_1_text.py (small texts), then exercises_4_2_2_pdf.py (the real PDF).
The settings, CleanPage and line_pattern are given; don't change them. Style: docs/CODE_STYLE.md.
"""
# lesson-rules: user-code  (style problems here are shown as warnings, never block a commit)

import re
import unicodedata  # pyright: ignore[reportUnusedImport] — until fix_characters uses it
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader  # pyright: ignore[reportUnusedImport] — until read_pdf_pages uses it

from lab_tools.log import cut_text, debug, log  # pyright: ignore[reportUnusedImport] — until your code logs

PDF_EXTRACTION_MODE = "layout"  # keeps empty lines between paragraphs; "plain" (the default) drops them
MIN_PAGE_SHARE_FOR_REPEATED = 0.5  # a line on half the pages or more is a header or footer


@dataclass
class CleanPage:
    """The clean text of one PDF page, and its page number (for "see page 3" answers in 4.10)."""

    page_number: int  # 1-based, as a PDF viewer shows it, e.g. 2
    page_text: str  # e.g. "Refunds\n\nYou can get a refund within 14 days..."


def line_pattern(line: str) -> str:
    """Given: the line's pattern, so "Page 1 of 6" and "Page 2 of 6" count as the same line.

    No own log lines: runs once per line; its callers log the totals.
    Args:
        line: e.g. "        Page 2 of 6".
    Returns:
        e.g. "Page # of #": spaces at both ends removed, every run of digits -> "#".
    """
    stripped_line = line.strip()
    line_pattern = re.sub(r"\d+", "#", stripped_line)  # \d+ = one or more digits
    return line_pattern


@debug
def read_pdf_pages(pdf_path: Path) -> list[str]:
    """Read the text of every page of a PDF, in page order.

    How:
        1. Open the file with PdfReader(pdf_path).
        2. For each page in reader.pages: page.extract_text(extraction_mode=PDF_EXTRACTION_MODE).
        3. Keep empty pages too (a scan gives ""), so list position + 1 = page number.
    Args:
        pdf_path: e.g. Path("04_rag/4_2_pdf_loading/handbook_4_2.pdf").
    Returns:
        e.g. ["Lumen Notes - Support Handbook (internal)\\nLumen Notes support handbook\\n\\n...", ..., ""].
    Raises:
        FileNotFoundError: no such file (PdfReader raises it for you).
    """
    raise NotImplementedError


@debug
def find_repeated_lines(page_texts: list[str]) -> set[str]:
    """Find the headers and footers: line patterns that show up on many pages.

    How:
        1. Per page: the set of line_pattern(line) of its non-empty lines (a set: twice on one page counts once).
        2. Count on how many pages each pattern shows up.
        3. Keep a pattern on 2+ pages AND on MIN_PAGE_SHARE_FOR_REPEATED of the pages or more.
    Args:
        page_texts: e.g. ["Head\\nA\\nPage 1 of 2", "Head\\nB\\nPage 2 of 2"].
    Returns:
        e.g. {"Head", "Page # of #"}; set() for one page or none (nothing to compare).
    """
    raise NotImplementedError


@debug
def remove_repeated_lines(page_text: str, repeated_patterns: set[str]) -> str:
    """Drop the header and footer lines from one page; keep everything else, empty lines too.

    How:
        1. Go through the lines of page_text.
        2. Keep a line unless its line_pattern(line) is in repeated_patterns.
        3. Join the kept lines with "\\n".
    Args:
        page_text: e.g. "Head\\nA\\n\\nB\\nPage 1 of 2".
        repeated_patterns: e.g. {"Head", "Page # of #"} (from find_repeated_lines).
    Returns:
        e.g. "A\\n\\nB".
    """
    raise NotImplementedError


@debug
def fix_characters(page_text: str) -> str:
    """Turn look-alike characters into the plain ones: "ﬁ" -> "fi", no-break space -> space.

    How:
        1. unicodedata.normalize("NFKC", page_text) does it all ("NFKC" = Unicode's
           "compatibility" form: each fancy character -> its plain twin).
    Args:
        page_text: e.g. "con\\ufb01rmation link works for 48\\xa0hours".
    Returns:
        e.g. "confirmation link works for 48 hours".
    """
    raise NotImplementedError


@debug
def join_broken_words(page_text: str) -> str:
    """Glue words cut at a line end back together: "confir-\\nmation" -> "confirmation".

    How:
        1. Find: a letter or digit, "-", a line break, maybe spaces, a lower-case letter.
           As a regex: r"(\\w)-\\n *([a-z])".
        2. Replace it with the two letters only: r"\\1\\2" (\\1 = what the first ( ) found).
    Args:
        page_text: e.g. "the confir-\\nmation link".
    Returns:
        e.g. "the confirmation link". "Retry-After" (no line break) stays as it is.
    """
    raise NotImplementedError


@debug
def join_paragraph_lines(page_text: str) -> str:
    """Make each paragraph one line; one empty line between paragraphs; no extra spaces.

    How:
        1. Go through the lines. A line with only spaces (or nothing) ends a paragraph.
        2. Inside a paragraph: " ".join(line.split()) per line (runs of spaces -> one),
           then join its lines with one space.
        3. Skip empty paragraphs; join the paragraphs with "\\n\\n".
    Args:
        page_text: e.g. "  Refunds\\n\\n\\n\\nYou can get a refund\\nwithin   14 days.\\n   ".
    Returns:
        e.g. "Refunds\\n\\nYou can get a refund within 14 days."; "" for only spaces.
    """
    raise NotImplementedError


@debug
def clean_pdf_pages(pdf_path: Path) -> list[CleanPage]:
    """Read a PDF and clean every page: the whole lesson in one function.

    How:
        1. read_pdf_pages, then find_repeated_lines over all pages.
        2. Per page, in this order: remove_repeated_lines -> fix_characters
           -> join_broken_words -> join_paragraph_lines.
        3. Skip a page that is empty after cleaning (a scan: log it); keep the PDF page number.
    Args:
        pdf_path: e.g. Path("04_rag/4_2_pdf_loading/handbook_4_2.pdf").
    Returns:
        e.g. [CleanPage(1, "Lumen Notes support handbook\\n\\n..."), ..., CleanPage(5, "...")].
    """
    raise NotImplementedError
