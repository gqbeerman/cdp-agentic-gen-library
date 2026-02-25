"""Thread management endpoints."""

import os

from fastapi import APIRouter, Request, HTTPException
from supabase import create_client, Client

from middleware.auth import get_user_id
from services.message_service import get_messages

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

    # Just insert into user_threads — no external API call needed
    result = (
        _get_supabase().table("user_threads")
        .insert(
            {
                "user_id": user_id,
                "title": "New Chat",
            }
        )
        .execute()
    )

    return result.data[0]


@router.delete("/{thread_id}")
async def delete_thread(thread_id: str, request: Request):
    """Delete a thread. Messages cascade-delete via FK constraint."""
    user_id = get_user_id(request)

    # Verify ownership
    result = (
        _get_supabase().table("user_threads")
        .select("id")
        .eq("id", thread_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Delete from Supabase — chat_messages cascade-delete automatically
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
        .select("id")
        .eq("id", thread_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Thread not found")

    messages = get_messages(thread_id)
    return messages
