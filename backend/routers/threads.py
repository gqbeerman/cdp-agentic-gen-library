"""Thread management endpoints."""

import os

from fastapi import APIRouter, Request, HTTPException
from supabase import create_client, Client

from middleware.auth import get_user_id
from services.openai_service import (
    create_thread as create_openai_thread,
    delete_thread as delete_openai_thread,
    get_thread_messages,
)

router = APIRouter(prefix="/api/threads", tags=["threads"])

_supabase: Client | None = None


def _get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        )
    return _supabase


@router.get("")
async def list_threads(request: Request):
    """List all threads for the authenticated user."""
    user_id = get_user_id(request)

    result = (
        _get_supabase().table("user_threads")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.post("")
async def create_thread(request: Request):
    """Create a new thread."""
    user_id = get_user_id(request)

    # Create thread on OpenAI
    openai_thread_id = create_openai_thread()

    # Store mapping in Supabase
    result = (
        _get_supabase().table("user_threads")
        .insert(
            {
                "user_id": user_id,
                "thread_id": openai_thread_id,
                "title": "New Chat",
            }
        )
        .execute()
    )

    return result.data[0]


@router.delete("/{thread_id}")
async def delete_thread(thread_id: str, request: Request):
    """Delete a thread."""
    user_id = get_user_id(request)

    # Get the OpenAI thread ID first
    result = (
        _get_supabase().table("user_threads")
        .select("thread_id")
        .eq("id", thread_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Thread not found")

    openai_thread_id = result.data[0]["thread_id"]

    # Delete from OpenAI
    delete_openai_thread(openai_thread_id)

    # Delete from Supabase
    _get_supabase().table("user_threads").delete().eq("id", thread_id).eq(
        "user_id", user_id
    ).execute()

    return {"status": "deleted"}


@router.get("/{thread_id}/messages")
async def list_messages(thread_id: str, request: Request):
    """List messages for a thread."""
    user_id = get_user_id(request)

    # Verify the thread belongs to the user
    result = (
        _get_supabase().table("user_threads")
        .select("thread_id")
        .eq("id", thread_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Thread not found")

    openai_thread_id = result.data[0]["thread_id"]
    messages = get_thread_messages(openai_thread_id)
    return messages
