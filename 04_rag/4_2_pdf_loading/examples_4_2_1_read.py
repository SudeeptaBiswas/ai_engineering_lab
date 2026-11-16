"""Part 1 of 3: read the handbook PDF with pypdf and look at the mess. No Ollama.

Run (~1 s):
  uv run python 04_rag/4_2_pdf_loading/examples_4_2_1_read.py

  1. read  : "plain" vs "layout" mode: characters, paragraph gaps, time
  2. look  : the first lines of page 1, as Python sees them (ascii() shows hidden characters)
  3. count : headers, footers, ligatures, no-break spaces, cut words, empty pages
"""

import re
import time  # time.perf_counter() = a stopwatch
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pypdf import PdfReader

from lab_tools.log import debug, log

LESSON_FOLDER = Path(__file__).parent  # this file's folder
PDF_PATH = LESSON_FOLDER / "handbook_4_2.pdf"  # made by make_pdf_4_2.py from the 4.1 handbook
ExtractionMode = Literal["plain", "layout"]  # pypdf's two ways to turn a page into text (Literal: 1.6)
EXTRACTION_MODES: list[ExtractionMode] = ["plain", "layout"]
HEADER_LINE = "Lumen Notes - Support Handbook (internal)"
FOOTER_REGEX = r"Page \d+ of \d+"  # "Page 2 of 6"; \d+ = one or more digits
CUT_WORD_REGEX = r"\w-\n *[a-z]"  # a letter, "-", line break, a lower-case letter: "confir-\nmation"
LIGATURES = ["\ufb01", "\ufb02"]  # "ﬁ" and "ﬂ": one character each
NO_BREAK_SPACE = "\xa0"
SHOWN_LINE_COUNT = 11  # how many lines of page 1 to print


@dataclass
class MessCount:
    """How much of each kind of mess the text of a PDF has."""

    header_lines: int  # e.g. 5: one per text page
    footer_lines: int  # e.g. 5
    ligatures: int  # e.g. 19
    no_break_spaces: int  # e.g. 41
    cut_words: int  # e.g. 3
    empty_pages: int  # e.g. 1: the scan


@debug
def read_pages(pdf_path: Path, extraction_mode: ExtractionMode) -> list[str]:
    """Read every page of a PDF as text, with one of pypdf's two modes.

    Args:
        pdf_path: e.g. PDF_PATH.
        extraction_mode: "plain" (pypdf's default) or "layout" (keeps empty lines).
    Returns:
        One text per page, e.g. 6 texts, the last one "" (the scan).
    """
    log.debug("start: %s, mode=%s", pdf_path.name, extraction_mode)
    reader = PdfReader(pdf_path)  # opens the file; reads pages only when asked
    page_texts: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text(extraction_mode=extraction_mode)
        page_texts.append(page_text)
    log.debug("result: %d pages", len(page_texts))
    return page_texts


@debug
def count_paragraph_gaps(page_texts: list[str]) -> int:
    """Count empty lines between text: the gaps that show where a paragraph ends.

    Args:
        page_texts: e.g. read_pages(PDF_PATH, "layout").
    Returns:
        e.g. 0 for plain mode, 42 for layout mode.
    """
    log.debug("start: %d pages", len(page_texts))
    gap_count = 0
    for page_text in page_texts:
        gap_count += len(re.findall(r"\S\n\s*\n\s*\S", page_text))  # text, empty line(s), text
    log.debug("result: %d gaps", gap_count)
    return gap_count


@debug
def count_mess(page_texts: list[str]) -> MessCount:
    """Count each kind of mess, so we can see it go away step by step in part 2.

    Args:
        page_texts: e.g. read_pages(PDF_PATH, "layout").
    Returns:
        e.g. MessCount(header_lines=5, footer_lines=5, ligatures=19, ...).
    """
    log.debug("start: %d pages", len(page_texts))
    all_text = "\n".join(page_texts)
    ligature_count = 0
    for ligature in LIGATURES:
        ligature_count += all_text.count(ligature)
    empty_page_count = 0
    for page_text in page_texts:
        if page_text.strip() == "":
            empty_page_count += 1
    mess_count = MessCount(header_lines=all_text.count(HEADER_LINE),
                           footer_lines=len(re.findall(FOOTER_REGEX, all_text)),
                           ligatures=ligature_count,
                           no_break_spaces=all_text.count(NO_BREAK_SPACE),
                           cut_words=len(re.findall(CUT_WORD_REGEX, all_text)),
                           empty_pages=empty_page_count)
    log.debug("result: %s", mess_count)
    return mess_count


if __name__ == "__main__":
    print(f"1. read {PDF_PATH.name} ({PDF_PATH.stat().st_size} bytes):")
    for mode in EXTRACTION_MODES:
        read_start = time.perf_counter()
        mode_page_texts = read_pages(PDF_PATH, mode)
        read_milliseconds = (time.perf_counter() - read_start) * 1000
        character_count = len("".join(mode_page_texts))
        gap_count = count_paragraph_gaps(mode_page_texts)
        print(f"   {mode:6}: {len(mode_page_texts)} pages, {character_count} characters, "
              f"{gap_count} paragraph gaps, {read_milliseconds:.0f} ms")

    layout_page_texts = read_pages(PDF_PATH, "layout")
    print(f"\n2. page 1, first {SHOWN_LINE_COUNT} lines (layout mode), as ascii():")
    first_page_lines = layout_page_texts[0].split("\n")
    for shown_line in first_page_lines[:SHOWN_LINE_COUNT]:
        print(f"   {ascii(shown_line)}")  # ascii(): \ufb01 = "ﬁ", \xa0 = no-break space

    print("\n3. mess in the whole PDF (layout mode):")
    print(f"   {count_mess(layout_page_texts)}")
