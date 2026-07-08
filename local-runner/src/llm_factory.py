"""Factory for creating LLM instances based on provider config."""

import logging
import shlex
import time

import httpx
from browser_use.llm.base import BaseChatModel

from src.config import settings

logger = logging.getLogger(__name__)


def _request_to_curl(request: httpx.Request) -> str:
    """Render an httpx.Request as an equivalent curl command for replay."""
    parts = ["curl", "-sS", "-X", request.method]
    for key, value in request.headers.items():
        if key.lower() in ("content-length", "host", "accept-encoding", "connection"):
            continue
        parts += ["-H", shlex.quote(f"{key}: {value}")]
    body = request.content
    if body:
        try:
            body_str = body.decode("utf-8")
        except UnicodeDecodeError:
            body_str = body.decode("latin-1")
        parts += ["--data-raw", shlex.quote(body_str)]
    parts.append(shlex.quote(str(request.url)))
    return " ".join(parts)


async def _log_request_as_curl(request: httpx.Request) -> None:
    logger.info("[LLM][curl] %s", _request_to_curl(request))


async def _log_response_body(response: httpx.Response) -> None:
    await response.aread()
    logger.info("[LLM][resposta bruta] status=%s body=%s", response.status_code, response.text)


def _logging_http_client(timeout: float) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=timeout,
        event_hooks={"request": [_log_request_as_curl], "response": [_log_response_body]},
    )


def _with_request_logging(llm: BaseChatModel) -> BaseChatModel:
    """Wrap llm.ainvoke so every call to the LLM logs when it's sent, when a
    response comes back, and how long it took (or the error, if it failed).
    """
    original_ainvoke = llm.ainvoke

    async def logged_ainvoke(messages, output_format=None, **kwargs):
        start = time.monotonic()
        logger.info(
            "[LLM] solicitacao enviada (provider=%s, model=%s, num_messages=%d)",
            llm.provider,
            llm.model,
            len(messages),
        )
        try:
            result = await original_ainvoke(messages, output_format, **kwargs)
            elapsed = time.monotonic() - start
            logger.info("[LLM] resposta recebida em %.1fs", elapsed)
            return result
        except Exception as exc:
            elapsed = time.monotonic() - start
            logger.error("[LLM] erro ao enviar/receber requisicao apos %.1fs: %r", elapsed, exc)
            raise

    llm.ainvoke = logged_ainvoke
    return llm


def create_llm() -> BaseChatModel:
    """Create a browser-use native LLM instance based on the configured provider."""
    match settings.llm_provider:
        case "azure_openai":
            from browser_use.llm.azure.chat import ChatAzureOpenAI

            llm = ChatAzureOpenAI(
                azure_deployment=settings.azure_openai_deployment,
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
            )

        case "openai":
            from browser_use.llm.openai.chat import ChatOpenAI

            llm = ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                timeout=300,
                http_client=_logging_http_client(300),
            )

        case "anthropic":
            from browser_use.llm.anthropic.chat import ChatAnthropic

            llm = ChatAnthropic(
                model=settings.anthropic_model,
                api_key=settings.anthropic_api_key,
            )

        case "google":
            from browser_use.llm.google.chat import ChatGoogle

            llm = ChatGoogle(
                model=settings.google_model,
                api_key=settings.google_api_key,
            )

        case _:
            raise ValueError(
                f"Unsupported LLM_PROVIDER: '{settings.llm_provider}'. "
                "Must be one of: azure_openai, openai, anthropic, google"
            )

    logger.info("[LLM] provider configurado: %s (model=%s)", settings.llm_provider, llm.model)
    return _with_request_logging(llm)
