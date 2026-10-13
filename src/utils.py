import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def init_llm():
    return ChatOpenAI(
            model="auto",
            api_key=os.getenv("FREELLM_API_KEY"),
            base_url=os.getenv("FREELLM_BASE_URL", "http://localhost:3001/v1"),
            temperature=0,
            max_tokens=None,
            max_retries=2,
        )
