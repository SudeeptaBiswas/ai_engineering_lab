"""Part 2 of 3: clean the PDF text step by step, and measure after each step. No Ollama.

Run (~1 s):
  uv run python 04_rag/4_2_pdf_loading/examples_4_2_2_clean.py

One row per step:  strange words (not in the source handbook) | answers found by exact text | characters
Pages are joined with an empty line between them ("\\n\\n"), so "raw" has 10 characters more than part 1.
"""

import re
import unicodedata  # Unicode tables: normalize() turns look-alike characters into plain ones
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from examples_4_2_1_read import PDF_PATH, read_pages
from lab_tools.log import cut_text, debug, log

SOURCE_HANDBOOK_PATH = Path(__file__).parent.parent / "4_1_rag_by_hand" / "handbook_4_1.md"
MIN_PAGE_SHARE = 0.5  # a line on half the pages or more = a header or footer
# Answers to the 9 handbook questions of 4.1 (examples_4_1_3_answer.py), as plain text
ANSWER_PHRASES = ["15 minutes", "30 minutes", "60", "14 days", "30 days", "conflict", "600", "7 days", "200 MB"]


@dataclass
class CleaningStep:
    """One cleaning step for a single page: its name for the table, and the function that does it."""

    step_name: str  # e.g. "3. glue cut words"
    page_cleaner: Callable[[str], str]  # a function: page text in, cleaner page text out


@dataclass
class StepResult:
    """All pages after one step, so main can measure and print each step."""

    step_name: str  # e.g. "raw" or "1. remove header + footer"
    page_texts: list[str]  # e.g. 6 texts


def pattern_of_line(line: str) -> str:
    """Make lines that differ only in numbers look the same, so "Page 1 of 6" and "Page 2 of 6" count as one repeated footer.

    How:
        1. Remove spaces at both ends (layout mode puts spaces in front of a centred footer).
        2. Replace each run of digits with "#".
    No own log lines: runs once per line; its callers log the totals.
    Args:
        line: e.g. "        Page 2 of 6".
    Returns:
        e.g. "Page # of #", the same for every page.
    """
    stripped_line = line.strip()
    line_pattern = re.sub(r"\d+", "#", stripped_line)  # \d+ = one or more digits
    return line_pattern


@debug
def find_header_footer_patterns(page_texts: list[str]) -> set[str]:
    """Find the patterns of lines that show up on many pages: the headers and footers.

    How:
        1. Per page: the set of line patterns (a set, so a line twice on one page counts once).
        2. Count pages per pattern; keep those on 2+ pages and on MIN_PAGE_SHARE of the pages.
    Args:
        page_texts: e.g. read_pages(PDF_PATH, "layout").
    Returns:
        e.g. {"Lumen Notes - Support Handbook (internal)", "Page # of #"}.
    """
    log.debug("start: %d pages", len(page_texts))
    pages_per_pattern: dict[str, int] = {}
    for page_text in page_texts:
        patterns_on_page: set[str] = set()
        for line in page_text.split("\n"):
            if line.strip() != "":
                patterns_on_page.add(pattern_of_line(line))
        for line_pattern in patterns_on_page:
            pages_per_pattern[line_pattern] = pages_per_pattern.get(line_pattern, 0) + 1  # .get(key, 0): 0 if new
    header_footer_patterns: set[str] = set()
    for line_pattern in pages_per_pattern:
        page_count = pages_per_pattern[line_pattern]
        if page_count >= 2 and page_count >= MIN_PAGE_SHARE * len(page_texts):
            header_footer_patterns.add(line_pattern)
    log.debug("result: %s", header_footer_patterns)
    return header_footer_patterns


@debug
def remove_header_footer(page_texts: list[str]) -> list[str]:
    """Step 1: find the header and footer patterns, then drop those lines from every page.

    Args:
        page_texts: e.g. read_pages(PDF_PATH, "layout").
    Returns:
        The same pages without header and footer lines; empty lines stay.
    """
    log.debug("start: %d pages", len(page_texts))
    header_footer_patterns = find_header_footer_patterns(page_texts)
    pages_without_repeats: list[str] = []
    for page_text in page_texts:
        kept_lines: list[str] = []
        for line in page_text.split("\n"):
            if pattern_of_line(line) not in header_footer_patterns:
                kept_lines.append(line)
        pages_without_repeats.append("\n".join(kept_lines))
    log.debug("result: %d pages", len(pages_without_repeats))
    return pages_without_repeats


@debug
def make_characters_plain(page_text: str) -> str:
    """Step 2: turn "ﬁ" into "fi" and a no-break space into a space, with Unicode's NFKC form.

    Args:
        page_text: e.g. a page with "con" + ligature + "rmation" and "48" + no-break space + "hours".
    Returns:
        e.g. "confirmation ... 48 hours".
    """
    log.debug("start: %s", cut_text(page_text))
    plain_text = unicodedata.normalize("NFKC", page_text)  # NFKC: each look-alike -> its plain twin
    log.debug("result: %d -> %d characters", len(page_text), len(plain_text))
    return plain_text


@debug
def glue_cut_words(page_text: str) -> str:
    """Step 3: glue "confir-" + line break + "mation" back into "confirmation".

    Args:
        page_text: e.g. "in Sett-\\nings".
    Returns:
        e.g. "in Settings".
    """
    log.debug("start: %s", cut_text(page_text))
    glued_text = re.sub(r"(\w)-\n *([a-z])", r"\1\2", page_text)  # \1, \2 = the 2 letters the ( ) found
    log.debug("result: %d -> %d characters", len(page_text), len(glued_text))
    return glued_text


@debug
def make_paragraphs_one_line(page_text: str) -> str:
    """Step 4: one line per paragraph, one empty line between paragraphs, single spaces.

    Args:
        page_text: e.g. "Refunds\\n\\n\\nYou can get a refund\\nwithin   14 days.".
    Returns:
        e.g. "Refunds\\n\\nYou can get a refund within 14 days.".
    """
    log.debug("start: %s", cut_text(page_text))
    paragraph_texts: list[str] = []
    for paragraph_block in re.split(r"\n\s*\n", page_text):  # split at empty lines
        words = paragraph_block.split()  # split() with no argument: at any run of spaces or line breaks
        if len(words) > 0:
            paragraph_texts.append(" ".join(words))
    one_line_text = "\n\n".join(paragraph_texts)
    log.debug("result: %d paragraphs", len(paragraph_texts))
    return one_line_text


@debug
def collect_words(document_text: str) -> set[str]:
    """Collect the words of a text in lower case, to compare two texts word by word.

    Args:
        document_text: e.g. "Within 14 days."
    Returns:
        e.g. {"within", "14", "days"}.
    """
    log.debug("start: %d characters", len(document_text))
    found_words = set(re.findall(r"\w+", document_text.lower()))  # \w+ = a run of letters or digits
    log.debug("result: %d words", len(found_words))
    return found_words


@debug
def measure_text(page_texts: list[str], source_words: set[str]) -> str:
    """Score the pages after one step: one table row with 3 numbers.

    Strange words: not in the source handbook, e.g. "sett" from "Sett-ings" (fewer = cleaner). Answers: ANSWER_PHRASES found as exact text (more = better).

    Args:
        page_texts: the pages after some cleaning step.
        source_words: collect_words(the source handbook).
    Returns:
        e.g. "14 strange words | 3/9 answers found | 6902 characters".
    """
    log.debug("start: %d pages", len(page_texts))
    all_text = "\n\n".join(page_texts)
    strange_words = collect_words(all_text) - source_words  # in the PDF text but not in the source
    found_count = 0
    for answer_phrase in ANSWER_PHRASES:
        if answer_phrase in all_text:
            found_count += 1
    table_row = f"{len(strange_words):2} strange words | {found_count}/{len(ANSWER_PHRASES)} answers found | {len(all_text)} characters"
    log.debug("result: %s, strange=%s", table_row, sorted(strange_words)[:6])
    return table_row


@debug
def run_cleaning_steps(page_texts: list[str]) -> list[StepResult]:
    """Run the 4 steps in order and keep the pages after each, so each step can be measured.

    Args:
        page_texts: e.g. read_pages(PDF_PATH, "layout").
    Returns:
        5 results: "raw", then one per step; the last one holds the clean pages.
    """
    log.debug("start: %d pages", len(page_texts))
    step_results = [StepResult("raw", page_texts),
                    StepResult("1. remove header + footer", remove_header_footer(page_texts))]
    page_steps = [CleaningStep("2. plain characters (NFKC)", make_characters_plain),
                  CleaningStep("3. glue cut words", glue_cut_words),
                  CleaningStep("4. one line per paragraph", make_paragraphs_one_line)]
    for page_step in page_steps:
        pages_before = step_results[-1].page_texts  # [-1] = the newest result
        pages_after: list[str] = []
        for page_text in pages_before:
            pages_after.append(page_step.page_cleaner(page_text))
        step_results.append(StepResult(page_step.step_name, pages_after))
    log.debug("result: %d results", len(step_results))
    return step_results


@debug
def clean_all_pages(page_texts: list[str]) -> list[str]:
    """Run all steps and drop pages left empty (the scan has no text at all).

    Args:
        page_texts: e.g. read_pages(PDF_PATH, "layout").
    Returns:
        The clean pages, e.g. 5 texts.
    """
    log.debug("start: %d pages", len(page_texts))
    last_result = run_cleaning_steps(page_texts)[-1]
    clean_pages: list[str] = []
    for page_text in last_result.page_texts:
        if page_text != "":
            clean_pages.append(page_text)
    log.debug("result: %d of %d pages", len(clean_pages), len(page_texts))
    return clean_pages


if __name__ == "__main__":
    raw_page_texts = read_pages(PDF_PATH, "layout")
    handbook_words = collect_words(SOURCE_HANDBOOK_PATH.read_text(encoding="utf-8"))
    print(f"Cleaning {PDF_PATH.name}, one row per step:")
    for step_result in run_cleaning_steps(raw_page_texts):
        print(f"   {step_result.step_name:28}: {measure_text(step_result.page_texts, handbook_words)}")
    final_pages = clean_all_pages(raw_page_texts)
    print(f"\n{len(final_pages)} pages left. Page 2, first 300 characters:\n{final_pages[1][:300]}")
