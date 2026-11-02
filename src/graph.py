from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from tools.playlist_manipulation import create_playlist, delete_playlist, toggle_playlist_privacy
from tools.get_songs import get_recommendations, search_songs, get_spotify_song_id
from tools.modify_songs_in_playlist import add_songs_to_playlist, delete_songs_from_playlist
from .state import AgentState
from .nodes import make_call_model, make_tool_node, tool_decision, approve

TOOLS = [
    create_playlist,
    delete_playlist,
    toggle_playlist_privacy,
    get_recommendations,
    search_songs,
    get_spotify_song_id,
    add_songs_to_playlist,
    delete_songs_from_playlist,
]


def build_graph(llm):
    graph = StateGraph(AgentState)

    graph.add_node("call_model", make_call_model(llm, TOOLS))
    graph.add_node("tools", make_tool_node(TOOLS))
    graph.add_node("approve", approve)

    graph.add_edge(START, "call_model")
    graph.add_conditional_edges("call_model", tool_decision, {"tools": "tools", "approve": "approve", END: END})
    graph.add_edge("tools", "call_model")

    return graph.compile(checkpointer=MemorySaver())
