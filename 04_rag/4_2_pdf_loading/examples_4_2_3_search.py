"""Part 3 of 3: does cleaning help the 4.1 vector search? Raw vs clean text. Needs Ollama + nomic-embed-text.

Run (15–18 s, the embed calls):
  uv run python 04_rag/4_2_pdf_loading/examples_4_2_3_search.py

Both texts: cut every 500 characters, overlap 100 (4.1, no headings left in a PDF),
embed, then ask the 9 handbook questions of 4.1. Is the chunk with the answer found?
"""

import time  # time.perf_counter() = a stopwatch
from dataclasses import dataclass

import httpx
import numpy as np
import numpy.typing as npt

from examples_4_2_1_read import PDF_PATH, read_pages
from examples_4_2_2_clean import clean_all_pages, glue_cut_words, make_characters_plain, make_paragraphs_one_line
from lab_tools.log import cut_text, debug, log

OLLAMA_URL = "http://127.0.0.1:11434"
EMBEDDING_MODEL = "nomic-embed-text"
CHUNK_SIZE = 500  # characters, as in 4.1 section 2
CHUNK_OVERLAP = 100
TOP_K = 3


@dataclass
class EmbeddedTexts:
    """What one embed call gives back: the vectors, and how many tokens the model read."""

    vectors: npt.NDArray[np.float64]  # one row per text, 768 numbers each
    token_count: int  # e.g. 1884, Ollama's "prompt_eval_count"


@dataclass
class EvalQuestion:
    """A handbook question from 4.1 and words the right chunk must contain."""

    question: str  # e.g. "How long does the password reset link work?"
    answer_phrase: str  # e.g. "15 minutes"


EVAL_QUESTIONS = [
    EvalQuestion("How long does the password reset link work?", "15 minutes"),
    EvalQuestion("My account got locked after wrong passwords. How long until I can try again?", "30 minutes"),
    EvalQuestion("How much does the Plus plan cost per year?", "60"),
    EvalQuestion("I paid three weeks ago. Can I still get a refund?", "14 days"),
    EvalQuestion("How long do deleted notes stay in the trash?", "30 days"),
    EvalQuestion("What happens if I edit the same note on two devices while offline?", "conflict"),
    EvalQuestion("How many requests per minute can one API key make?", "600"),
    EvalQuestion("How long is the download link for a full account export valid?", "7 days"),
    EvalQuestion("What is the biggest attachment I can add?", "200 mb"),
]


@debug
def cut_by_size(document_text: str) -> list[str]:
    """Cut a text into CHUNK_SIZE pieces, each repeating the last CHUNK_OVERLAP characters (4.1).

    Args:
        document_text: e.g. all pages joined.
    Returns:
        e.g. 17 pieces of up to 500 characters.
    """
    log.debug("start: %d characters", len(document_text))
    chunks: list[str] = []
    start = 0
    while start < len(document_text):
        end = start + CHUNK_SIZE
        chunks.append(document_text[start:end])
        if end >= len(document_text):  # this piece reached the end
            break
        start = start + CHUNK_SIZE - CHUNK_OVERLAP
    log.debug("result: %d chunks", len(chunks))
    return chunks


@debug
def embed_and_count_tokens(texts: list[str]) -> EmbeddedTexts:
    """Embed texts in one call (2.5); also return how many tokens the model read.

    Args:
        texts: e.g. 17 chunks.
    Returns:
        e.g. EmbeddedTexts(vectors=<17 x 768 table>, token_count=1884).
    """
    log.debug("start: %d texts", len(texts))
    request_body = {"model": EMBEDDING_MODEL, "input": texts}
    response = httpx.post(f"{OLLAMA_URL}/api/embed", json=request_body, timeout=300.0)
    response.raise_for_status()
    reply_json = response.json()
    vectors = np.array(reply_json["embeddings"], dtype=np.float64)
    token_count = int(reply_json["prompt_eval_count"])  # tokens Ollama read for all texts together
    embedded_texts = EmbeddedTexts(vectors=vectors, token_count=token_count)
    log.debug("result: shape=%s tokens=%d", vectors.shape, token_count)
    return embedded_texts


@debug
def has_answer(chunk_text: str, answer_phrase: str) -> bool:
    """Judge a chunk fairly: clean a COPY first, so raw chunks aren't marked wrong for "15\\xa0minutes".

    Args:
        chunk_text: e.g. "...expires after 15\\xa0minutes and can..."
        answer_phrase: e.g. "15 minutes".
    Returns:
        e.g. True.
    """
    log.debug("start: %s", cut_text(chunk_text))
    judged_text = make_characters_plain(chunk_text)
    judged_text = glue_cut_words(judged_text)
    judged_text = make_paragraphs_one_line(judged_text).lower()
    is_found = answer_phrase.lower() in judged_text
    log.debug("expected=%r got=%s is_found=%s", answer_phrase, cut_text(judged_text), is_found)
    return is_found


@debug
def score_search(document_text: str) -> str:
    """Chunk, embed, ask the 9 questions; count right chunk 1st and right chunk in the top 3.

    Args:
        document_text: the raw or the clean text.
    Returns:
        e.g. "17 chunks, 1884 tokens, embed 4.9 s | right chunk 1st 8/9, in top 3 9/9".
    """
    log.debug("start: %d characters", len(document_text))
    chunks = cut_by_size(document_text)
    embed_start = time.perf_counter()
    embedded_chunks = embed_and_count_tokens(chunks)
    embed_seconds = time.perf_counter() - embed_start
    first_count = 0
    top_three_count = 0
    for eval_question in EVAL_QUESTIONS:
        embedded_question = embed_and_count_tokens([eval_question.question])
        question_vector = embedded_question.vectors[0]  # [0] = the only row
        scores = embedded_chunks.vectors @ question_vector  # one dot product per chunk (4.1)
        best_first_rows = np.argsort(-scores, kind="stable")[:TOP_K]
        found_in_rows: list[bool] = []
        for row_number in best_first_rows:
            found_in_rows.append(has_answer(chunks[int(row_number)], eval_question.answer_phrase))
        if found_in_rows[0]:  # the best chunk has the answer
            first_count += 1
        if True in found_in_rows:  # one of the top 3 has it
            top_three_count += 1
    question_count = len(EVAL_QUESTIONS)
    score_row = (f"{len(chunks)} chunks, {embedded_chunks.token_count} tokens, embed {embed_seconds:.1f} s | "
                 f"right chunk 1st {first_count}/{question_count}, in top {TOP_K} {top_three_count}/{question_count}")
    log.debug("result: %s", score_row)
    return score_row


if __name__ == "__main__":
    raw_page_texts = read_pages(PDF_PATH, "layout")
    raw_text = "\n".join(raw_page_texts)
    clean_text = "\n\n".join(clean_all_pages(raw_page_texts))
    print("Search, 9 handbook questions (4.1):")
    print(f"   raw  : {score_search(raw_text)}")
    print(f"   clean: {score_search(clean_text)}")
