"""Provider configuration for OpenAI-compatible LLM endpoints.

Supports: OpenAI, OpenRouter, Ollama, LM Studio, or any custom endpoint.
All share the /v1/chat/completions API shape.
"""

import os
import logging

logger = logging.getLogger(__name__)

# Default settings per provider
PROVIDER_DEFAULTS: dict[str, dict] = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",  # Ollama doesn't need a real key
    },
    "lmstudio": {
        "base_url": "http://localhost:1234/v1",
        "api_key": "lm-studio",  # LM Studio doesn't need a real key
    },
}

# Default models per provider (used if LLM_MODEL is not set)
DEFAULT_MODELS: dict[str, str] = {
    "openai": "gpt-4o",
    "openrouter": "openai/gpt-4o",
    "ollama": "llama3.2",
    "lmstudio": "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
}

DEFAULT_TITLE_MODELS: dict[str, str] = {
    "openai": "gpt-4o-mini",
    "openrouter": "openai/gpt-4o-mini",
    "ollama": "llama3.2",
    "lmstudio": "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
}


def get_provider_config() -> dict:
    """Read LLM provider settings from environment variables.

    Env vars:
        LLM_PROVIDER   - Provider name (openai|openrouter|ollama|lmstudio|custom)
        LLM_BASE_URL   - Override the default base URL for the provider
        LLM_API_KEY    - API key (falls back to OPENAI_API_KEY for openai provider)
        LLM_MODEL      - Chat model to use
        TITLE_MODEL    - Lightweight model for title generation

    Returns dict with: provider, base_url, api_key, model, title_model
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower().strip()
    defaults = PROVIDER_DEFAULTS.get(provider, {})

    # Base URL: env override → provider default
    base_url = os.getenv("LLM_BASE_URL", "").strip() or defaults.get("base_url", "")

    # API key: LLM_API_KEY → OPENAI_API_KEY (for backward compat) → provider default
    api_key = (
        os.getenv("LLM_API_KEY", "").strip()
        or os.getenv("OPENAI_API_KEY", "").strip()
        or defaults.get("api_key", "not-needed")
    )

    # Model: env → provider default
    model = os.getenv("LLM_MODEL", "").strip() or DEFAULT_MODELS.get(provider, "gpt-4o")
    title_model = os.getenv("TITLE_MODEL", "").strip() or DEFAULT_TITLE_MODELS.get(provider, model)

    config = {
        "provider": provider,
        "base_url": base_url,
        "api_key": api_key,
        "model": model,
        "title_model": title_model,
    }

    logger.info(f"LLM provider: {provider} | base_url: {base_url} | model: {model}")
    return config
