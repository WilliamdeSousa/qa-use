"""Factory for creating LLM instances based on provider config."""

from langchain_core.language_models.chat_models import BaseChatModel

from src.config import settings


def create_llm() -> BaseChatModel:
    """Create an LLM instance based on the configured provider.

    Uses browser_use.ChatAzureOpenAI for Azure to avoid the missing `provider`
    attribute crash that happens with langchain_openai.AzureChatOpenAI.
    """
    match settings.llm_provider:
        case "azure_openai":
            # browser-use ships its own patched wrapper that adds the `provider` attr
            from browser_use import ChatAzureOpenAI

            return ChatAzureOpenAI(
                azure_deployment=settings.azure_openai_deployment,
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
            )

        case "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,  # type: ignore[arg-type]
            )

        case "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model_name=settings.anthropic_model,
                api_key=settings.anthropic_api_key,  # type: ignore[arg-type]
            )

        case "google":
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=settings.google_model,
                google_api_key=settings.google_api_key,  # type: ignore[arg-type]
            )

        case _:
            raise ValueError(
                f"Unsupported LLM_PROVIDER: '{settings.llm_provider}'. "
                "Must be one of: azure_openai, openai, anthropic, google"
            )
