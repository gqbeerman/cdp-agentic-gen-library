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
    "When referencing information from the retrieved documents, you MUST cite your sources using the exact labels provided in the context blocks (e.g. '[Page 4]', '[Section 2]'). Do not use generic numbers or abstract chunk references."
)


# ── Streaming completions ──

import json
from tools.retrieval import search_knowledge_base, retrieval_tool_schema

# ...

async def chat_stream(
    messages: list[dict],
    user_id: str,
    thread_id: str | None = None,
) -> AsyncGenerator[str, None]:
    """Stream a chat completion from the configured provider, handling tools."""
    config = _get_config()
    client = _get_client()

    tools = [retrieval_tool_schema]

    # PASS 1: Generate response, possibly calling tools
    stream = client.chat.completions.create(
        model=config["model"],
        messages=messages,
        tools=tools,
        stream=True,
    )

    full_response = ""
    tool_calls = {}

    for chunk in stream:
        delta = chunk.choices[0].delta if chunk.choices else None
        if not delta:
            continue

        # Option A: Normal content chunk
        if delta.content:
            text = delta.content
            full_response += text
            yield text
            
        # Option B: Tool call chunk
        elif delta.tool_calls:
            for tc in delta.tool_calls:
                idx = tc.index
                if idx not in tool_calls:
                    tool_calls[idx] = {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": ""}
                    }
                if tc.function.arguments:
                    tool_calls[idx]["function"]["arguments"] += tc.function.arguments

    # Check if any tools were actually called
    if tool_calls:
        # yield a status message so the UI knows we're searching
        # In a real app we might use a dedicated event type
        print(f"Tool calls detected: {len(tool_calls)}")
        
        # Format the assistant message containing the tool calls
        assistant_message = {
            "role": "assistant",
            "content": None,
            "tool_calls": list(tool_calls.values())
        }
        messages.append(assistant_message)

        # Execute all tool calls
        for tc in tool_calls.values():
            if tc["function"]["name"] == "search_knowledge_base":
                args = json.loads(tc["function"]["arguments"])
                print(f"Executing tool search_knowledge_base with args: {args}")
                result = await search_knowledge_base(args["query"], user_id)
                
                # Append tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result
                })

        # PASS 2: Send the updated messages list back to the LLM
        second_stream = client.chat.completions.create(
            model=config["model"],
            messages=messages,
            stream=True
        )
        
        for chunk in second_stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                text = delta.content
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
