from collections.abc import AsyncIterator

from openai import AsyncAzureOpenAI, AsyncOpenAI

from app.llm.base import LLMProvider, Message


class OpenAIProvider(LLMProvider):
    """OpenAI-compatible LLM provider."""

    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        self.model = model
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = AsyncOpenAI(**kwargs)

    def _build_messages(
        self, messages: list[Message], system: str | None
    ) -> list[dict]:
        result = []
        if system:
            result.append({"role": "system", "content": system})
        for msg in messages:
            result.append({"role": msg.role, "content": msg.content})
        return result

    async def complete(
        self,
        messages: list[Message],
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self._build_messages(messages, system),
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    async def stream(
        self,
        messages: list[Message],
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self._build_messages(messages, system),
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AzureOpenAIProvider(OpenAIProvider):
    """Azure OpenAI LLM provider. Same API, different client."""

    def __init__(self, api_key: str, model: str, base_url: str, api_version: str):
        self.model = model
        self.client = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=base_url,
            api_version=api_version,
        )
