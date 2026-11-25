"""Part 3 of 3: compare two embedding models on the same 12 questions. Needs Ollama + nomic-embed-text.

Run (~15 s; the FIRST run also downloads Chroma's built-in model, 79 MB, ~2 min):
  uv run python 04_rag/4_4_chroma/examples_4_4_3_models.py

  1. models : nomic-embed-text (Ollama, 768 numbers) vs all-MiniLM-L6-v2 (Chroma's own, 384)
  2. easy   : let Chroma embed for you: add(documents=...) and query(query_texts=...)
  3. trap   : query_texts on a collection filled with nomic vectors
  4. limit  : how much of a long text each model reads; the rest is dropped
"""

import time  # time.perf_counter() = a stopwatch
from dataclasses import dataclass

import chromadb
import numpy as np
from chromadb.api import ClientAPI
from chromadb.errors import InvalidArgumentError
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from chroma_store_4_4 import NO_TELEMETRY, EmbedFunction, open_collection
from examples_4_4_1_store import SAMPLE_QUESTION, TOP_K, ask_collection, store_new_chunks
from handbook_4_4 import EVAL_QUESTIONS, HandbookChunk, embed_texts, load_handbook_chunks
from lab_tools.log import debug, log

BUILT_IN_MODEL = DefaultEmbeddingFunction()  # all-MiniLM-L6-v2, runs inside Python (onnxruntime), no Ollama
NOMIC_COLLECTION_NAME = "handbook-nomic-embed-text"  # made in section 1, used again in section 3


@dataclass
class ModelScore:
    """How one embedding model did on the 12 questions."""

    vector_length: int  # numbers per text, e.g. 768
    embed_seconds: float  # 18 chunks + 12 questions, model already loaded, e.g. 1.2
    right_first: int  # best chunk holds the answer sentence, e.g. 12
    right_in_top: int  # top 3 hold it, e.g. 12


@debug
def embed_with_built_in_model(texts: list[str]) -> list[list[float]]:
    """Chroma's own model, with the same shape as embed_texts: one plain list per text.

    Args:
        texts: e.g. 18 chunks.
    Returns:
        One list of 384 numbers per text, each of length 1.0.
    """
    log.debug("start: %d texts", len(texts))
    numpy_vectors = BUILT_IN_MODEL(texts)  # one numpy array per text
    vectors: list[list[float]] = []
    for numpy_vector in numpy_vectors:
        vectors.append(numpy_vector.tolist())  # numpy array -> plain list of floats
    log.debug("result: %d vectors", len(vectors))
    return vectors


@debug
def score_model(client: ClientAPI, collection_name: str, chunks: list[HandbookChunk],
                embed_function: EmbedFunction) -> ModelScore:
    """Store the chunks with one model, ask the 12 questions with the same model, count the right ones.

    How:
        1. Warm up: one embed call, so loading the model is not counted.
        2. Store the chunks (embeds 18) and embed the 12 questions: timed.
        3. Per question: is the answer sentence in the best chunk? In the top 3?
    Args:
        client: e.g. chromadb.EphemeralClient(settings=NO_TELEMETRY).
        collection_name: one per model, e.g. "handbook-minilm".
        chunks: e.g. load_handbook_chunks().
        embed_function: embed_texts or embed_with_built_in_model.
    Returns:
        e.g. ModelScore(vector_length=768, embed_seconds=1.2, right_first=12, right_in_top=12).
    """
    log.debug("start: %s", collection_name)
    warm_up_vectors = embed_function(["warm up"])
    collection = open_collection(client, collection_name)
    start_seconds = time.perf_counter()
    store_new_chunks(collection, chunks, embed_function)
    question_texts: list[str] = []
    for eval_question in EVAL_QUESTIONS:
        question_texts.append(eval_question.question)
    question_vectors = embed_function(question_texts)
    embed_seconds = time.perf_counter() - start_seconds
    right_first = 0
    right_in_top = 0
    for question_number in range(len(EVAL_QUESTIONS)):
        answer_sentence = EVAL_QUESTIONS[question_number].answer_sentence
        found_in_hits: list[bool] = []
        for search_hit in ask_collection(collection, question_vectors[question_number], TOP_K, None):
            found_in_hits.append(answer_sentence in search_hit.chunk_text)
        log.debug("question %d: expected the answer in the top %d got %s", question_number + 1, TOP_K,
                  found_in_hits)
        if found_in_hits[0]:  # the best chunk holds it
            right_first += 1
        if True in found_in_hits:
            right_in_top += 1
    model_score = ModelScore(len(warm_up_vectors[0]), embed_seconds, right_first, right_in_top)
    log.debug("result: %s", model_score)
    return model_score


if __name__ == "__main__":
    handbook_chunks = load_handbook_chunks()
    memory_client = chromadb.EphemeralClient(settings=NO_TELEMETRY)

    print("1. models: same 18 chunks, same 12 questions")
    models_to_compare = {"nomic-embed-text": embed_texts, "all-MiniLM-L6-v2": embed_with_built_in_model}
    for model_name in models_to_compare:
        collection_name = f"handbook-{model_name}".lower()  # e.g. NOMIC_COLLECTION_NAME
        model_score = score_model(memory_client, collection_name, handbook_chunks, models_to_compare[model_name])
        print(f"   {model_name:17} {model_score.vector_length} numbers | {model_score.embed_seconds:.2f} s | "
              f"right 1st {model_score.right_first}/12, in top {TOP_K} {model_score.right_in_top}/12")

    print("\n2. easy: no vectors given, Chroma embeds with its built-in model")
    easy_collection = open_collection(memory_client, "handbook-easy")
    easy_ids: list[str] = []
    easy_texts: list[str] = []
    for handbook_chunk in handbook_chunks:
        easy_ids.append(handbook_chunk.chunk_id)
        easy_texts.append(handbook_chunk.text)
    easy_collection.add(ids=easy_ids, documents=easy_texts)  # no embeddings=...: Chroma makes them
    easy_answers = easy_collection.query(query_texts=[SAMPLE_QUESTION], n_results=TOP_K)
    print(f"   {SAMPLE_QUESTION!r} -> {easy_answers['ids'][0]}")

    print("\n3. trap: query_texts on the collection that holds nomic vectors")
    nomic_collection = open_collection(memory_client, NOMIC_COLLECTION_NAME)
    try:
        nomic_collection.query(query_texts=[SAMPLE_QUESTION], n_results=TOP_K)
    except InvalidArgumentError as error:  # Chroma embedded the question with MiniLM
        print(f"   {type(error).__name__}: {error}")

    print("\n4. limit: an answer at the END of a long text. Is it still in the vector?")
    filler_text = "\n\n".join(easy_texts[:8])  # the first 8 chunks glued: intro to billing, no refund rule
    refund_chunk_text = ""
    for handbook_chunk in handbook_chunks:
        if handbook_chunk.chunk_id == "refunds-0":
            refund_chunk_text = handbook_chunk.text
    long_text_with_refund = f"{filler_text}\n\n{refund_chunk_text}"
    print(f"   {len(filler_text)} characters, then the refund chunk ({len(refund_chunk_text)}) at the end")
    for model_name in models_to_compare:
        embed_function = models_to_compare[model_name]
        question_vector = np.array(embed_function([SAMPLE_QUESTION])[0])
        filler_vector = np.array(embed_function([filler_text])[0])
        long_text_vector = np.array(embed_function([long_text_with_refund])[0])
        similarity_without = float(filler_vector @ question_vector)  # refund question vs the filler alone
        similarity_with = float(long_text_vector @ question_vector)  # ... vs filler + refund chunk
        print(f"   {model_name:17} refund question vs text: without the refund part {similarity_without:.3f}, "
              f"with it {similarity_with:.3f}")