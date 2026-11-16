"""Tests for pdf_text_4_2.py, part 1: cleaning small texts. No PDF, no Ollama.

  uv run pytest 04_rag/4_2_pdf_loading/exercises_4_2_1_text.py -v
"""

import pytest

from lab_tools.log import debug, log
from pdf_text_4_2 import (fix_characters, find_repeated_lines, join_broken_words, join_paragraph_lines,
                          remove_repeated_lines)


NO_PAGES: list[str] = []  # typed empty values, so pyright knows what the rows hold
NO_PATTERNS: set[str] = set()


@pytest.mark.parametrize(("page_texts", "expected_patterns"), [
    # header + footer on both pages; the page numbers differ, the pattern is the same
    (["Head\nA\nPage 1 of 2", "Head\nB\nPage 2 of 2"], {"Head", "Page # of #"}),
    # on 2 of 3 pages (67%) is enough; "A" on 1 of 3 is not
    (["Head\nA", "Head\nB", "C"], {"Head"}),
    # on 2 of 5 pages (40%) is too few: maybe just a common sentence
    (["Head\nA", "Head\nB", "C", "D", "E"], NO_PATTERNS),
    # twice on ONE page is not a header: count pages, not lines
    (["Note\nNote\nA", "B"], NO_PATTERNS),
    # one page: nothing to compare with
    (["Head\nA\nPage 1 of 1"], NO_PATTERNS),
    # no pages at all
    (NO_PAGES, NO_PATTERNS),
    # pages with only empty lines: empty lines never count
    (["\n\n", "\n\n"], NO_PATTERNS),
])
@debug
def test_find_repeated_lines_finds_headers_and_footers(page_texts: list[str], expected_patterns: set[str]) -> None:
    """Lines on most pages are headers or footers: they would sit in every chunk and teach search nothing.

    Args:
        page_texts: a few small pages.
        expected_patterns: the line patterns that should come back.
    """
    found_patterns = find_repeated_lines(page_texts)
    log.debug("expected=%r got=%r", expected_patterns, found_patterns)
    assert found_patterns == expected_patterns


@pytest.mark.parametrize(("page_text", "expected_text"), [
    # header and footer go, the empty line between paragraphs stays
    ("Head\nA\n\nB\nPage 1 of 2", "A\n\nB"),
    # the footer is found by its pattern, even with spaces in front (layout mode)
    ("A\n          Page 7 of 9", "A"),
    # a line that only CONTAINS the header words stays
    ("Head office is in Oslo.\nA", "Head office is in Oslo.\nA"),
])
@debug
def test_remove_repeated_lines_drops_only_whole_matching_lines(page_text: str, expected_text: str) -> None:
    """Only whole header/footer lines go: a sentence that mentions the same words is real content.

    Args:
        page_text: one small page.
        expected_text: the page without its header and footer.
    """
    repeated_patterns = {"Head", "Page # of #"}
    page_without_repeats = remove_repeated_lines(page_text, repeated_patterns)
    log.debug("expected=%r got=%r", expected_text, page_without_repeats)
    assert page_without_repeats == expected_text


@pytest.mark.parametrize(("page_text", "expected_text"), [
    ("con\ufb01rmation", "confirmation"),  # "ﬁ" ligature: one sign -> "f" + "i"
    ("of\ufb02ine", "offline"),            # "ﬂ" ligature -> "f" + "l"
    ("48\xa0hours", "48 hours"),              # no-break space -> normal space
    ("Plain text, 14 days.", "Plain text, 14 days."),  # plain text stays the same
])
@debug
def test_fix_characters_turns_look_alikes_into_plain_characters(page_text: str, expected_text: str) -> None:
    """Look-alike characters break exact search: "48 hours" is not found in "48\\xa0hours".

    Args:
        page_text: text with a look-alike character.
        expected_text: the same text with plain characters.
    """
    plain_text = fix_characters(page_text)
    log.debug("expected=%r got=%r", expected_text, plain_text)
    assert plain_text == expected_text


@pytest.mark.parametrize(("page_text", "expected_text"), [
    ("the confir-\nmation link", "the confirmation link"),  # the basic case
    ("in Sett-\n   ings", "in Settings"),                    # spaces before the next line (layout mode)
    ("the Retry-After header", "the Retry-After header"),    # a real hyphen inside a line stays
    ("version 7.4-\n8.1", "version 7.4-\n8.1"),               # next line starts with a digit: not a cut word
    ("Plans -\nprices", "Plans -\nprices"),                   # space before "-": a dash, not a cut word
    ("sign-\nup", "signup"),                                  # known loss: a real hyphen at a line end goes too
])
@debug
def test_join_broken_words_glues_word_parts(page_text: str, expected_text: str) -> None:
    """A word cut in two is two strange words ("confir", "mation") that no search will match.

    Args:
        page_text: text with a word cut at a line end.
        expected_text: the same text with the word whole.
    """
    joined_text = join_broken_words(page_text)
    log.debug("expected=%r got=%r", expected_text, joined_text)
    assert joined_text == expected_text


@pytest.mark.parametrize(("page_text", "expected_text"), [
    # lines of one paragraph join with a space; one empty line between paragraphs
    ("Refunds\n\nYou can get a refund\nwithin 14 days.", "Refunds\n\nYou can get a refund within 14 days."),
    # many empty lines (layout mode) -> one; spaces at line ends and starts go
    ("  A b  \n c\n\n\n\n   \nD  \n", "A b c\n\nD"),
    # runs of spaces inside a line -> one space
    ("within   14    days", "within 14 days"),
    # nothing but spaces and line breaks -> ""
    ("\n   \n\n", ""),
    # nothing in, nothing out
    ("", ""),
])
@debug
def test_join_paragraph_lines_gives_one_line_per_paragraph(page_text: str, expected_text: str) -> None:
    """One line per paragraph, one empty line between: 4.3 can cut at paragraphs, and no space is wasted.

    Args:
        page_text: text with PDF line breaks and spaces.
        expected_text: the same text, one paragraph per line.
    """
    joined_text = join_paragraph_lines(page_text)
    log.debug("expected=%r got=%r", expected_text, joined_text)
    assert joined_text == expected_text
