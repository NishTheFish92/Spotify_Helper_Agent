import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.types import Command
from src.graph import build_graph


class FakeLLM(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


def ai_call(*calls):
    """An AIMessage requesting the given (name, args, id) tool calls."""
    return AIMessage("", tool_calls=[{"name": n, "args": a, "id": i} for n, a, i in calls])


@pytest.fixture
def make_app():
    """Builds the graph with a scripted LLM and dummy tools that record their calls."""
    calls = []

    @tool
    def create_playlist(name: str) -> str:
        """Dummy create_playlist."""
        calls.append(("create_playlist", name))
        return "created"

    @tool
    def delete_playlist(name: str) -> str:
        """Dummy delete_playlist."""
        calls.append(("delete_playlist", name))
        return "deleted"

    @tool
    def search_songs(query: str) -> str:
        """Dummy search_songs."""
        calls.append(("search_songs", query))
        return "song A, song B"

    @tool
    def broken_tool(x: str) -> str:
        """Always fails."""
        raise RuntimeError("spotify 404")

    def _make(*replies):
        llm = FakeLLM(messages=iter(replies))
        app = build_graph(llm, tools=[create_playlist, delete_playlist, search_songs, broken_tool])
        config = {"configurable": {"thread_id": "test"}}
        return app, config, calls

    return _make


def start(query):
    return {"messages": [HumanMessage(query)]}


def test_plain_reply_ends_without_tools(make_app):
    app, config, calls = make_app(AIMessage("I manage playlists."))
    result = app.invoke(start("what can you do"), config)

    assert [type(m) for m in result["messages"]] == [HumanMessage, AIMessage]
    assert calls == []


def test_safe_tool_runs_then_returns_to_model(make_app):
    app, config, calls = make_app(
        ai_call(("create_playlist", {"name": "Gym"}, "1")),
        AIMessage("Created Gym."),
    )
    result = app.invoke(start("create Gym"), config)

    assert calls == [("create_playlist", "Gym")]
    assert [type(m) for m in result["messages"]] == [HumanMessage, AIMessage, ToolMessage, AIMessage]
    assert app.get_state(config).interrupts == ()


def test_delete_pauses_before_running(make_app):
    app, config, calls = make_app(ai_call(("delete_playlist", {"name": "Gym"}, "1")))
    app.invoke(start("delete Gym"), config)

    state = app.get_state(config)
    assert state.next == ("approve",)
    assert 'Delete playlist "Gym"' in state.interrupts[0].value
    assert calls == []


def test_approve_yes_runs_delete(make_app):
    app, config, calls = make_app(
        ai_call(("delete_playlist", {"name": "Gym"}, "1")),
        AIMessage("Deleted Gym."),
    )
    app.invoke(start("delete Gym"), config)
    result = app.invoke(Command(resume="y"), config)

    assert calls == [("delete_playlist", "Gym")]
    assert result["messages"][-1].content == "Deleted Gym."


def test_approve_no_cancels_every_call(make_app):
    app, config, calls = make_app(
        ai_call(("search_songs", {"query": "chill"}, "1"), ("delete_playlist", {"name": "Gym"}, "2")),
        AIMessage("OK, nothing deleted."),
    )
    app.invoke(start("find chill songs and delete Gym"), config)
    result = app.invoke(Command(resume="no, keep it"), config)

    assert calls == []
    cancelled = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert {m.tool_call_id for m in cancelled} == {"1", "2"}
    assert all("cancelled" in m.content and "no, keep it" in m.content for m in cancelled)
    assert result["messages"][-1].content == "OK, nothing deleted."


def test_two_deletes_pause_twice(make_app):
    app, config, calls = make_app(
        ai_call(("delete_playlist", {"name": "A"}, "1")),
        ai_call(("delete_playlist", {"name": "B"}, "2")),
        AIMessage("Both deleted."),
    )
    app.invoke(start("delete A and B"), config)
    assert app.get_state(config).interrupts

    app.invoke(Command(resume="y"), config)
    assert app.get_state(config).interrupts

    result = app.invoke(Command(resume="y"), config)
    assert app.get_state(config).interrupts == ()
    assert calls == [("delete_playlist", "A"), ("delete_playlist", "B")]
    assert result["messages"][-1].content == "Both deleted."


def test_memory_persists_within_thread_only(make_app):
    app, config, _ = make_app(AIMessage("one"), AIMessage("two"), AIMessage("three"))
    app.invoke(start("first"), config)
    result = app.invoke(start("second"), config)

    assert [m.content for m in result["messages"]] == ["first", "one", "second", "two"]

    other = app.invoke(start("fresh"), {"configurable": {"thread_id": "other"}})
    assert [m.content for m in other["messages"]] == ["fresh", "three"]


def test_unknown_tool_returns_error_message(make_app):
    app, config, _ = make_app(
        ai_call(("not_a_tool", {}, "1")),
        AIMessage("Sorry, I can't do that."),
    )
    result = app.invoke(start("do something"), config)

    tool_msg = result["messages"][2]
    assert isinstance(tool_msg, ToolMessage)
    assert tool_msg.status == "error"
    assert "not_a_tool is not a valid tool" in tool_msg.content


def test_failing_tool_returns_error_message(make_app):
    app, config, _ = make_app(
        ai_call(("broken_tool", {"x": "hi"}, "1")),
        AIMessage("Something went wrong."),
    )
    result = app.invoke(start("break it"), config)

    tool_msg = result["messages"][2]
    assert tool_msg.status == "error"
    assert "spotify 404" in tool_msg.content
    assert result["messages"][-1].content == "Something went wrong."
