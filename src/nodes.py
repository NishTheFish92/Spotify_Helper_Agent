from langchain_core.messages import SystemMessage
from langgraph.graph import END
from langgraph.prebuilt import ToolNode
from .state import AgentState

SYSTEM_PROMPT = SystemMessage(
    content=(
        "You are a helpful Spotify assistant. "
        "Always use the right tool based on the user query and the tool description "
        "If the request is incomplete, politely ask for the missing values. "
        "Do not assume playlist names or song names that have not been specified by the user"
        "Return the result of the Action (Success/Failure)"

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
    if state["messages"][-1].tool_calls:
        return "tools"
    else:
        return END