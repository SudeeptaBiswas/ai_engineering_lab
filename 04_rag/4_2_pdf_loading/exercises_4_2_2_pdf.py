"""Tests for pdf_text_4_2.py, part 2: the real handbook PDF. No Ollama.

  uv run pytest 04_rag/4_2_pdf_loading/exercises_4_2_2_pdf.py -v
"""

import re
from pathlib import Path

import pytest

from lab_tools.log import debug, log
from pdf_text_4_2 import CleanPage, clean_pdf_pages, find_repeated_lines, read_pdf_pages

LESSON_FOLDER = Path(__file__).parent  # this file's folder
PDF_PATH = LESSON_FOLDER / "handbook_4_2.pdf"  # made by make_pdf_4_2.py
SOURCE_HANDBOOK_PATH = LESSON_FOLDER.parent / "4_1_rag_by_hand" / "handbook_4_1.md"  # the text the PDF was made from
PDF_PAGE_COUNT = 6  # 5 text pages + 1 scanned page
HEADER_LINE = "Lumen Notes - Support Handbook (internal)"
# Answers to the 4.1 handbook questions, as plain text (examples_4_1_3_answer.py)
EXPECTED_ANSWER_PHRASES = ["15 minutes", "30 minutes", "60", "14 days", "30 days", "conflict", "600",
                           "7 days", "200 MB"]


@pytest.fixture(scope="module")
@debug
def clean_pages() -> list[CleanPage]:
    """Clean the PDF once for all tests in this file (a "module" fixture, 1.9).

    Returns:
        clean_pdf_pages(PDF_PATH), e.g. 5 CleanPage objects.
    """
    pages = clean_pdf_pages(PDF_PATH)
    log.debug("result: %d pages", len(pages))
    return pages


@debug
def collect_words(document_text: str) -> set[str]:
    """Collect the words of a text in lower case, so two texts can be compared word by word.

    Args:
        document_text: e.g. "Within 14 days."
    Returns:
        e.g. {"within", "14", "days"}.
    """
    found_words = set(re.findall(r"\w+", document_text.lower()))  # \w+ = a run of letters, digits or _
    log.debug("result: %d words", len(found_words))
    return found_words


@debug
def test_read_pdf_pages_keeps_every_page_in_order() -> None:
    """All 6 pages come back, the scan as "": then list position + 1 is still the page number."""
    page_texts = read_pdf_pages(PDF_PATH)
    log.debug("expected=%d got=%d", PDF_PAGE_COUNT, len(page_texts))
    assert len(page_texts) == PDF_PAGE_COUNT
    first_page_first_line = page_texts[0].split("\n")[0]
    log.debug("expected=%r got=%r", HEADER_LINE, first_page_first_line)
    assert first_page_first_line == HEADER_LINE
    scanned_page_text = page_texts[PDF_PAGE_COUNT - 1]
    log.debug("expected='' got=%r", scanned_page_text.strip())
    assert scanned_page_text.strip() == ""


@debug
def test_read_pdf_pages_keeps_empty_lines_between_paragraphs() -> None:
    """Layout mode keeps the gaps between paragraphs: without them, 4.3 can't cut at paragraphs."""
    page_texts = read_pdf_pages(PDF_PATH)
    has_empty_line = "\n\n" in page_texts[0]
    log.debug("expected=True got=%s", has_empty_line)
    assert has_empty_line


@debug
def test_read_pdf_pages_raises_for_a_missing_file(tmp_path: Path) -> None:
    """A wrong path must fail loudly, not give an empty list that looks like an empty PDF.

    Args:
        tmp_path: an empty folder pytest makes for this test.
    """
    missing_pdf_path = tmp_path / "no_such_file.pdf"
    log.debug("expected=FileNotFoundError for %s", missing_pdf_path.name)
    with pytest.raises(FileNotFoundError):
        read_pdf_pages(missing_pdf_path)


@debug
def test_find_repeated_lines_finds_the_real_header_and_footer() -> None:
    """On the real PDF, only the header and the "Page N of 6" footer are found: a real sentence must never be removed."""
    page_texts = read_pdf_pages(PDF_PATH)
    found_patterns = find_repeated_lines(page_texts)
    expected_patterns = {HEADER_LINE, "Page # of #"}
    log.debug("expected=%r got=%r", expected_patterns, found_patterns)
    assert found_patterns == expected_patterns


@debug
def test_clean_pdf_pages_skips_the_scan_and_keeps_page_numbers(clean_pages: list[CleanPage]) -> None:
    """The scan (page 6) has no text, so it goes; the others keep their PDF page numbers for citations.

    Args:
        clean_pages: the fixture above.
    """
    page_numbers: list[int] = []
    for clean_page in clean_pages:
        page_numbers.append(clean_page.page_number)
    expected_page_numbers = [1, 2, 3, 4, 5]
    log.debug("expected=%r got=%r", expected_page_numbers, page_numbers)
    assert page_numbers == expected_page_numbers


@debug
def test_clean_pdf_pages_has_only_words_of_the_source(clean_pages: list[CleanPage]) -> None:
    """Every word in the clean text is a word of the original handbook: no "con\\ufb01rmation", no "Sett", no header.

    Args:
        clean_pages: the fixture above.
    """
    all_clean_text = ""
    for clean_page in clean_pages:
        all_clean_text += clean_page.page_text + "\n\n"
    source_text = SOURCE_HANDBOOK_PATH.read_text(encoding="utf-8")
    strange_words = collect_words(all_clean_text) - collect_words(source_text)  # in the PDF text, not in the source
    log.debug("expected=set() got=%r", strange_words)
    assert strange_words == set()


@debug
def test_clean_pdf_pages_lets_exact_search_find_every_answer(clean_pages: list[CleanPage]) -> None:
    """Every answer phrase is found by plain `in` (raw text: 3 of 9), as 4.7 keyword search needs.

    Args:
        clean_pages: the fixture above.
    """
    all_clean_text = ""
    for clean_page in clean_pages:
        all_clean_text += clean_page.page_text + "\n\n"
    missing_phrases: list[str] = []
    for answer_phrase in EXPECTED_ANSWER_PHRASES:
        if answer_phrase not in all_clean_text:
            missing_phrases.append(answer_phrase)
    log.debug("expected=[] got=%r", missing_phrases)
    assert missing_phrases == []
