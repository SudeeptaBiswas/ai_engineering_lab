"""One chat turn: the user's question in, the model's final answer out (v2: with tools).

The tool loop (lesson 3.3), with the gate (lesson 3.4):
  send messages -> reply has tool calls? -> gate each call -> run it or block it
  -> send the results back -> ask again ... until a reply has no tool calls.
Then the final answer is checked (answer_check.py): no refund claims
without a refund that really ran.

Only the question and the final answer go into memory. Tool messages live
in this turn only: trimming could otherwise keep a tool result but drop the
call that asked for it.

Tests: 02_llm_fundamentals/2_6_assistant_v1/exercises_2_6_3_cli.py (plain turns)
       03_prompting_tools/3_5_assistant_v2/test_3_5_4_turn.py (tool rounds)
"""

from dataclasses import dataclass, field
from typing import Any

from assistant.answer_check import correct_false_refund_claim
from assistant.memory import ChatMemory, Message
from assistant.ollama_client import ToolCall, stream_reply
from assistant.tool_gate import find_reason_to_block
from assistant.tool_runner import build_tool_specs, run_tool
from lab_tools.log import cut_text, debug, log

MAX_MODEL_CALLS_PER_TURN = 4  # the model may ask for tools forever (3.3); stop here
NO_ANSWER_TEXT = "Sorry, I could not finish that. Please ask again in other words."
ANSWER_PREFIX = "bot> "


@dataclass
class ModelReply:
    """The model's whole reply for one call: its text and the tools it asked for."""

    text: str  # e.g. "Your order arrives on 2026-11-14."; often "" when it asks for tools
    tool_calls: list[ToolCall] = field(default_factory=list[ToolCall])  # [] = this is the final answer


@debug
def stream_and_collect_reply(turn_messages: list[Message]) -> ModelReply:
    """Call the model once, show its text on screen as it comes, and collect the whole reply.

    How:
        1. Stream the reply, offering every tool.
        2. Print each text piece at once ("bot> " before the first one).
        3. Collect the text pieces and the tool calls.
    Args:
        turn_messages: memory messages + this turn's tool messages so far.
    Returns:
        e.g. ModelReply(text="", tool_calls=[ToolCall("order_status", {"order_id": "A-1001"})]).
    Raises:
        httpx.HTTPError: from stream_reply (cli.main catches it).
    """
    text_pieces: list[str] = []
    tool_calls: list[ToolCall] = []
    tool_specs = build_tool_specs()
    for stream_piece in stream_reply(turn_messages, tool_specs):
        if stream_piece.text != "":
            if len(text_pieces) == 0:  # first text of this reply
                print(ANSWER_PREFIX, end="", flush=True)  # end="" = no new line; flush = show now
            print(stream_piece.text, end="", flush=True)
            text_pieces.append(stream_piece.text)
        tool_calls.extend(stream_piece.tool_calls)
    if len(text_pieces) > 0:
        print()  # the new line after the streamed text
    reply_text = "".join(text_pieces)  # glue the pieces into one text
    model_reply = ModelReply(text=reply_text, tool_calls=tool_calls)
    log.debug("result: text=%s tool_calls=%s", cut_text(reply_text), tool_calls)
    return model_reply


@debug
def get_tool_result(tool_call: ToolCall, user_question: str) -> str:
    """Ask the gate about one tool call, then run it, or explain why it was blocked.

    Args:
        tool_call: e.g. ToolCall("refund", {"order_id": "A-1001", "amount": 500}).
        user_question: the customer's message this turn (the gate checks who asked).
    Returns:
        The text the model gets back, e.g. "shipped on 2026-11-10, ..." or
        "error: blocked: refund needs a human: the customer did not ask for one".
    """
    block_reason = find_reason_to_block(tool_call.tool_name, tool_call.tool_arguments, user_question)
    if block_reason is not None:
        print(f"  (blocked {tool_call.tool_name}: {block_reason})")
        blocked_text = f"error: blocked: {block_reason}"
        return blocked_text
    print(f"  (using {tool_call.tool_name} {tool_call.tool_arguments})")
    tool_result_text = run_tool(tool_call.tool_name, tool_call.tool_arguments)
    log.debug("result: %s", cut_text(tool_result_text))
    return tool_result_text


def build_tool_round_messages(model_reply: ModelReply, user_question: str) -> list[Message]:
    """Build the messages that go back to the model after it asked for tools.

    How (3.3 part 1): first the model's own reply (it must see what it asked),
    then one "tool" message with the result of each call.
    Args:
        model_reply: a reply with at least one tool call.
        user_question: the customer's message this turn.
    Returns:
        e.g. [{"role": "assistant", "content": "", "tool_calls": [...]},
              {"role": "tool", "tool_name": "order_status", "content": "shipped ..."}].
    """
    tool_calls_for_ollama: list[dict[str, Any]] = []  # back in Ollama's own shape
    for tool_call in model_reply.tool_calls:
        function_part = {"name": tool_call.tool_name, "arguments": tool_call.tool_arguments}
        tool_calls_for_ollama.append({"function": function_part})
    model_reply_message: Message = {"role": "assistant", "content": model_reply.text,
                                    "tool_calls": tool_calls_for_ollama}
    tool_round_messages: list[Message] = [model_reply_message]
    for tool_call in model_reply.tool_calls:
        tool_result_text = get_tool_result(tool_call, user_question)
        tool_result_message: Message = {"role": "tool", "tool_name": tool_call.tool_name, "content": tool_result_text}
        tool_round_messages.append(tool_result_message)
    return tool_round_messages


@debug
def answer_one_turn(memory: ChatMemory, user_question: str) -> str:
    """Answer one user question, running tools when the model asks for them.

    How:
        1. Save the question in memory; copy the memory messages for this turn.
        2. Call the model. No tool calls -> that text is the final answer.
        3. Tool calls -> gate + run each, add the results, call the model again.
        4. After MAX_MODEL_CALLS_PER_TURN calls without an answer -> NO_ANSWER_TEXT.
        5. Correct a false refund claim (answer_check.py).
        6. Save the final answer in memory.
    Args:
        memory: the chat so far.
        user_question: e.g. "Where is my order A-1001?".
    Returns:
        The final answer, e.g. "Your order A-1001 arrives on 2026-11-14.".
    Raises:
        httpx.HTTPError: from the model call (cli.main catches it).
    """
    log.debug("start: user_question=%s", cut_text(user_question))
    memory.add_message("user", user_question)
    turn_messages = memory.messages_to_send()  # a copy: tool messages stay out of memory
    final_answer = NO_ANSWER_TEXT
    for model_call_number in range(1, MAX_MODEL_CALLS_PER_TURN + 1):
        log.debug("model call %d of %d", model_call_number, MAX_MODEL_CALLS_PER_TURN)
        model_reply = stream_and_collect_reply(turn_messages)
        if len(model_reply.tool_calls) == 0:
            final_answer = model_reply.text
            break
        tool_round_messages = build_tool_round_messages(model_reply, user_question)
        turn_messages.extend(tool_round_messages)
    if final_answer == NO_ANSWER_TEXT:
        print(ANSWER_PREFIX + NO_ANSWER_TEXT)
    checked_answer = correct_false_refund_claim(final_answer, turn_messages)
    memory.add_message("assistant", checked_answer)
    log.debug("result: checked_answer=%s", cut_text(checked_answer))
    return checked_answer
