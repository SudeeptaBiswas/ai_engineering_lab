# 4.2 Loading PDFs, cleaning text: from a PDF file to text search can trust (~3 h)

Basic level, phase 04. Uses: 4.1 (chunks, search, the 9 handbook
questions), 2.5 (embeddings), 1.6 (`Literal`), 1.9 (fixtures). Next:
4.3 cut at paragraphs, 4.5 LangChain's PDF loader, 4.6 PDF Q&A,
4.7 keyword search, 4.10 "see page 3".

All numbers **measured on 10284Sudee** (CPU only), pypdf 7.1.0,
Ollama 0.40.16, nomic-embed-text, 2026-11-16. Scores were the same in 3 runs.
(*) = checked once with a one-off script that was not kept.

## The problem
Same handbook as 4.1, but now it is a PDF:
[handbook_4_2.pdf](handbook_4_2.pdf) (open it: it looks normal).
The answer to *"How long does the password reset link work?"* is on page 1:
**15 minutes**. Read the PDF with pypdf, then search for the answer:
```python
"15 minutes" in pdf_text    # False
```
Why? Between "15" and "minutes" is not a space. It is a **no-break space**
(`"\xa0"`): it looks the same, but it is a different character.
Exact text search finds only **3 of the 9** handbook answers.
And the text has **14 words that are not in the handbook**:
`con\ufb01rmation`, `Sett`, `ings`, `internal`...

## Goal
Clean text per page, with its page number: **0** strange words,
**9/9** answers found by exact text. Under 1 s for the whole PDF (part 2: 0.6 s).

## How we get there
A PDF is not text. It is drawing orders: *"draw these letters at this
spot"*. pypdf reads the letters back and guesses the lines.
What looks nice on paper is noise for search:
the same header on every page, words cut at the line end, two letters
drawn as one sign. We undo each of these, one step at a time,
and measure after each step.

## Steps
```
1. Read each page as text (pypdf, "layout" mode).   6 pages -> 6 texts, the last one ""
2. Find + remove headers and footers.               "Page 2 of 6" -> gone
3. Turn look-alike characters into plain ones.     "con\ufb01rm" -> "confirm", "15\xa0min" -> "15 min"
4. Glue words cut at a line end.                    "Sett-\nings" -> "Settings"
5. One line per paragraph; drop empty pages.        5 clean pages, numbers 1-5
```

## Your path
1. Read sections 1–3. Run part 1.
2. Read section 4. Run part 2.
3. Read sections 5–6. Run part 3.
4. Do the exercises: write the 7 functions yourself.

## Java → Python map
| Java | Python |
|---|---|
| PDFBox `PDFTextStripper.getText(doc)` | pypdf `page.extract_text()` |
| `Normalizer.normalize(s, Normalizer.Form.NFKC)` | `unicodedata.normalize("NFKC", s)` |
| `s.replaceAll("(\\w)-\\n *([a-z])", "$1$2")` | `re.sub(r"(\w)-\n *([a-z])", r"\1\2", s)` |
| `map.merge(key, 1, Integer::sum)` | `counts[key] = counts.get(key, 0) + 1` |

## 1. What is inside a PDF?
Here is one line of page 1, as the PDF file stores it:
```
BT /F1 10 Tf 72 616 Td (Free plan. We send a con\200rmation email ...) Tj ET
```
- `BT ... ET` = a text block. `/F1 10 Tf` = font 1, 10 points.
  `72 616 Td` = go to x 72, y 616 (y counts from the **bottom**).
  `(...) Tj` = draw these letters.
- No words, no lines, no paragraphs: just letters at spots.
  pypdf turns spots back into lines. It is a good guess, not the truth.
- `\200` = byte 128. This font maps it to **one sign for "fi"**:
  a **ligature** (two letters drawn as one, because "f" and "i" touch).
  pypdf gives it back as one character: `"\ufb01"` (`ﬁ`).

Our PDF is made by [make_pdf_4_2.py](make_pdf_4_2.py) from the 4.1
handbook. It follows fixed rules, the way Word or LaTeX do. No word was
picked by hand. Same facts as 4.1, so we can reuse the 4.1 questions.

## 2. Reading a page with pypdf
```python
reader = PdfReader(pdf_path)                    # opens the file
for page in reader.pages:                       # one Page object per page
    page_text = page.extract_text(extraction_mode="layout")
```
Two modes. Part 1 prints this:

| Mode | Characters | Paragraph gaps | Time (6 pages) |
|---|---|---|---|
| `"plain"` (the default) | 6 346 | **0** | 35 ms |
| `"layout"` | 6 892 | **42** | 21 ms |

- **plain** loses every empty line. A heading and its paragraph run
  together. 4.3 wants to cut at paragraphs, so that's a loss.
- **layout** keeps the gaps. Cost: extra spaces and empty lines
  (the last text page has ~75 empty lines: counted once by hand (*)). Step 5 removes them.
- Time: both tiny. (The first call loads pypdf's code, so it is slower.)

> ▶ **Now run part 1** (no Ollama, ~1 s): modes, page 1 as `ascii()`, mess counts.
> `uv run python 04_rag/4_2_pdf_loading/examples_4_2_1_read.py`

`ascii()` prints hidden characters as codes: `\ufb01` = `ﬁ`, `\xa0` = no-break
space. Also: when output goes to a pipe or a file, a plain `print("ﬁ")`
crashed on this PC: Windows code page `cp932` has no sign for it.

## 3. The mess, kind by kind
| Kind | Example (raw) | Count | Why it hurts |
|---|---|---|---|
| header | `Lumen Notes - Support Handbook (internal)` | 5 | in every chunk; a word ("internal") the handbook never uses |
| footer | `Page 2 of 6` | 5 | same; and the number changes per page |
| ligature | `con\ufb01rmation`, `of\ufb02ine` | 19 | `"confirmation"` is not found |
| no-break space | `15\xa0minutes` | 41 | `"15 minutes"` is not found |
| cut word | `Sett-` / `ings` | 3 | 2 strange words instead of 1 real one |
| empty page | page 6 (a scan) | 1 | no text at all: a picture of text |

## 4. Clean in four steps
Part 2 runs the steps in order and measures after each:

| After step | Strange words | Answers found (exact) | Characters |
|---|---|---|---|
| raw | 14 | 3/9 | 6 902 |
| 1. remove header + footer | 13 | 3/9 | 6 349 |
| 2. plain characters (NFKC) | 6 | **9/9** | 6 368 |
| 3. glue cut words | **0** | 9/9 | 6 362 |
| 4. one line per paragraph | 0 | 9/9 | 6 132 |

Raw is 6 902 here, 6 892 in part 1: part 2 puts an empty line between pages (+10).

- **Header / footer** = a line on half the pages or more. To match
  "Page 1 of 6" with "Page 2 of 6", digits become `#` first:
  both are `"Page # of #"` (`line_pattern`, given).
- **NFKC** = Unicode's "compatibility" form: each look-alike
  character becomes its plain twin. `ﬁ` → `fi`, no-break space → space.
- **Glue**: a letter or digit, `-`, a line break, a lower-case letter → the two
  letters only. `Retry-After` (no line break) stays.
- **Order matters.** Remove the header **before** joining lines, or it
  is glued into a paragraph. Glue cut words **before** joining lines,
  or the `-\n` is gone.

> ▶ **Now run part 2** (no Ollama, ~1 s): one row per step.
> `uv run python 04_rag/4_2_pdf_loading/examples_4_2_2_clean.py`

## 5. Does cleaning help the search?
Same as 4.1: cut every 500 characters, overlap 100, embed, 9 questions.
A PDF has no `## ` left, so cutting by heading is not possible (4.3).

| Text | Chunks | Tokens | Right chunk 1st | in top 3 |
|---|---|---|---|---|
| raw | 17 | 1 884 | 8/9 | 9/9 |
| clean | 16 | 1 757 | **9/9** | 9/9 |

- **Vector search hardly cares.** The one raw miss ("biggest attachment")
  was a near tie: 0.485 vs 0.483 (*). Embeddings read meaning, not exact signs.
- **Exact search cares a lot**: 3/9 vs 9/9 (section 4). That is what
  4.7 keyword search, the 4.1 answer check, and 4.10 quotes depend on.
- **7% fewer tokens** (1 884 → 1 757): no headers, no extra spaces.
- To be fair, the judge cleans a **copy** of each chunk before looking
  for the answer. Else raw chunks would lose only because of `\xa0`.

> ▶ **Now run part 3** (needs Ollama, 15–18 s): raw vs clean search.
> `uv run python 04_rag/4_2_pdf_loading/examples_4_2_3_search.py`

## 6. Things that bite
- **Scans have no text.** Page 6 gives `""`. You need OCR (image →
  text, e.g. Tesseract). Not in this course. Always count empty pages.
- **A real hyphen at a line end is lost**: `sign-` / `up` → `signup`.
  The glue can't tell. Rare; we accept it (a test says so).
- **NFKC changes more than ligatures**: `m²` → `m2`, `½` → `1⁄2`.
  Fine for search; keep the raw text if you must show exact signs.
- **The header rule only counts. It can't read.** It removes any line
  that shows up on half the pages or more. Two ways that goes wrong:
  - *Too few pages*: a 1-page PDF. Its header shows up on 1 page only,
    so it looks like normal text and **stays**.
  - *A real sentence repeats*: a 6-page manual ends 3 pages with
    "Contact support at help@lumen.example." 3 of 6 = half, so that
    line is **removed**, though it is real content.
  So after cleaning, look at what `find_repeated_lines` returned.
- **Columns and tables**: layout mode reads straight across the page,
  so two columns get mixed line by line. Check a page by eye first.
- **Headings are lost.** Bold 13-point "Refunds" is just a line now.
  4.3 cuts at paragraphs instead.

## 7. Where it is used next
| Lesson | Uses |
|---|---|
| 4.3 Chunking | the one-line paragraphs: cut at `"\n\n"` |
| 4.5 LangChain | `PyPDFLoader` = step 1, one "Document" per page |
| 4.6 PDF Q&A, assistant v3 | `clean_pdf_pages` on your own PDFs |
| 4.7 Hybrid search | exact words (BM25) next to vectors |
| 4.10 Citations | `CleanPage.page_number` → "see page 3" |

## Exercises: PDF → clean pages
**Goal:** the steps above, in [pdf_text_4_2.py](pdf_text_4_2.py), until
all 32 tests pass. Each function has a `How:` list in its docstring.
The tests are the spec: [exercises_4_2_1_text.py](exercises_4_2_1_text.py)
(small texts), then [exercises_4_2_2_pdf.py](exercises_4_2_2_pdf.py) (the
real PDF). No Ollama needed. Follow [CODE_STYLE.md](../../docs/CODE_STYLE.md).

| # | Function | Goal | Example: in → out | Tests |
|---|---|---|---|---|
| 1 | `read_pdf_pages` | one text per page, layout mode | `handbook_4_2.pdf` → 6 texts, last `""` | 3 |
| 2 | `find_repeated_lines` | header + footer patterns | `["Head\nA\nPage 1 of 2", "Head\nB\nPage 2 of 2"]` → `{"Head", "Page # of #"}` | 7 + 1 |
| 3 | `remove_repeated_lines` | drop those lines from a page | `"Head\nA\n\nB\nPage 1 of 2"` → `"A\n\nB"` | 3 |
| 4 | `fix_characters` | NFKC | `"con\ufb01rm 48\xa0hours"` → `"confirm 48 hours"` | 4 |
| 5 | `join_broken_words` | glue `-\n` | `"the confir-\nmation"` → `"the confirmation"` | 6 |
| 6 | `join_paragraph_lines` | one line per paragraph | `"A b\n c\n\n\nD"` → `"A b c\n\nD"` | 5 |
| 7 | `clean_pdf_pages` | functions 1–6, in order | `handbook_4_2.pdf` → `CleanPage(1, ...)` … `CleanPage(5, ...)` | 3 |

Edge cases the tests check (so you don't have to guess):
- `find_repeated_lines`: count **pages**, not lines (twice on one page = 1).
  2+ pages AND half the pages or more. One page or none → `set()`.
  Empty lines never count.
- `remove_repeated_lines`: only whole lines whose `line_pattern` matches.
  "Head office is in Oslo." stays. Empty lines stay.
- `join_broken_words`: next line starts with a digit (`7.4-` / `8.1`) or
  there is a space before `-` → no change. `sign-` / `up` → `signup`.
- `join_paragraph_lines`: runs of spaces → one; only spaces → `""`.
- `read_pdf_pages`: missing file → `FileNotFoundError` (pypdf raises it).
- `clean_pdf_pages`: skip pages empty after cleaning, but keep the PDF's
  page numbers (1, 2, 3, 4, 5, not 0–4).

Run: `uv run pytest 04_rag/4_2_pdf_loading -v`.
Reference solution, measured: **32 passed in 0.27–0.63 s** (6 runs),
pyright 0. The stubs: 29 failed, 3 errors (the fixture calls `clean_pdf_pages`).
