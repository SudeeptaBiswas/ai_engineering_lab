"""Part 2 of 3: how fast is numpy search vs a Python loop? No Ollama needed.

Run (~3 s):
  uv run python 04_rag/4_1_rag_by_hand/examples_4_1_2_speed.py

  4. speed : the same scores two ways, on 122 and 20 000 random chunks
"""

import time  # time.perf_counter() = a stopwatch
from dataclasses import dataclass

import numpy as np

from examples_4_1_1_search import EmbeddingMatrix
from lab_tools.log import debug, log

VECTOR_SIZE = 768  # numbers per vector, same as nomic-embed-text
CHUNK_COUNTS = [122, 20000]  # 122 = our real chunks; 20 000 = a big document set


@dataclass
class SearchTimes:
    """How long one search took, both ways, in milliseconds."""

    numpy_milliseconds: float  # e.g. 0.3
    loop_milliseconds: float  # e.g. 8.0


@debug
def make_random_unit_vectors(chunk_count: int) -> EmbeddingMatrix:
    """Make stand-in chunk vectors with length 1, like nomic's, so no Ollama is needed.

    How:
        1. Random numbers, chunk_count rows x VECTOR_SIZE columns.
        2. Divide each row by its length, so every row has length 1.
    Args:
        chunk_count: e.g. 122.
    Returns:
        A matrix of shape (chunk_count, 768).
    """
    log.debug("start: chunk_count=%d", chunk_count)
    random_generator = np.random.default_rng(42)  # seed 42: same numbers every run
    random_vectors = random_generator.normal(size=(chunk_count, VECTOR_SIZE))
    vector_lengths = np.linalg.norm(random_vectors, axis=1, keepdims=True)  # one length per row
    unit_vectors = random_vectors / vector_lengths  # each row now has length 1
    log.debug("result: shape %s", unit_vectors.shape)
    return unit_vectors


@debug
def score_with_python_loop(question_vector: list[float], chunk_vectors: list[list[float]]) -> list[float]:
    """The same scores without numpy: a dot product per chunk, written as loops (2.5).

    Args:
        question_vector: 768 numbers.
        chunk_vectors: one list of 768 numbers per chunk.
    Returns:
        One score per chunk.
    """
    log.debug("start: %d chunks", len(chunk_vectors))
    scores: list[float] = []
    for chunk_vector in chunk_vectors:
        total = 0.0
        for position in range(len(question_vector)):
            total += question_vector[position] * chunk_vector[position]
        scores.append(total)
    log.debug("result: %d scores", len(scores))
    return scores


@debug
def time_numpy_and_loop(chunk_vectors: EmbeddingMatrix) -> SearchTimes:
    """Measure how long scoring every chunk takes with numpy and with the Python loop.

    Only the scoring is timed, both ways: no sort, no list conversion.
    (The loop function's 2 log lines run once each: tiny next to its 6+ ms.)
    How:
        1. Use the first chunk as the question; turn the vectors into lists for the loop.
        2. Time numpy: chunk_vectors @ question_vector.
        3. Time the loop: score_with_python_loop.
        4. Check both gave the same scores.
    Args:
        chunk_vectors: e.g. make_random_unit_vectors(122).
    Returns:
        e.g. SearchTimes(numpy_milliseconds=0.1, loop_milliseconds=6.0).
    """
    log.debug("start: %d chunks", chunk_vectors.shape[0])
    question_vector = chunk_vectors[0]
    question_list = question_vector.tolist()  # numpy -> plain Python lists, before the stopwatch
    chunk_lists = chunk_vectors.tolist()
    warm_up_scores = chunk_vectors @ question_vector  # first call loads numpy's math code: measured 12.6 ms once
    log.debug("warm-up done: %d scores", len(warm_up_scores))
    start = time.perf_counter()
    numpy_scores = chunk_vectors @ question_vector  # one dot product per row, in one step
    numpy_milliseconds = (time.perf_counter() - start) * 1000  # seconds -> ms
    start = time.perf_counter()
    loop_scores = score_with_python_loop(question_list, chunk_lists)
    loop_milliseconds = (time.perf_counter() - start) * 1000
    same_scores = bool(np.allclose(numpy_scores, loop_scores))  # equal up to rounding
    log.debug("expected=same scores got same_scores=%s", same_scores)
    search_times = SearchTimes(numpy_milliseconds=numpy_milliseconds, loop_milliseconds=loop_milliseconds)
    log.debug("result: %s", search_times)
    return search_times


if __name__ == "__main__":
    print("4. speed:")
    for chunk_count in CHUNK_COUNTS:
        chunk_vectors = make_random_unit_vectors(chunk_count)
        search_times = time_numpy_and_loop(chunk_vectors)
        print(f"  {chunk_count:>6} chunks: numpy {search_times.numpy_milliseconds:.3f} ms, "
              f"Python loop {search_times.loop_milliseconds:.0f} ms")
