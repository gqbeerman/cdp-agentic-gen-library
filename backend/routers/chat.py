"""Chat endpoint with SSE streaming."""

import json
import os

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from supabase import create_client, Client

from middleware.auth import get_user_id
from services.openai_service import run_and_stream, generate_title

router = APIRouter(prefix="/api", tags=["chat"])

_supabase: Client | None = None


def _get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        )
    return _supabase


class ChatRequest(BaseModel):
    thread_id: str
    message: str


@router.post("/chat")
async def chat(request: Request, body: ChatRequest):
    """Send a message and stream the assistant's response via SSE."""
    user_id = get_user_id(request)

    # Verify the thread belongs to the user and get its current title
    result = (
        _get_supabase().table("user_threads")
        .select("thread_id, title")
        .eq("id", body.thread_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Thread not found")

    openai_thread_id = result.data[0]["thread_id"]
    current_title = result.data[0]["title"]

    async def event_generator():
        try:
            async for chunk in run_and_stream(openai_thread_id, body.message):
                if chunk.startswith("__CITATIONS_RESOLVED__"):
                    resolved_text = chunk[len("__CITATIONS_RESOLVED__"):]
                    yield {
                        "data": json.dumps({"citations_resolved": resolved_text}),
                    }
                else:
                    yield {
                        "data": json.dumps({"content": chunk}),
                    }
            yield {"data": "[DONE]"}

            # Auto-generate title on the first message
            if current_title == "New Chat":
                new_title = generate_title(body.message)
                _get_supabase().table("user_threads").update(
                    {"title": new_title}
                ).eq("id", body.thread_id).eq("user_id", user_id).execute()

                yield {
                    "data": json.dumps(
                        {"title_update": {"thread_id": body.thread_id, "title": new_title}}
                    ),
                }
        except Exception as e:
            yield {
                "data": json.dumps({"error": str(e)}),
            }

    return EventSourceResponse(event_generator())
