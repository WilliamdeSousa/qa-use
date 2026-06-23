FROM python:3.12-slim

# Install system deps for Playwright/Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml .
RUN uv sync --no-dev --no-install-project

# Install Playwright browsers (Chromium only)
RUN uv run python -m playwright install --with-deps chromium

# Workaround: browser-use checks llm.provider/model_name without getattr, breaking standard LangChain providers
COPY patch_browser_use.py .
RUN uv run python3 patch_browser_use.py

# Copy application code
COPY src/ src/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
