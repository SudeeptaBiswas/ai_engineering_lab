"""Part 3 of 3: answer 12 questions three ways. Needs Ollama + qwen3:1.7b + nomic-embed-text.

Run (~3 min):
  uv run python 04_rag/4_1_rag_by_hand/examples_4_1_3_answer.py

  5. alone : the model with no documents
  6. RAG   : the 3 best chunks in the prompt (chunks by heading, part 1)
  7. whole : all documents in the prompt, default context 4096 (2 questions only: slow)
"""

import time  # time.perf_counter() = a stopwatch
from dataclasses import dataclass

import httpx

from examples_4_1_1_search import TOP_K, EmbeddingMatrix, chunk_by_headings, embed_texts, load_documents
from examples_4_1_1_search import find_top_rows
from lab_tools.log import cut_text, debug, log

OLLAMA_URL = "http://127.0.0.1:11434"
CHAT_MODEL = "qwen3:1.7b"
ALONE_SYSTEM_PROMPT = "You are the support assistant for Lumen Notes. Answer in 1 to 2 sentences."
RAG_SYSTEM_PROMPT = ALONE_SYSTEM_PROMPT + " Use only the text below. If the text does not say, answer: I don't know.\n\n"
CHUNK_SEPARATOR = "\n\n---\n\n"  # between chunks in the prompt, so the model sees where one ends


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

    answer_text: str  # e.g. "The link expires after 15 minutes."
    prompt_tokens: int  # Ollama's prompt_eval_count: the real count, after any cut


@dataclass
class ScoreReport:
    """How one way of asking did on a list of questions."""

    right_count: int  # e.g. 11
    question_count: int  # e.g. 12
    total_seconds: float  # time for all questions together
    prompt_token_counts: list[int]  # one per question
    missed_answers: list[str]  # "question -> answer" for each wrong one


@debug
def ask_model(system_prompt: str, question: str) -> ModelAnswer:
    """Ask the chat model one question with the given system prompt (default context 4096).

    Args:
        system_prompt: the rules, maybe followed by document text.
        question: e.g. "How long does the password reset link work?".
    Returns:
        e.g. ModelAnswer(answer_text="The link expires after 15 minutes.", prompt_tokens=310).
    """
    log.debug("start: question=%r system_prompt=%s", question, cut_text(system_prompt))
    system_message = {"role": "system", "content": system_prompt}
    user_message = {"role": "user", "content": question}
    model_options = {"temperature": 0, "seed": 42, "num_predict": 200}  # same answer every run, max 200 tokens
    request_body = {"model": CHAT_MODEL, "messages": [system_message, user_message], "stream": False,
                    "think": False, "options": model_options}
    response = httpx.post(f"{OLLAMA_URL}/api/chat", json=request_body, timeout=900.0)
    response.raise_for_status()
    reply_json = response.json()
    answer_text = reply_json["message"]["content"]  # the model's reply, as text
    prompt_tokens = reply_json["prompt_eval_count"]  # tokens the model really read
    model_answer = ModelAnswer(answer_text=answer_text, prompt_tokens=prompt_tokens)
    log.debug("result: %d prompt tokens, %s", model_answer.prompt_tokens, cut_text(model_answer.answer_text))
    return model_answer


@debug
def answer_has_expected_words(answer_text: str, expected_words: str) -> bool:
    """Check the answer contains the expected words (lower case, "-" read as a space: "15-minute").

    Args:
        answer_text: e.g. "The reset link expires after 15 minutes.".
        expected_words: e.g. "15 minutes".
    Returns:
        e.g. True.
    """
    cleaned_answer = answer_text.lower().replace("-", " ")  # "15-Minute" -> "15 minute"
    is_right = expected_words in cleaned_answer
    log.debug("expected=%r got=%s is_right=%s", expected_words, cut_text(cleaned_answer), is_right)
    return is_right


@debug
def build_rag_system_prompt(question: str, chunk_texts: list[str], chunk_vectors: EmbeddingMatrix) -> str:
    """Find the TOP_K best chunks for the question and put them under the rules.

    How:
        1. Embed the question.
        2. Find the best rows (find_top_rows) and take those chunk texts.
        3. Rules + the chunks, joined by CHUNK_SEPARATOR.
    Args:
        question: e.g. "Can I get my money back?".
        chunk_texts: all chunks.
        chunk_vectors: their vectors, same order.
    Returns:
        RAG_SYSTEM_PROMPT + the chunks, joined by CHUNK_SEPARATOR.
    """
    log.debug("start: question=%r", question)
    question_vectors = embed_texts([question])
    question_vector = question_vectors[0]  # [0] = the only row
    top_rows = find_top_rows(question_vector, chunk_vectors, TOP_K)
    top_chunk_texts: list[str] = []
    for row_number in top_rows:
        top_chunk_texts.append(chunk_texts[row_number])
    system_prompt = RAG_SYSTEM_PROMPT + CHUNK_SEPARATOR.join(top_chunk_texts)
    log.debug("result: %d characters", len(system_prompt))
    return system_prompt


@debug
def score_answers(eval_questions: list[EvalQuestion], system_prompt_by_question: dict[str, str]) -> ScoreReport:
    """Ask every question with its own system prompt and count the right answers.

    How:
        1. Ask the model each question; keep its prompt token count.
        2. Check the answer has the expected words; keep the wrong ones.
        3. Time the whole run.
    Args:
        eval_questions: the questions to ask.
        system_prompt_by_question: question -> the system prompt to send with it.
    Returns:
        e.g. ScoreReport(right_count=11, question_count=12, total_seconds=55.0, ...).
    """
    log.debug("start: %d questions", len(eval_questions))
    score_report = ScoreReport(right_count=0, question_count=len(eval_questions), total_seconds=0.0,
                               prompt_token_counts=[], missed_answers=[])
    start = time.perf_counter()
    for eval_question in eval_questions:
        system_prompt = system_prompt_by_question[eval_question.question]
        model_answer = ask_model(system_prompt, eval_question.question)
        score_report.prompt_token_counts.append(model_answer.prompt_tokens)
        is_right = answer_has_expected_words(model_answer.answer_text, eval_question.expected_words)
        if is_right:
            score_report.right_count += 1
        else:
            short_question = eval_question.question[:45]  # first 45 characters, so a miss fits one line
            short_answer = model_answer.answer_text[:80]  # first 80 characters
            score_report.missed_answers.append(f"{short_question} -> {short_answer!r}")  # !r adds quotes
    score_report.total_seconds = time.perf_counter() - start
    log.debug("result: %d/%d right", score_report.right_count, score_report.question_count)
    return score_report


@debug
def print_report(heading: str, score_report: ScoreReport) -> None:
    """Print the misses, then right / total, time and the prompt token range.

    Args:
        heading: e.g. "6. RAG".
        score_report: from score_answers.
    """
    log.debug("start: %s, %d misses", heading, len(score_report.missed_answers))
    for missed_answer in score_report.missed_answers:
        print(f"   miss: {missed_answer}")
    fewest_tokens = min(score_report.prompt_token_counts)
    most_tokens = max(score_report.prompt_token_counts)
    print(f"{heading}: {score_report.right_count}/{score_report.question_count} right, "
          f"{score_report.total_seconds:.1f} s, prompt tokens {fewest_tokens}-{most_tokens}\n")


if __name__ == "__main__":
    documents_text = load_documents()
    heading_chunks = chunk_by_headings(documents_text)
    heading_vectors = embed_texts(heading_chunks)
    alone_system_prompts: dict[str, str] = {}
    rag_system_prompts: dict[str, str] = {}
    whole_system_prompts: dict[str, str] = {}
    for eval_question in EVAL_QUESTIONS:
        question = eval_question.question
        alone_system_prompts[question] = ALONE_SYSTEM_PROMPT
        rag_system_prompts[question] = build_rag_system_prompt(question, heading_chunks, heading_vectors)
        whole_system_prompts[question] = RAG_SYSTEM_PROMPT + documents_text
    alone_report = score_answers(EVAL_QUESTIONS, alone_system_prompts)
    print_report("5. alone", alone_report)
    rag_report = score_answers(EVAL_QUESTIONS, rag_system_prompts)
    print_report("6. RAG", rag_report)
    whole_report = score_answers(EVAL_QUESTIONS[:2], whole_system_prompts)  # only 2: each takes ~30 s
    print_report("7. whole (first 2 questions)", whole_report)
