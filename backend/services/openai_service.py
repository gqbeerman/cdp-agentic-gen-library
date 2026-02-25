"""Wrapper around the OpenAI Responses API for thread-based chat with file_search."""

import os
import re
from typing import AsyncGenerator

from openai import OpenAI
from services.langsmith_service import trace_chat


_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Lazily initialize the OpenAI client."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def create_thread() -> str:
    """Create a new OpenAI thread and return its ID."""
    thread = _get_client().beta.threads.create()
    return thread.id


def delete_thread(thread_id: str) -> None:
    """Delete an OpenAI thread."""
    try:
        _get_client().beta.threads.delete(thread_id)
    except Exception:
        # Thread may not exist on OpenAI side — that's fine
        pass


# Cache file_id -> filename lookups to avoid repeated API calls
_file_name_cache: dict[str, str] = {}


def _resolve_citations(text: str, annotations: list) -> str:
    """Replace citation markers like 【4:2†source】 with actual filenames."""
    if not annotations:
        return text

    for annotation in annotations:
        if hasattr(annotation, "file_citation") and annotation.file_citation:
            file_id = annotation.file_citation.file_id
            # Look up the filename (with caching)
            if file_id not in _file_name_cache:
                try:
                    file_obj = _get_client().files.retrieve(file_id)
                    _file_name_cache[file_id] = file_obj.filename
                except Exception:
                    _file_name_cache[file_id] = "unknown file"

            filename = _file_name_cache[file_id]
            # Replace the annotation marker with a readable citation
            text = text.replace(annotation.text, f" [{filename}]")

    return text


def get_thread_messages(thread_id: str) -> list[dict]:
    """Retrieve all messages from a thread, sorted oldest first."""
    messages = _get_client().beta.threads.messages.list(thread_id=thread_id, order="asc")
    result = []
    for msg in messages.data:
        content_text = ""
        for content_block in msg.content:
            if content_block.type == "text":
                content_text = _resolve_citations(
                    content_block.text.value,
                    content_block.text.annotations,
                )
        result.append(
            {
                "id": msg.id,
                "role": msg.role,
                "content": content_text,
            }
        )
    return result


def add_message(thread_id: str, content: str) -> str:
    """Add a user message to a thread."""
    message = _get_client().beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content,
    )
    return message.id


async def run_and_stream(thread_id: str, user_message: str) -> AsyncGenerator[str, None]:
    """Add a message and stream the assistant response.
    
    Yields chunks of the assistant's response text as they arrive.
    After streaming, yields a special __CITATIONS_RESOLVED__ marker followed
    by the fully resolved text (with real filenames instead of source markers).
    """
    # Add the user message
    add_message(thread_id, user_message)

    # Create a run and stream the response
    full_response = ""
    with _get_client().beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=_get_or_create_assistant(),
    ) as stream:
        for text in stream.text_deltas:
            full_response += text
            yield text

    # Resolve citations from the final assistant message
    try:
        messages = _get_client().beta.threads.messages.list(
            thread_id=thread_id, order="desc", limit=1
        )
        if messages.data:
            last_msg = messages.data[0]
            for content_block in last_msg.content:
                if content_block.type == "text" and content_block.text.annotations:
                    resolved = _resolve_citations(
                        content_block.text.value,
                        content_block.text.annotations,
                    )
                    # Signal the resolved text to the caller
                    yield f"__CITATIONS_RESOLVED__{resolved}"
                    full_response = resolved
    except Exception:
        pass

    # Trace the completed interaction
    trace_chat(
        thread_id=thread_id,
        user_message=user_message,
        assistant_response=full_response,
    )


def generate_title(user_message: str) -> str:
    """Generate a short title for a thread based on the first user message."""
    try:
        response = _get_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate a very short title (3-6 words) that summarizes the user's message. "
                        "Do not use quotes or punctuation. Just return the title text."
                    ),
                },
                {"role": "user", "content": user_message},
            ],
            max_tokens=20,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "New Chat"


_assistant_id: str | None = None

VECTOR_STORE_ID = os.getenv(
    "OPENAI_VECTOR_STORE_ID", "vs_699dc2bf4fd081919b5e039d2ba1110c"
)


def _get_or_create_assistant() -> str:
    """Get or create the default assistant with file_search enabled and vector store attached."""
    global _assistant_id
    if _assistant_id:
        return _assistant_id

    # Check for existing assistant by name
    assistants = _get_client().beta.assistants.list(limit=100)
    for assistant in assistants.data:
        if assistant.name == "Agentic RAG Library":
            _assistant_id = assistant.id
            # Ensure the vector store is attached
            _get_client().beta.assistants.update(
                _assistant_id,
                tool_resources={
                    "file_search": {"vector_store_ids": [VECTOR_STORE_ID]}
                },
            )
            return _assistant_id

    # Create new assistant with vector store
    assistant = _get_client().beta.assistants.create(
        name="Agentic RAG Library",
        instructions=(
            "You are a helpful research assistant for the Agentic RAG Library. "
            "Answer questions clearly and concisely. "
            "Always use file_search to find relevant information before answering. "
            "Cite your sources when referencing documents."
        ),
        model="gpt-4o",
        tools=[{"type": "file_search"}],
        tool_resources={
            "file_search": {"vector_store_ids": [VECTOR_STORE_ID]}
        },
    )
    _assistant_id = assistant.id
    return _assistant_id

