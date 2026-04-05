from app.config import settings
from app.llm.anthropic import AnthropicProvider
from app.llm.base import LLMProvider
from app.llm.openai_provider import AzureOpenAIProvider, OpenAIProvider

_provider_instance: LLMProvider | None = None


def get_provider() -> LLMProvider:
    """Get or create the configured LLM provider singleton."""
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    if settings.llm_provider == "anthropic":
        _provider_instance = AnthropicProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )
    elif settings.llm_provider == "openai":
        _provider_instance = OpenAIProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            base_url=settings.llm_base_url,
        )
    elif settings.llm_provider == "azure":
        if not settings.llm_base_url:
            raise ValueError(
                "Azure provider requires LLM_BASE_URL (your Azure endpoint)"
            )
        _provider_instance = AzureOpenAIProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            base_url=settings.llm_base_url,
            api_version=settings.llm_api_version,
        )
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")

    return _provider_instance
