import pytest
from langchain_core.messages import AIMessage
from langgraph.graph import END
from src.nodes import tool_decision, describe_action, DESTRUCTIVE_TOOLS
from src.graph import TOOLS


def state_with_calls(*names):
    calls = [{"name": n, "args": {}, "id": str(i)} for i, n in enumerate(names)]
    return {"messages": [AIMessage("", tool_calls=calls)]}


@pytest.mark.parametrize(
    "names, expected",
    [
        ((), END),
        (("create_playlist",), "tools"),
        (("search_songs", "get_spotify_song_id"), "tools"),
        (("delete_playlist",), "approve"),
        (("delete_songs_from_playlist",), "approve"),
        (("search_songs", "delete_playlist"), "approve"),
    ],
)
def test_tool_decision(names, expected):
    assert tool_decision(state_with_calls(*names)) == expected


def test_destructive_tools_match_real_tool_names():
    # A typo here would silently skip approval for that tool.
    assert DESTRUCTIVE_TOOLS <= {t.name for t in TOOLS}


def test_describe_delete_playlist():
    call = {"name": "delete_playlist", "args": {"name": "Gym"}}
    assert describe_action(call) == 'Delete playlist "Gym"'


def test_describe_delete_songs_shows_count():
    call = {"name": "delete_songs_from_playlist", "args": {"song_ids": ["a", "b", "c"], "playlist_name": "Chill"}}
    assert describe_action(call) == 'Remove 3 songs from "Chill"'


def test_describe_falls_back_for_other_tools():
    call = {"name": "create_playlist", "args": {"name": "Gym"}}
    assert describe_action(call) == "create_playlist({'name': 'Gym'})"
