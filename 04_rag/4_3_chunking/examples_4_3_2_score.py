"""Part 2 of 3: which way of cutting finds the answer? Needs Ollama + nomic-embed-text.

Run (~1 min, the embed calls):
  uv run python 04_rag/4_3_chunking/examples_4_3_2_score.py

12 handbook questions. A chunk is right only if it holds the WHOLE answer sentence,
e.g. "The reset link we send expires after 15 minutes and can be used only once".
  1. size  : cut by characters, 200 to 2000, with and without overlap
  2. ways  : sentences, paragraphs + headings, recursive, at 200 / 500 / 1000
"""

from dataclasses import dataclass

import httpx
import numpy as np
import numpy.typing as npt

from examples_4_3_1_cut import (HANDBOOK_PATH, SEPARATORS_BIGGEST_FIRST, cut_at_biggest_boundary, cut_at_paragraphs,
                                cut_at_sentences, cut_every_n_characters)
from lab_tools.log import debug, log

OLLAMA_URL = "http://127.0.0.1:11434"
EMBEDDING_MODEL = "nomic-embed-text"
TOP_K = 3  # chunks that would go into the prompt (4.1)
SIZES_AND_OVERLAPS = [(200, 0), (200, 40), (500, 0), (500, 100), (1000, 0), (1000, 200), (2000, 400)]
MAX_CHARACTERS_TRIED = [200, 500, 1000]


@dataclass
class EvalQuestion:
    """A handbook question and the whole sentence that answers it."""

    question: str  # e.g. "How long does the password reset link work?"
    answer_sentence: str  # e.g. "The reset link we send expires after 15 minutes and can be used only once"


@dataclass
class SearchScore:
    """How one way of cutting did on the 12 questions."""

    chunk_count: int  # e.g. 16
    right_first: int  # questions whose best chunk holds the answer sentence, e.g. 12
    right_in_top: int  # ... whose top 3 hold it, e.g. 12
    characters_per_question: int  # the top 3 chunks together: what the model would read, e.g. 1160


EVAL_QUESTIONS = [
    EvalQuestion("How long does the password reset link work?",
                 "The reset link we send expires after 15 minutes and can be used only once"),
    EvalQuestion("My account got locked after wrong passwords. How long until I can try again?",
                 "After 5 wrong passwords in a row, the account is locked for 30 minutes"),
    EvalQuestion("How much does the Plus plan cost per year?", "6 euros per month or 60 euros per year"),
    EvalQuestion("I paid three weeks ago. Can I still get a refund?", "After 14 days we do not refund"),
    EvalQuestion("How long do deleted notes stay in the trash?", "Deleted notes stay in the Trash for 30 days"),
    EvalQuestion("What happens if I edit the same note on two devices while offline?",
                 'the second one is saved as a copy with "(conflict)" in its title'),
    EvalQuestion("How many requests per minute can one API key make?", "Each API key may make 600 requests per minute"),
    EvalQuestion("How long is the download link for a full account export valid?", "the link stays valid for 7 days"),
    EvalQuestion("What is the biggest attachment I can add?", "Each attachment can be at most 200 MB"),
    EvalQuestion("What happens when my payment fails three times?",
                 "After the third failed try, the account moves back to the Free plan"),
    EvalQuestion("I lost my phone and my backup codes. How do I get into my account?",
                 "support can turn two-step sign-in off, but only after an identity check"),
    EvalQuestion("How many members can a shared notebook have?",
                 "A shared notebook (Team only) can have at most 50 members"),
]


@debug
def embed_texts(texts: list[str]) -> npt.NDArray[np.float64]:
    """Turn texts into vectors in one call (2.5).

    Args:
        texts: e.g. 16 chunks.
    Returns:
        A table, one row of 768 numbers per text, e.g. shape (16, 768).
    """
    log.debug("start: %d texts", len(texts))
    request_body = {"model": EMBEDDING_MODEL, "input": texts}
    response = httpx.post(f"{OLLAMA_URL}/api/embed", json=request_body, timeout=600.0)
    response.raise_for_status()
    vectors = np.array(response.json()["embeddings"], dtype=np.float64)
    log.debug("result: shape=%s", vectors.shape)
    return vectors


@debug
def score_search(chunks: list[str], question_vectors: npt.NDArray[np.float64]) -> SearchScore:
    """Embed the chunks, ask the 12 questions, count where the whole answer sentence is found.

    How:
        1. Embed all chunks; score them against each question (4.1: table @ vector).
        2. Look in the best 3 chunks for the answer sentence.
        3. Add up the length of those 3: what the model would have to read.
    Args:
        chunks: e.g. cut_at_sentences(handbook, 500).
        question_vectors: embed_texts(the 12 questions), shape (12, 768).
    Returns:
        e.g. SearchScore(chunk_count=14, right_first=11, right_in_top=12, characters_per_question=1334).
    """
    log.debug("start: %d chunks", len(chunks))
    chunk_vectors = embed_texts(chunks)
    right_first = 0
    right_in_top = 0
    total_characters = 0
    for question_number in range(len(EVAL_QUESTIONS)):
        answer_sentence = EVAL_QUESTIONS[question_number].answer_sentence.lower()
        scores = chunk_vectors @ question_vectors[question_number]  # one score per chunk
        best_first_rows = np.argsort(-scores, kind="stable")[:TOP_K]
        found_in_rows: list[bool] = []
        for row_number in best_first_rows:
            best_chunk = chunks[int(row_number)]
            found_in_rows.append(answer_sentence in best_chunk.lower())
            total_characters += len(best_chunk)
        log.debug("question %d: expected the answer in the top %d got %s", question_number + 1, TOP_K,
                  found_in_rows)
        if found_in_rows[0]:  # the best chunk holds it
            right_first += 1
        if True in found_in_rows:
            right_in_top += 1
    search_score = SearchScore(len(chunks), right_first, right_in_top, total_characters // len(EVAL_QUESTIONS))
    log.debug("result: %s", search_score)
    return search_score


@debug
def format_score(way_name: str, search_score: SearchScore) -> str:
    """One table row for the screen.

    Args:
        way_name: e.g. "characters 500, overlap 100".
        search_score: e.g. score_search(...).
    Returns:
        e.g. "characters 500, overlap 100  16 chunks | right 1st 11/12, in top 3 11/12 | 1438 characters".
    """
    question_count = len(EVAL_QUESTIONS)
    score_row = (f"{way_name:30} {search_score.chunk_count:2} chunks | "
                 f"right 1st {search_score.right_first:2}/{question_count}, "
                 f"in top {TOP_K} {search_score.right_in_top:2}/{question_count} | "
                 f"{search_score.characters_per_question} characters to read")
    log.debug("result: %s", score_row)
    return score_row


if __name__ == "__main__":
    handbook_text = HANDBOOK_PATH.read_text(encoding="utf-8")
    question_texts: list[str] = []
    for eval_question in EVAL_QUESTIONS:
        question_texts.append(eval_question.question)
    all_question_vectors = embed_texts(question_texts)

    print("1. cut by characters: size and overlap")
    for size_and_overlap in SIZES_AND_OVERLAPS:
        chunk_size = size_and_overlap[0]
        overlap = size_and_overlap[1]
        size_chunks = cut_every_n_characters(handbook_text, chunk_size, overlap)
        size_score = score_search(size_chunks, all_question_vectors)
        print(f"   {format_score(f'characters {chunk_size}, overlap {overlap}', size_score)}")

    print("\n2. cut at boundaries, same max size")
    for max_characters in MAX_CHARACTERS_TRIED:
        ways_to_cut = {
            f"sentences {max_characters}": cut_at_sentences(handbook_text, max_characters),
            f"paragraphs + headings {max_characters}": cut_at_paragraphs(handbook_text, max_characters, True),
            f"recursive {max_characters}": cut_at_biggest_boundary(handbook_text, max_characters,
                                                                   SEPARATORS_BIGGEST_FIRST),
        }
        for way_name in ways_to_cut:
            way_score = score_search(ways_to_cut[way_name], all_question_vectors)
            print(f"   {format_score(way_name, way_score)}")
