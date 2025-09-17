from langchain.agents import initialize_agent, AgentType, Tool
import os
from dotenv import load_dotenv
from langchain.schema import SystemMessage
from tools.playlist_manipulation import create_playlist
load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")

#Gemini Initialization
def run_spotify_agent(llm):
    
    tools = [
        Tool(name="Create Playlist", func=create_playlist, description="Creates a playlist with specified name Input: 'name'"),
    ]

    system_message = SystemMessage(
        content=(
            "You are a helpful Spotify assistant. "
            "Always use the right tool based on the user query and the tool description "
            "If the request is incomplete (e.g., just 'add'), politely ask for the missing values. "
            "Return the result of the Action (Success/Failure)"
        )
    )


    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        agent_kwargs={"system_message": system_message},
    )


    print("🤖 Agent ready! Type 'quit' to exit.\n")

    while True:
        query = input("You: ")
        if query.lower().strip() == "quit":
            print("Bot: Goodbye 👋")
            break

        try:
            response = agent.invoke({"input": query})   
            print("Bot:", response["output"])
        except Exception as e:
            print("Bot: (error handled)", str(e))
