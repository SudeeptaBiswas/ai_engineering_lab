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
import unicodedata  # Unicode tables: normalize() turns look-alike characters into plain ones
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from lab_tools.log import cut_text, debug, log

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
    log.debug("start: %s, mode=%s", pdf_path.name, PDF_EXTRACTION_MODE)
    reader = PdfReader(pdf_path)  # opens the file; reads pages only when asked
    page_texts: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text(extraction_mode=PDF_EXTRACTION_MODE)
        page_texts.append(page_text)
    log.debug("result: %d pages", len(page_texts))
    return page_texts


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
    log.debug("start: %d pages", len(page_texts))
    pages_per_pattern: dict[str, int] = {}
    for page_text in page_texts:
        patterns_on_page: set[str] = set()
        for line in page_text.split("\n"):
            if line.strip() != "":
                patterns_on_page.add(line_pattern(line))
        for line_on_pattern in patterns_on_page:
            pages_per_pattern[line_on_pattern] = pages_per_pattern.get(line_on_pattern, 0) + 1  # .get(key, 0): 0 if new
    header_footer_patterns: set[str] = set()
    for line_on_pattern in pages_per_pattern:
        page_count = pages_per_pattern[line_on_pattern]
        if page_count >= 2 and page_count >= MIN_PAGE_SHARE_FOR_REPEATED * len(page_texts):
            header_footer_patterns.add(line_on_pattern)
    log.debug("result: %s", header_footer_patterns)
    return header_footer_patterns


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
    log.debug("start: %s, %d patterns", cut_text(page_text), len(repeated_patterns))
    kept_lines: list[str] = []
    for line in page_text.split("\n"):
        if line_pattern(line) not in repeated_patterns:
            kept_lines.append(line)
    kept_text = "\n".join(kept_lines)
    log.debug("result: %d -> %d characters", len(page_text), len(kept_text))
    return kept_text


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
    log.debug("start: %s", cut_text(page_text))
    plain_text = unicodedata.normalize("NFKC", page_text)  # NFKC: each look-alike -> its plain twin
    log.debug("result: %d -> %d characters", len(page_text), len(plain_text))
    return plain_text


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
    log.debug("start: %s", cut_text(page_text))
    glued_text = re.sub(r"(\w)-\n *([a-z])", r"\1\2", page_text)  # \1, \2 = the 2 letters the ( ) found
    log.debug("result: %d -> %d characters", len(page_text), len(glued_text))
    return glued_text


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
    log.debug("start: %s", cut_text(page_text))
    paragraph_texts: list[str] = []
    paragraph_lines: list[str] = []
    for line in page_text.split("\n") + [""]:  # + [""]: one more empty line closes the last paragraph
        if line.strip() == "":
            if len(paragraph_lines) > 0:
                paragraph_texts.append(" ".join(paragraph_lines))
            paragraph_lines = []
        else:
            paragraph_lines.append(" ".join(line.split()))  # split() with no argument: at any run of spaces
    one_line_text = "\n\n".join(paragraph_texts)
    log.debug("result: %d paragraphs", len(paragraph_texts))
    return one_line_text


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
    log.debug("start: %s", pdf_path.name)
    page_texts = read_pdf_pages(pdf_path)
    repeated_patterns = find_repeated_lines(page_texts)
    clean_pages: list[CleanPage] = []
    for page_index, page_text in enumerate(page_texts):  # enumerate: (0, first page), (1, second page), ...
        page_number = page_index + 1
        without_repeats = remove_repeated_lines(page_text, repeated_patterns)
        plain_text = fix_characters(without_repeats)
        glued_text = join_broken_words(plain_text)
        clean_text = join_paragraph_lines(glued_text)
        if clean_text == "":
            log.debug("page %d is empty after cleaning (a scan?): skipped", page_number)
        else:
            clean_pages.append(CleanPage(page_number, clean_text))
    log.debug("result: %d of %d pages", len(clean_pages), len(page_texts))
    return clean_pages
