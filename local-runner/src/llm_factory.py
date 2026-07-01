"""Factory for creating LLM instances based on provider config."""

from browser_use.llm.base import BaseChatModel

from src.config import settings


def create_llm() -> BaseChatModel:
    print("LLM PROVIDER:", settings.llm_provider)
    """Create a browser-use native LLM instance based on the configured provider."""
    match settings.llm_provider:
        case "azure_openai":
            from browser_use.llm.azure.chat import ChatAzureOpenAI

            return ChatAzureOpenAI(
                azure_deployment=settings.azure_openai_deployment,
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
            )

        case "openai":
            from browser_use.llm.openai.chat import ChatOpenAI

            return ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                timeout=300,
            )

        case "anthropic":
            from browser_use.llm.anthropic.chat import ChatAnthropic

            return ChatAnthropic(
                model=settings.anthropic_model,
                api_key=settings.anthropic_api_key,
            )

        case "google":
            from browser_use.llm.google.chat import ChatGoogle

            return ChatGoogle(
                model=settings.google_model,
                api_key=settings.google_api_key,
            )

        case _:
            raise ValueError(
                f"Unsupported LLM_PROVIDER: '{settings.llm_provider}'. "
                "Must be one of: azure_openai, openai, anthropic, google"
            )
