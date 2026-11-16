"""Given helper for lesson 4.2: turn the 4.1 handbook (Markdown) into a PDF with real-world mess.

Run once (~0.1 s; handbook_4_2.pdf is already in the folder, this re-makes it):
  uv run python 04_rag/4_2_pdf_loading/make_pdf_4_2.py

The mess follows fixed rules, the way word processors do it. No word is picked by hand:
  1. header + footer on every page      "Lumen Notes - Support Handbook (internal)", "Page 2 of 6"
  2. long words cut at the line end     "confir-" / "mation"
  3. "fi" and "fl" drawn as ONE sign    "ﬁ" (a ligature), not "f" + "i"
  4. a no-break space after a number    "15\\xa0minutes", so number and unit stay on one line
  5. a scanned page at the end          a picture of text: no text in the file at all
"""

import re
from dataclasses import dataclass
from pathlib import Path

from lab_tools.log import cut_text, debug, log
from pdf_file_4_2 import PAGE_HEIGHT, PAGE_WIDTH, write_pdf_file

LESSON_FOLDER = Path(__file__).parent  # this file's folder
SOURCE_HANDBOOK_PATH = LESSON_FOLDER.parent / "4_1_rag_by_hand" / "handbook_4_1.md"
PDF_PATH = LESSON_FOLDER / "handbook_4_2.pdf"
MARGIN = 72  # points between the text and the paper edge (1 inch)
MAX_LINE_CHARACTERS = 92  # ~ what fits in 468 points of 10-point Helvetica
MIN_WORD_PART = 3  # a cut word keeps at least 3 letters on each line
HEADER_TEXT = "Lumen Notes - Support Handbook (internal)"
FOOTER_TEMPLATE = "Page {page_number} of {page_count}"
NO_BREAK_SPACE = "\xa0"  # looks like a space, but is a different character
LIGATURE_CODES = {"fi": "\x80", "fl": "\x81"}  # 2 letters -> 1 byte; FONT_ENCODING maps it to one sign


@dataclass
class PdfLine:
    """One line on a page: which font, how big, what text, how much space above it."""

    font_key: str  # "F1" = Helvetica, "F2" = Helvetica-Bold
    font_size: int  # in points, e.g. 10
    line_text: str  # e.g. "You can sign up with an email address or with a Google account. A new"
    space_above: int  # points from the line above, e.g. 14


@debug
def cut_paragraph_into_lines(paragraph_text: str) -> list[str]:
    """Cut one paragraph into lines of at most MAX_LINE_CHARACTERS, cutting long words with "-".

    How:
        1. Add words to the line while they fit.
        2. A word that doesn't fit and has 2 x MIN_WORD_PART+ letters: put the first part + "-" on this line.
        3. Else the word starts the next line.
    Args:
        paragraph_text: e.g. "We send a confirmation email right after sign-up; ..." (one line, no "\\n").
    Returns:
        e.g. ["We send a confir-", "mation email right after sign-up; ..."] (at a narrower width).
    """
    log.debug("start: %s", cut_text(paragraph_text))
    lines: list[str] = []
    current_line = ""
    for word in paragraph_text.split(" "):  # split on normal spaces only: "15\xa0minutes" stays one word
        line_with_word = word if current_line == "" else current_line + " " + word  # rule-ok: tiny
        if len(line_with_word) <= MAX_LINE_CHARACTERS:
            current_line = line_with_word
            continue
        free_characters = MAX_LINE_CHARACTERS - len(current_line) - 2  # - 2 = the space before + the "-"
        can_cut_word = word.isalpha() and free_characters >= MIN_WORD_PART and len(word) - free_characters >= MIN_WORD_PART
        if can_cut_word:
            lines.append(current_line + " " + word[:free_characters] + "-")
            current_line = word[free_characters:]
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    log.debug("result: %d words -> %d lines", paragraph_text.count(" ") + 1, len(lines))
    return lines


@debug
def lay_out_handbook(handbook_markdown: str) -> list[PdfLine]:
    """Turn the Markdown handbook into PDF lines: title, bold headings, paragraphs cut into lines.

    How:
        1. Split into blocks at empty lines.
        2. "# " = title (18 pt), "## " = heading (13 pt bold; the "## " is not printed).
        3. Other blocks = one paragraph: join its lines, add no-break spaces, cut into lines.
    Args:
        handbook_markdown: the text of handbook_4_1.md.
    Returns:
        e.g. [PdfLine("F2", 18, "Lumen Notes support handbook", 0), PdfLine("F1", 10, ...), ...].
    """
    log.debug("start: %d characters", len(handbook_markdown))
    pdf_lines: list[PdfLine] = []
    for block_text in handbook_markdown.strip().split("\n\n"):
        if block_text.startswith("# "):
            pdf_lines.append(PdfLine("F2", 18, block_text.removeprefix("# "), 0))
        elif block_text.startswith("## "):
            pdf_lines.append(PdfLine("F2", 13, block_text.removeprefix("## "), 26))
        else:
            paragraph_text = block_text.replace("\n", " ")
            paragraph_text = re.sub(r"(\d) (?=[a-z])", r"\1" + NO_BREAK_SPACE, paragraph_text)  # "15 minutes" -> "15\xa0minutes"
            space_above = 20  # a gap before a new paragraph
            for paragraph_line in cut_paragraph_into_lines(paragraph_text):
                pdf_lines.append(PdfLine("F1", 10, paragraph_line, space_above))
                space_above = 14  # the normal line height inside a paragraph
    log.debug("result: %d lines", len(pdf_lines))
    return pdf_lines


@debug
def split_into_pages(pdf_lines: list[PdfLine]) -> list[list[PdfLine]]:
    """Fill pages top to bottom, leaving room for the header and the footer.

    Args:
        pdf_lines: e.g. lay_out_handbook(...).
    Returns:
        One list of lines per page, e.g. 5 pages.
    """
    log.debug("start: %d lines", len(pdf_lines))
    usable_height = PAGE_HEIGHT - 2 * MARGIN - 30  # - 30 = header and its gap
    pages: list[list[PdfLine]] = [[]]
    used_height = 0
    for pdf_line in pdf_lines:
        if used_height + pdf_line.space_above + pdf_line.font_size > usable_height:
            pages.append([])
            used_height = 0
        pages[-1].append(pdf_line)
        used_height += pdf_line.space_above + pdf_line.font_size
    log.debug("result: %d pages", len(pages))
    return pages


def to_pdf_string(line_text: str) -> bytes:
    """Write a line as PDF string bytes: escape \\ ( ), swap "fi"/"fl" for their ligature codes.

    No own log lines: runs once per line; draw_text_page logs the page.
    Args:
        line_text: e.g. "official (all plans)".
    Returns:
        e.g. b"o\\x80cial \\\\(all plans\\\\)" (one byte per character).
    """
    escaped_text = line_text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    for letter_pair, ligature_code in LIGATURE_CODES.items():
        escaped_text = escaped_text.replace(letter_pair, ligature_code)
    pdf_string = escaped_text.encode("latin-1")  # 1 character -> 1 byte; "\x80" -> byte 128 (our "fi")
    return pdf_string


@debug
def draw_text_page(page_lines: list[PdfLine], page_number: int, page_count: int) -> bytes:
    """Draw one text page: header, the lines, footer. PDF y counts from the BOTTOM of the page.

    Args:
        page_lines: one entry of split_into_pages(...).
        page_number: 1-based, e.g. 2.
        page_count: all pages, the scan included, e.g. 6.
    Returns:
        The page's drawing commands, e.g. b"BT /F1 8 Tf 72 740 Td (Lumen ...) Tj ET\\n...".
    """
    log.debug("start: page %d of %d, %d lines", page_number, page_count, len(page_lines))
    footer_text = FOOTER_TEMPLATE.format(page_number=page_number, page_count=page_count)
    drawing_commands = b"BT /F1 8 Tf %d %d Td (%s) Tj ET\n" % (MARGIN, PAGE_HEIGHT - MARGIN + 20, to_pdf_string(HEADER_TEXT))
    y_position = PAGE_HEIGHT - MARGIN - 10
    for page_line in page_lines:
        y_position -= page_line.space_above
        line_bytes = to_pdf_string(page_line.line_text)
        drawing_commands += b"BT /%s %d Tf %d %d Td (%s) Tj ET\n" % (
            page_line.font_key.encode(), page_line.font_size, MARGIN, y_position, line_bytes)
    drawing_commands += b"BT /F1 8 Tf %d %d Td (%s) Tj ET\n" % (PAGE_WIDTH // 2 - 25, MARGIN - 30, to_pdf_string(footer_text))
    log.debug("result: page %d, %d lines, %d bytes", page_number, len(page_lines), len(drawing_commands))
    return drawing_commands


@debug
def draw_scanned_page() -> bytes:
    """Draw a stand-in for a scanned page: grey bars where text would be, but no text at all.

    Returns:
        Drawing commands with only rectangles ("re" = rectangle, "f" = fill), no "Tj" (text).
    """
    log.debug("start: 30 grey bars")
    drawing_commands = b"0.6 g\n"  # fill colour: grey
    for bar_number in range(30):
        bar_y = PAGE_HEIGHT - MARGIN - 20 - bar_number * 18
        drawing_commands += b"%d %d 440 8 re f\n" % (MARGIN, bar_y)
    log.debug("result: %d bytes", len(drawing_commands))
    return drawing_commands


@debug
def make_handbook_pdf(pdf_path: Path) -> int:
    """Build the messy handbook PDF: text pages, then one scanned page.

    Args:
        pdf_path: where to write it, e.g. PDF_PATH.
    Returns:
        The page count, e.g. 6.
    """
    log.debug("start: %s -> %s", SOURCE_HANDBOOK_PATH.name, pdf_path.name)
    handbook_markdown = SOURCE_HANDBOOK_PATH.read_text(encoding="utf-8")
    text_pages = split_into_pages(lay_out_handbook(handbook_markdown))
    page_count = len(text_pages) + 1  # + 1 = the scanned page
    page_drawings: list[bytes] = []
    for page_index in range(len(text_pages)):
        page_drawings.append(draw_text_page(text_pages[page_index], page_index + 1, page_count))
    page_drawings.append(draw_scanned_page())
    write_pdf_file(page_drawings, pdf_path)
    log.debug("result: %d pages", page_count)
    return page_count


if __name__ == "__main__":
    made_page_count = make_handbook_pdf(PDF_PATH)
    print(f"{PDF_PATH.name}: {made_page_count} pages, {PDF_PATH.stat().st_size} bytes")
