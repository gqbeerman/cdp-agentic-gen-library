"""Chat endpoint with SSE streaming."""

import json
import os

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from supabase import create_client, Client

from middleware.auth import get_user_id
from services.completions_service import chat_stream, generate_title, get_system_prompt
from services.message_service import save_message, build_completion_messages
from services.provider_config import get_provider_config

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
    model: str | None = None
    embedding_model: str | None = None
    openrouter_api_key: str | None = None
    provider_keys: dict[str, str] = {}


@router.post("/chat")
async def chat(request: Request, body: ChatRequest):
    """Send a message and stream the assistant's response via SSE."""
    user_id = get_user_id(request)

    # Verify the thread belongs to the user and get its current title
    result = (
        _get_supabase().table("user_threads")
        .select("id, title")
        .eq("id", body.thread_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Thread not found")

    current_title = result.data[0]["title"]
    config = get_provider_config()

    # Save the user message to our database
    save_message(
        thread_id=body.thread_id,
        role="user",
        content=body.message,
    )

    # Build the full messages array (system + history)
    actual_model = body.model or config["model"]
    system_prompt = get_system_prompt(actual_model)
    messages = build_completion_messages(body.thread_id, system_prompt)

    async def event_generator():
        full_response = ""
        try:
            async for chunk in chat_stream(
                messages, 
                user_id=user_id, 
                thread_id=body.thread_id,
                model=body.model,
                embedding_model=body.embedding_model,
                openrouter_api_key=body.openrouter_api_key,
                provider_keys=body.provider_keys
            ):
                full_response += chunk
                yield {
                    "data": json.dumps({"content": chunk}),
                }
            yield {"data": "[DONE]"}

            # Determine the actual provider used
            actual_provider = "openrouter" if (body.openrouter_api_key and "/" in (body.model or "")) else config["provider"]

            # Save the assistant response to our database
            save_message(
                thread_id=body.thread_id,
                role="assistant",
                content=full_response,
                model=body.model or config["model"],
                provider=actual_provider,
            )

            # Auto-generate title on the first message
            if current_title == "New Chat":
                new_title = generate_title(
                    body.message, 
                    openrouter_api_key=body.openrouter_api_key,
                    provider_keys=body.provider_keys
                )
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
