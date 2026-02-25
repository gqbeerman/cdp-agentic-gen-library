"""Chat completions service using the OpenAI-compatible API.

Works with any provider that implements /v1/chat/completions:
OpenAI, OpenRouter, Ollama, LM Studio, etc.
"""

import logging
from typing import AsyncGenerator

from openai import OpenAI

from services.provider_config import get_provider_config
from services.langsmith_service import trace_chat

logger = logging.getLogger(__name__)

_client: OpenAI | None = None
_config: dict | None = None


def _get_config() -> dict:
    """Lazily load provider config."""
    global _config
    if _config is None:
        _config = get_provider_config()
    return _config


def _get_client() -> OpenAI:
    """Lazily initialize the OpenAI-compatible client."""
    global _client
    if _client is None:
        config = _get_config()
        _client = OpenAI(
            base_url=config["base_url"],
            api_key=config["api_key"],
        )
    return _client


# ── System prompt ──

SYSTEM_PROMPT = (
    "You are a helpful research assistant for the Agentic RAG Library. "
    "Answer questions clearly and concisely. "
    "Cite your sources when referencing documents."
)


# ── Streaming completions ──

async def chat_stream(
    messages: list[dict],
    thread_id: str | None = None,
) -> AsyncGenerator[str, None]:
    """Stream a chat completion from the configured provider.

    Args:
        messages: The full messages array including system prompt.
        thread_id: Optional thread ID for tracing.

    Yields:
        Content chunks as they arrive from the model.
    """
    config = _get_config()
    client = _get_client()

    full_response = ""

    stream = client.chat.completions.create(
        model=config["model"],
        messages=messages,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            text = chunk.choices[0].delta.content
            full_response += text
            yield text

    # Trace the completed interaction
    if thread_id:
        user_msg = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            "",
        )
        trace_chat(
            thread_id=thread_id,
            user_message=user_msg,
            assistant_response=full_response,
            model=config["model"],
            provider=config["provider"],
        )


# ── Title generation ──

def generate_title(user_message: str) -> str:
    """Generate a short title for a thread based on the first user message."""
    config = _get_config()
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=config["title_model"],
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate a very short title (3-6 words) that summarizes "
                        "the user's message. Do not use quotes or punctuation. "
                        "Just return the title text."
                    ),
                },
                {"role": "user", "content": user_message},
            ],
            max_tokens=20,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"Failed to generate title: {e}")
        return "New Chat"
