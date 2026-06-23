from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration loaded from environment variables."""

    llm_provider: Literal["azure_openai", "openai", "anthropic", "google"] = "azure_openai"

    # Azure OpenAI
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_deployment: str = "o4-mini"
    azure_openai_api_version: str = "2025-01-01-preview"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "o4-mini"

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    # Google
    google_api_key: str = ""
    google_model: str = "gemini-2.5-flash"

    # Browser settings
    browser_headless: bool = True
    max_agent_steps: int = 10

    model_config = {"env_prefix": "", "case_sensitive": False}


settings = Settings()
