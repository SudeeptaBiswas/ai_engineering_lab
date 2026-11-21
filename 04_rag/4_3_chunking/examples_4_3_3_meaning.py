"""Part 3 of 3: cut where the topic changes ("semantic chunking"). Needs Ollama + nomic-embed-text.

Run (~20 s):
  uv run python 04_rag/4_3_chunking/examples_4_3_3_meaning.py

  1. look  : the 5 places where two sentences in a row are least alike
  2. score : cut there (10% / 25% lowest), same 12 questions as part 2, vs paragraphs + headings
  3. cost  : embedding every sentence vs embedding the chunks only
"""

import re
import time  # time.perf_counter() = a stopwatch

import numpy as np
import numpy.typing as npt

from examples_4_3_1_cut import HANDBOOK_PATH, SENTENCE_END_REGEX, cut_at_paragraphs, find_paragraphs
from examples_4_3_2_score import EVAL_QUESTIONS, embed_texts, format_score, score_search
from lab_tools.log import debug, log

MAX_CHARACTERS = 500
LOWEST_SHOWN = 5  # how many topic changes to print
CUT_PERCENTS = [10, 25]  # cut at the 10% (or 25%) least alike pairs


@debug
def list_sentences(document_text: str) -> list[str]:
    """Every sentence of a text, headings included, in order.

    Args:
        document_text: e.g. the handbook.
    Returns:
        e.g. 93 sentences.
    """
    log.debug("start: %d characters", len(document_text))
    sentences: list[str] = []
    for paragraph in find_paragraphs(document_text):
        sentences.extend(re.split(SENTENCE_END_REGEX, paragraph))
    log.debug("result: %d sentences", len(sentences))
    return sentences


@debug
def similarity_to_next(sentence_vectors: npt.NDArray[np.float64]) -> list[float]:
    """How alike each sentence is to the one after it: low = the topic changes here.

    Args:
        sentence_vectors: one row per sentence, e.g. shape (93, 768).
    Returns:
        One number per pair in a row, e.g. 92 numbers like 0.71; nomic vectors have length 1, so dot = cosine (2.5).
    """
    log.debug("start: %d sentences", len(sentence_vectors))
    similarities: list[float] = []
    for row_number in range(len(sentence_vectors) - 1):
        similarity = float(sentence_vectors[row_number] @ sentence_vectors[row_number + 1])
        similarities.append(similarity)
    log.debug("result: lowest %.3f, highest %.3f", min(similarities), max(similarities))
    return similarities


@debug
def cut_where_topic_changes(sentences: list[str], similarities: list[float], cut_below: float,
                            max_characters: int) -> list[str]:
    """Start a new chunk where two sentences in a row are less alike than cut_below, or the chunk is full.

    Args:
        sentences: e.g. list_sentences(handbook).
        similarities: similarity_to_next(...), one fewer than sentences.
        cut_below: e.g. 0.55.
        max_characters: e.g. 500.
    Returns:
        e.g. 17 chunks.
    """
    log.debug("start: %d sentences, cut below %.3f", len(sentences), cut_below)
    chunks: list[str] = []
    current_chunk = sentences[0]
    for sentence_number in range(1, len(sentences)):
        joined_chunk = current_chunk + " " + sentences[sentence_number]
        is_new_topic = similarities[sentence_number - 1] < cut_below
        if is_new_topic or len(joined_chunk) > max_characters:
            chunks.append(current_chunk)
            current_chunk = sentences[sentence_number]
        else:
            current_chunk = joined_chunk
    chunks.append(current_chunk)
    log.debug("result: %d chunks", len(chunks))
    return chunks


if __name__ == "__main__":
    handbook_text = HANDBOOK_PATH.read_text(encoding="utf-8")
    handbook_sentences = list_sentences(handbook_text)
    embed_start = time.perf_counter()
    handbook_sentence_vectors = embed_texts(handbook_sentences)
    sentence_embed_seconds = time.perf_counter() - embed_start
    handbook_similarities = similarity_to_next(handbook_sentence_vectors)

    print(f"1. the {LOWEST_SHOWN} least alike pairs of sentences in a row (of {len(handbook_similarities)}):")
    lowest_first_rows = np.argsort(handbook_similarities, kind="stable")[:LOWEST_SHOWN]
    for pair_row in lowest_first_rows:
        pair_number = int(pair_row)
        print(f"   {handbook_similarities[pair_number]:.3f}  {handbook_sentences[pair_number][-35:]!r} | "
              f"{handbook_sentences[pair_number + 1][:35]!r}")

    question_texts: list[str] = []
    for eval_question in EVAL_QUESTIONS:
        question_texts.append(eval_question.question)
    all_question_vectors = embed_texts(question_texts)
    print(f"\n2. search score, max {MAX_CHARACTERS} characters:")
    for cut_percent in CUT_PERCENTS:
        cut_below = float(np.percentile(handbook_similarities, cut_percent))  # the value cut_percent % are under
        meaning_chunks = cut_where_topic_changes(handbook_sentences, handbook_similarities, cut_below,
                                                 MAX_CHARACTERS)
        meaning_score = score_search(meaning_chunks, all_question_vectors)
        print(f"   {format_score(f'meaning, lowest {cut_percent}% (< {cut_below:.3f})', meaning_score)}")
    paragraph_chunks = cut_at_paragraphs(handbook_text, MAX_CHARACTERS, True)
    paragraph_score = score_search(paragraph_chunks, all_question_vectors)
    print(f"   {format_score('paragraphs + headings', paragraph_score)}")

    embed_start = time.perf_counter()
    embed_texts(paragraph_chunks)
    chunk_embed_seconds = time.perf_counter() - embed_start
    print(f"\n3. cost: embed {len(handbook_sentences)} sentences {sentence_embed_seconds:.1f} s, "
          f"then the chunks again; paragraphs: embed {len(paragraph_chunks)} chunks {chunk_embed_seconds:.1f} s")
