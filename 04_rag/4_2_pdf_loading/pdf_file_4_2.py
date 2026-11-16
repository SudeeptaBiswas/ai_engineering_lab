"""Given helper for lesson 4.2: write pages of PDF drawing commands into a real .pdf file.

Used by make_pdf_4_2.py. You don't need to read this to do the lesson; it shows that a PDF
is numbered objects (pages, fonts, drawing commands) plus a table of where each one starts.
"""

from pathlib import Path

from lab_tools.log import debug, log

PAGE_WIDTH = 612  # US Letter, in points (1 point = 1/72 inch)
PAGE_HEIGHT = 792
# Font encoding: normal Windows letters, except byte 128 = the "fi" sign and 129 = "fl"
FONT_ENCODING = b"<< /Type /Encoding /BaseEncoding /WinAnsiEncoding /Differences [128 /fi /fl] >>"


@debug
def write_pdf_file(page_drawings: list[bytes], pdf_path: Path) -> int:
    """Write the PDF file: numbered objects, then a table of where each object starts (the "xref").

    How:
        1. Objects 1-5: catalog, page list, 2 fonts, the font encoding (with the ligatures).
        2. Per page: a page object + its drawing commands.
        3. xref table + trailer, so a reader can jump to any object.
    Args:
        page_drawings: one bytes block per page, e.g. from draw_text_page(...).
        pdf_path: e.g. Path("handbook_4_2.pdf").
    Returns:
        File size in bytes, e.g. 11983.
    """
    log.debug("start: %d pages -> %s", len(page_drawings), pdf_path.name)
    page_count = len(page_drawings)
    first_page_object = 6
    page_references = b" ".join(b"%d 0 R" % (first_page_object + 2 * page_index) for page_index in range(page_count))  # rule-ok: "6 0 R 8 0 R ..."
    pdf_objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
                   b"<< /Type /Pages /Kids [%s] /Count %d >>" % (page_references, page_count),
                   b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding 5 0 R >>",
                   b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding 5 0 R >>",
                   FONT_ENCODING]
    for page_index in range(page_count):
        content_object = first_page_object + 2 * page_index + 1
        pdf_objects.append(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] /Resources << /Font << /F1 3 0 R "
                           b"/F2 4 0 R >> >> /Contents %d 0 R >>" % (PAGE_WIDTH, PAGE_HEIGHT, content_object))
        page_drawing = page_drawings[page_index]
        pdf_objects.append(b"<< /Length %d >>\nstream\n%sendstream" % (len(page_drawing), page_drawing))
    pdf_bytes = b"%PDF-1.4\n"
    object_offsets: list[int] = []
    for object_index in range(len(pdf_objects)):
        object_offsets.append(len(pdf_bytes))
        pdf_bytes += b"%d 0 obj\n%s\nendobj\n" % (object_index + 1, pdf_objects[object_index])
    xref_offset = len(pdf_bytes)
    pdf_bytes += b"xref\n0 %d\n0000000000 65535 f \n" % (len(pdf_objects) + 1)
    for object_offset in object_offsets:
        pdf_bytes += b"%010d 00000 n \n" % object_offset
    pdf_bytes += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(pdf_objects) + 1, xref_offset)
    pdf_path.write_bytes(pdf_bytes)
    log.debug("result: %d pages, %d bytes -> %s", page_count, len(pdf_bytes), pdf_path.name)
    return len(pdf_bytes)
