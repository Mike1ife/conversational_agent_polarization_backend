import os
from langchain_openai import ChatOpenAI

api_key = os.getenv("API_KEY")
llm = ChatOpenAI(
    model="longcat-flash-chat",
    openai_api_key=api_key,
    openai_api_base="https://api.longcat.chat/openai",
    max_completion_tokens=1024,
)
