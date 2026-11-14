"""Part 2 of 2: answer 12 questions three ways. Needs Ollama + qwen3:1.7b + nomic-embed-text.

Run (~3 min):
  uv run python 04_rag/4_1_rag_by_hand/examples_4_1_2_answer.py

  5. alone : the model with no documents
  6. RAG   : the 3 best chunks in the prompt (chunks by heading, part 1)
  7. whole : all documents in the prompt, default context 4096 (2 questions only: slow)
"""

import time  # time.perf_counter() = a stopwatch
from dataclasses import dataclass

import httpx

from examples_4_1_1_search import Matrix, chunk_by_headings, embed_texts, load_documents, top_rows_by_score
from lab_tools.log import cut_text, debug, log

OLLAMA_URL = "http://127.0.0.1:11434"
CHAT_MODEL = "qwen3:1.7b"
BASE_RULES = "You are the support assistant for Lumen Notes. Answer in 1 to 2 sentences."
RAG_RULES = BASE_RULES + " Use only the text below. If the text does not say, answer: I don't know.\n\n"
CHUNK_SEPARATOR = "\n\n---\n\n"
TOP_K = 3


@dataclass
class EvalQuestion:
    """A question with the words a right answer must contain."""

    question: str
    expected_words: str  # e.g. "15 minutes"; checked in lower case, "-" read as a space


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
    EvalQuestion("In which app version did dark mode arrive?", "7.4.0"),
    EvalQuestion("Since which version can I search my notes without internet?", "8.3.0"),
    EvalQuestion("From which version is Windows 10 required?", "9.1.0"),
]


@dataclass
class ModelAnswer:
    """The model's answer and how many prompt tokens it really read."""

    text: str
    prompt_tokens: int  # Ollama's prompt_eval_count: the real count, after any cut


@debug
def ask_model(system_text: str, question: str) -> ModelAnswer:
    """Ask the chat model one question with the given system text (default context 4096).

    Args:
        system_text: the rules, maybe followed by document text.
        question: e.g. "How long does the password reset link work?".
    Returns:
        e.g. ModelAnswer(text="The link expires after 15 minutes.", prompt_tokens=310).
    """
    chat_messages = [{"role": "system", "content": system_text}, {"role": "user", "content": question}]
    request_body = {"model": CHAT_MODEL, "messages": chat_messages, "stream": False, "think": False,
                    "options": {"temperature": 0, "seed": 42, "num_predict": 200}}
    response = httpx.post(f"{OLLAMA_URL}/api/chat", json=request_body, timeout=900.0)
    response.raise_for_status()
    reply_json = response.json()
    model_answer = ModelAnswer(text=reply_json["message"]["content"], prompt_tokens=reply_json["prompt_eval_count"])
    log.debug("result: %d prompt tokens, %s", model_answer.prompt_tokens, cut_text(model_answer.text))
    return model_answer


def is_right(answer_text: str, expected_words: str) -> bool:
    """Check the answer contains the expected words (lower case, "-" read as a space: "15-minute").

    Args:
        answer_text: e.g. "The reset link expires after 15 minutes.".
        expected_words: e.g. "15 minutes".
    Returns:
        e.g. True.
    """
    cleaned_answer = answer_text.lower().replace("-", " ")
    answer_is_right = expected_words in cleaned_answer
    return answer_is_right


@debug
def build_rag_system_text(question: str, chunk_texts: list[str], chunk_vectors: Matrix) -> str:
    """Find the TOP_K best chunks for the question and put them under the rules.

    Args:
        question: e.g. "Can I get my money back?".
        chunk_texts: all chunks.
        chunk_vectors: their vectors, same order.
    Returns:
        RAG_RULES + the chunks, joined by CHUNK_SEPARATOR.
    """
    question_vectors = embed_texts([question])
    top_rows = top_rows_by_score(question_vectors[0], chunk_vectors, TOP_K)
    top_chunk_texts: list[str] = []
    for row_number in top_rows:
        top_chunk_texts.append(chunk_texts[row_number])
    system_text = RAG_RULES + CHUNK_SEPARATOR.join(top_chunk_texts)
    return system_text


def run_and_score(label: str, eval_questions: list[EvalQuestion], system_text_for: dict[str, str]) -> None:
    """Ask every question with its system text; print misses, then right / total, time and tokens.

    Args:
        label: e.g. "6. RAG".
        eval_questions: the questions to ask.
        system_text_for: question -> the system text to send with it.
    """
    right_count = 0
    prompt_token_counts: list[int] = []
    start = time.perf_counter()
    for eval_question in eval_questions:
        model_answer = ask_model(system_text_for[eval_question.question], eval_question.question)
        prompt_token_counts.append(model_answer.prompt_tokens)
        if is_right(model_answer.text, eval_question.expected_words):
            right_count += 1
        else:
            print(f"   miss: {eval_question.question[:45]} -> {model_answer.text[:80]!r}")
    elapsed_seconds = time.perf_counter() - start
    print(f"{label}: {right_count}/{len(eval_questions)} right, {elapsed_seconds:.1f} s, "
          f"prompt tokens {min(prompt_token_counts)}-{max(prompt_token_counts)}\n")


if __name__ == "__main__":
    all_text = load_documents()
    heading_chunks = chunk_by_headings(all_text)
    heading_vectors = embed_texts(heading_chunks)
    alone_texts: dict[str, str] = {}
    rag_texts: dict[str, str] = {}
    whole_texts: dict[str, str] = {}
    for eval_question in EVAL_QUESTIONS:
        alone_texts[eval_question.question] = BASE_RULES
        rag_texts[eval_question.question] = build_rag_system_text(eval_question.question, heading_chunks,
                                                                  heading_vectors)
        whole_texts[eval_question.question] = RAG_RULES + all_text
    run_and_score("5. alone", EVAL_QUESTIONS, alone_texts)
    run_and_score("6. RAG", EVAL_QUESTIONS, rag_texts)
    run_and_score("7. whole (first 2 questions)", EVAL_QUESTIONS[:2], whole_texts)
