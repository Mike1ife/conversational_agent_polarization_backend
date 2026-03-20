from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="longcat-flash-chat",
    openai_api_key="ak_1i10Gb61767d9lt7k13YA2Hg0nM5f",
    openai_api_base="https://api.longcat.chat/openai",
    max_completion_tokens=512,
)
