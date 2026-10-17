from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from .graph import build_graph
import pathlib

pathlib.Path("user_id").touch(exist_ok=True)
load_dotenv()
VERBOSE = True

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
            if VERBOSE:
                for chunk in app.stream(inputs, config, stream_mode="updates"):
                    for node, update in chunk.items():
                        for message in update["messages"]:
                            message.pretty_print()
            else:
                result = app.invoke(inputs, config)
                print("Bot:", result["messages"][-1].content)
        except Exception as e:
            print("Bot: (error handled)", str(e))
