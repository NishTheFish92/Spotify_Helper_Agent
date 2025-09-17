from src import main_auth
from src import run_spotify_agent
from src import init_llm
access_token = main_auth()
llm = init_llm()
run_spotify_agent(llm)
