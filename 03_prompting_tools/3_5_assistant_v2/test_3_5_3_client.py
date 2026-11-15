"""Tests for assistant/ollama_client.py, tool part: reading tool calls from the stream. No Ollama.

  uv run pytest 03_prompting_tools/3_5_assistant_v2/test_3_5_3_client.py -v
"""

from assistant.ollama_client import ToolCall, parse_stream_line
from lab_tools.log import debug, log

# Real line from qwen3:1.7b, Ollama 0.40.16, "Where is my order A-1001?" (2026-11-15).
# The tool call comes as one line with empty text.
TOOL_CALL_LINE = ('{"message":{"role":"assistant","content":"","tool_calls":[{"id":"call_7vx7fsnh",'
                  '"function":{"index":0,"name":"order_status","arguments":{"order_id":"A-1001"}}}]},'
                  '"done":false}')
TWO_TOOL_CALLS_LINE = ('{"message":{"role":"assistant","content":"","tool_calls":['
                       '{"function":{"name":"multiply","arguments":{"first_number":12.5,"second_number":8}}},'
                       '{"function":{"name":"multiply","arguments":{"first_number":7,"second_number":6}}}]},'
                       '"done":false}')
NULL_TOOL_CALLS_LINE = '{"message":{"role":"assistant","content":"Hi","tool_calls":null},"done":false}'


@debug
def test_tool_call_line_gives_one_tool_call() -> None:
    """The real tool-call line becomes one ToolCall and no text: else the tool would never run."""
    stream_piece = parse_stream_line(TOOL_CALL_LINE)
    expected_tool_calls = [ToolCall(tool_name="order_status", tool_arguments={"order_id": "A-1001"})]
    log.debug("expected=%s got=%s", expected_tool_calls, stream_piece.tool_calls)
    assert stream_piece.tool_calls == expected_tool_calls
    assert stream_piece.text == ""


@debug
def test_two_tool_calls_in_one_line_keep_their_order() -> None:
    """2 calls in one reply both come out, in order: 3.3 part 1, two questions at once."""
    stream_piece = parse_stream_line(TWO_TOOL_CALLS_LINE)
    expected_tool_calls = [ToolCall("multiply", {"first_number": 12.5, "second_number": 8}),
                           ToolCall("multiply", {"first_number": 7, "second_number": 6})]
    log.debug("expected=%s got=%s", expected_tool_calls, stream_piece.tool_calls)
    assert stream_piece.tool_calls == expected_tool_calls


@debug
def test_null_tool_calls_mean_none() -> None:
    """A null "tool_calls" is read as no tool calls, and the text is kept: Ollama sends null, it must not crash."""
    stream_piece = parse_stream_line(NULL_TOOL_CALLS_LINE)
    log.debug("expected=('Hi', []) got=(%r, %s)", stream_piece.text, stream_piece.tool_calls)
    assert stream_piece.text == "Hi"
    assert stream_piece.tool_calls == []
