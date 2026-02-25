"""Message storage service — CRUD for chat messages in Supabase.

Replaces OpenAI's managed thread storage with self-managed messages
stored in the `chat_messages` table.
"""

import os
import logging

from supabase import create_client, Client

logger = logging.getLogger(__name__)

_supabase: Client | None = None


def _get_supabase() -> Client:
    """Lazily initialize the Supabase client."""
    global _supabase
    if _supabase is None:
        _supabase = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        )
    return _supabase


def get_messages(thread_id: str) -> list[dict]:
    """Fetch all messages for a thread, ordered by created_at ascending.

    Returns list of dicts with: id, role, content, model, provider, created_at
    """
    result = (
        _get_supabase()
        .table("chat_messages")
        .select("id, role, content, model, provider, created_at")
        .eq("thread_id", thread_id)
        .order("created_at", desc=False)
        .execute()
    )
    return result.data


def save_message(
    thread_id: str,
    role: str,
    content: str,
    model: str | None = None,
    provider: str | None = None,
) -> dict:
    """Insert a message into the chat_messages table.

    Returns the inserted row.
    """
    row = {
        "thread_id": thread_id,
        "role": role,
        "content": content,
    }
    if model:
        row["model"] = model
    if provider:
        row["provider"] = provider

    result = _get_supabase().table("chat_messages").insert(row).execute()
    return result.data[0] if result.data else {}


def build_completion_messages(
    thread_id: str,
    system_prompt: str,
) -> list[dict]:
    """Build the messages array for a chat completions call.

    Returns: [system_message] + [all thread messages in chronological order]

    Each message is a dict with 'role' and 'content' keys,
    matching the OpenAI Chat Completions API format.
    """
    messages = [{"role": "system", "content": system_prompt}]

    thread_messages = get_messages(thread_id)
    for msg in thread_messages:
        messages.append({
            "role": msg["role"],
            "content": msg["content"],
        })

    return messages
