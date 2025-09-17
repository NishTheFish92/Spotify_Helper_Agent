from langchain_google_genai import ChatGoogleGenerativeAI
def init_llm():
    return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            temperature=0,
            max_tokens=None,
            max_retries=2,
        )
    