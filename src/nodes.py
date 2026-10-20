from typing import Literal
from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.graph import END
from langgraph.prebuilt import ToolNode
from langgraph.types import Command, interrupt
from .state import AgentState

DESTRUCTIVE_TOOLS = {"delete_playlist", "delete_songs_from_playlist"}

SYSTEM_PROMPT = SystemMessage(
    content=(
        "You are a helpful Spotify assistant. "
        "Always use the right tool based on the user query and the tool description. "
        "If the request is incomplete, politely ask for the missing values. "
        "Do not assume playlist names or song names that have not been specified by the user. "
        "Return the result of the Action (Success/Failure)."

    )
)


def make_call_model(llm, tools):
    llm_with_tools = llm.bind_tools(tools)

    def call_model(state: AgentState):
        response = llm_with_tools.invoke([SYSTEM_PROMPT] + state["messages"])
        return {"messages": [response]}

    return call_model


def make_tool_node(tools):
    return ToolNode(tools)

def tool_decision(state: AgentState):
    tool_calls = state["messages"][-1].tool_calls
    if any(call["name"] in DESTRUCTIVE_TOOLS for call in tool_calls):
        return "approve"
    elif tool_calls:
        return "tools"
    else:
        return END


def describe_action(call):
    args = call["args"]
    if call["name"] == "delete_playlist":
        return f'Delete playlist "{args.get("name")}"'
    if call["name"] == "delete_songs_from_playlist":
        return f'Remove {len(args.get("song_ids", []))} songs from "{args.get("playlist_name")}"'
    return f"{call['name']}({args})"


def approve(state: AgentState) -> Command[Literal["tools", "call_model"]]:
    tool_calls = state["messages"][-1].tool_calls
    actions = "\n".join(
        f"  • {describe_action(call)}"
        for call in tool_calls
        if call["name"] in DESTRUCTIVE_TOOLS
    )
    question = f"⚠  This can't be undone:\n{actions}\nProceed? (y/n):"

    answer = interrupt(question)

    if str(answer).strip().lower() in ("y", "yes","yeah","ye"):
        return Command(goto="tools")

    reject_content=f"User cancelled this action. User remark : {answer}. Do not retry it. Redo any other cancelled actions if still needed."
    cancelled = [
        ToolMessage(
            content=reject_content,
            tool_call_id=call["id"],
            name=call["name"],
        )
        for call in tool_calls
    ]
    return Command(update={"messages": cancelled}, goto="call_model")
