"""Part 2 of 3: is Chroma's search as good as 4.1's numpy search? Filters, distances, changes. Needs Ollama.

Run (~16 s):
  uv run python 04_rag/4_4_chroma/examples_4_4_2_search.py

  1. score  : the 12 questions of 4.3, Chroma vs numpy (table @ vector, 4.1)
  2. space  : the same search measured by "l2" (Chroma's default) instead of "cosine"
  3. filter : one vague question, without and with where={"heading": ...}
  4. change : add() with an id that exists vs update(): which one changes the text?
"""

from dataclasses import dataclass

import chromadb
import numpy as np
from chromadb.base_types import Where

from chroma_store_4_4 import NO_TELEMETRY, open_collection
from examples_4_4_1_store import SAMPLE_QUESTION, TOP_K, ask_collection, store_new_chunks
from handbook_4_4 import EVAL_QUESTIONS, HandbookChunk, embed_texts, load_handbook_chunks
from lab_tools.log import debug, log

VAGUE_QUESTION = "How long is the link valid?"  # which link? password reset, export, shared note...
FILTER_HEADING = "Export and import"
CHANGED_REFUND_TEXT = "Refunds\n\nYou can ask for a full refund within 30 days of a payment."
SHOWN_CHARACTERS = 60  # how much of the changed chunk to print


@dataclass
class ChromaScore:
    """How Chroma's search did on the 12 questions."""

    right_first: int  # best chunk holds the answer sentence, e.g. 12
    right_in_top: int  # top 3 hold it, e.g. 12
    same_as_numpy: int  # same 3 ids in the same order as 4.1's numpy search, e.g. 12


@debug
def numpy_top_ids(chunks: list[HandbookChunk], chunk_vectors: list[list[float]], question_vector: list[float],
                  top_k: int) -> list[str]:
    """4.1's search, for comparison: score every chunk with one table @ vector, keep the best ids.

    Args:
        chunks: e.g. load_handbook_chunks().
        chunk_vectors: embed_texts of their texts, same order.
        question_vector: e.g. embed_texts(["How long ..."])[0].
        top_k: e.g. 3.
    Returns:
        e.g. ["refunds-0", "billing-and-invoices-1", "billing-and-invoices-0"].
    """
    log.debug("start: %d chunks, top_k=%d", len(chunks), top_k)
    scores = np.array(chunk_vectors) @ np.array(question_vector)  # one similarity per chunk
    best_rows = np.argsort(-scores, kind="stable")[:top_k]  # row numbers, best first
    top_ids: list[str] = []
    for row_number in best_rows:
        top_ids.append(chunks[int(row_number)].chunk_id)
    log.debug("result: %s", top_ids)
    return top_ids


@debug
def score_chroma_against_numpy(collection: chromadb.Collection, chunks: list[HandbookChunk],
                               chunk_vectors: list[list[float]]) -> ChromaScore:
    """Ask the 12 questions both ways: does Chroma find the answer, and the same top 3 as numpy?

    How:
        1. Embed the 12 questions once.
        2. Per question: Chroma's top 3 (ask_collection) and numpy's top 3.
        3. Count: answer sentence in Chroma's best chunk; in its top 3; same ids, same order.
    Args:
        collection: holds the 18 chunks, measured by cosine.
        chunks: the same 18 chunks.
        chunk_vectors: their vectors, same order.
    Returns:
        e.g. ChromaScore(right_first=12, right_in_top=12, same_as_numpy=12).
    """
    log.debug("start: %d chunks", len(chunks))
    question_texts: list[str] = []
    for eval_question in EVAL_QUESTIONS:
        question_texts.append(eval_question.question)
    question_vectors = embed_texts(question_texts)
    right_first = 0
    right_in_top = 0
    same_as_numpy = 0
    for question_number in range(len(EVAL_QUESTIONS)):
        answer_sentence = EVAL_QUESTIONS[question_number].answer_sentence
        chroma_hits = ask_collection(collection, question_vectors[question_number], TOP_K, None)
        chroma_ids: list[str] = []
        found_in_hits: list[bool] = []
        for chroma_hit in chroma_hits:
            chroma_ids.append(chroma_hit.chunk_id)
            found_in_hits.append(answer_sentence in chroma_hit.chunk_text)
        numpy_ids = numpy_top_ids(chunks, chunk_vectors, question_vectors[question_number], TOP_K)
        log.debug("question %d: expected numpy %s got chroma %s", question_number + 1, numpy_ids, chroma_ids)
        if found_in_hits[0]:  # the best chunk holds it
            right_first += 1
        if True in found_in_hits:
            right_in_top += 1
        if chroma_ids == numpy_ids:
            same_as_numpy += 1
    chroma_score = ChromaScore(right_first, right_in_top, same_as_numpy)
    log.debug("result: %s", chroma_score)
    return chroma_score


if __name__ == "__main__":
    handbook_chunks = load_handbook_chunks()
    chunk_texts: list[str] = []
    for handbook_chunk in handbook_chunks:
        chunk_texts.append(handbook_chunk.text)
    handbook_vectors = embed_texts(chunk_texts)
    memory_client = chromadb.EphemeralClient(settings=NO_TELEMETRY)  # memory only: gone when the script ends
    cosine_collection = open_collection(memory_client, "handbook-cosine")
    store_new_chunks(cosine_collection, handbook_chunks, embed_texts)  # same texts -> same vectors as above

    print("1. score: 12 questions")
    chroma_score = score_chroma_against_numpy(cosine_collection, handbook_chunks, handbook_vectors)
    print(f"   right 1st {chroma_score.right_first}/12, in top {TOP_K} {chroma_score.right_in_top}/12, "
          f"same top {TOP_K} as numpy {chroma_score.same_as_numpy}/12")

    print('\n2. space: "cosine" vs "l2", best 3 for the refund question')
    l2_collection = memory_client.get_or_create_collection("handbook-l2")  # no configuration = Chroma's default
    store_new_chunks(l2_collection, handbook_chunks, embed_texts)
    refund_vector = embed_texts([SAMPLE_QUESTION])[0]  # "I paid three weeks ago. Can I still get a refund?"
    collections_by_space = {"cosine": cosine_collection, "l2": l2_collection}
    for space_name in collections_by_space:
        space_answers = collections_by_space[space_name].query(query_embeddings=[refund_vector], n_results=TOP_K)
        space_distances = space_answers["distances"] or [[]]  # None only if left out of include
        rounded_distances: list[float] = []
        for distance in space_distances[0]:
            rounded_distances.append(round(distance, 3))
        print(f"   {space_name:6}  {space_answers['ids'][0]}  {rounded_distances}")
        # concise: [round(distance, 3) for distance in space_distances[0]]

    print(f"\n3. filter: {VAGUE_QUESTION!r}")
    vague_vector = embed_texts([VAGUE_QUESTION])[0]
    where_filters: list[Where | None] = [None, {"heading": FILTER_HEADING}]
    for where_filter in where_filters:
        print(f"   where={where_filter}")
        for search_hit in ask_collection(cosine_collection, vague_vector, TOP_K, where_filter):
            print(f"     {search_hit.similarity:.3f}  {search_hit.chunk_id}")

    print("\n4. change: the refund window goes from 14 to 30 days")
    changed_vectors = embed_texts([CHANGED_REFUND_TEXT])
    cosine_collection.add(ids=["refunds-0"], embeddings=np.array(changed_vectors, dtype=np.float32),
                          documents=[CHANGED_REFUND_TEXT])
    rows_after_add = cosine_collection.get(ids=["refunds-0"])
    texts_after_add = rows_after_add["documents"] or [""]  # None only if left out of include
    paragraph_after_add = texts_after_add[0].split("\n\n")[1]  # [1] = the paragraph after the heading
    print(f"   add()    same id: {cosine_collection.count()} chunks, "
          f"text {paragraph_after_add[:SHOWN_CHARACTERS]!r}")
    cosine_collection.update(ids=["refunds-0"], embeddings=np.array(changed_vectors, dtype=np.float32),
                             documents=[CHANGED_REFUND_TEXT])
    rows_after_update = cosine_collection.get(ids=["refunds-0"])
    texts_after_update = rows_after_update["documents"] or [""]
    paragraph_after_update = texts_after_update[0].split("\n\n")[1]
    print(f"   update() same id: {cosine_collection.count()} chunks, "
          f"text {paragraph_after_update[:SHOWN_CHARACTERS]!r}")
