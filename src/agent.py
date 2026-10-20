from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from .graph import build_graph
import pathlib

pathlib.Path("user_id").touch(exist_ok=True)
load_dotenv()
VERBOSE = False

def run_spotify_agent(llm):

    app = build_graph(llm)
    config = {"configurable": {"thread_id": "cli"}}

    print("Agent ready! Type 'quit' to exit.\n")

    while True:
        query = input("You: ")
        if query.lower().strip() == "quit":
            print("Bot: Goodbye 👋")
            break

        try:
            inputs = {"messages": [HumanMessage(query)]}
            while True:
                if VERBOSE:
                    for chunk in app.stream(inputs, config, stream_mode="updates"):
                        for node, update in chunk.items():
                            if node == "__interrupt__" or not update:
                                continue
                            for message in update["messages"]:
                                message.pretty_print()
                else:
                    app.invoke(inputs, config)

                state = app.get_state(config)
                if not state.interrupts:
                    break
                answer = input(f"Bot: {state.interrupts[0].value} ")
                inputs = Command(resume=answer)

            if not VERBOSE:
                print("Bot:", state.values["messages"][-1].content)
        except Exception as e:
            print("Bot: (error handled)", str(e))
