"""LangSmith tracing for OpenAI interactions."""

import os
import logging

logger = logging.getLogger(__name__)

# Check if LangSmith is configured
_langsmith_enabled = bool(os.getenv("LANGCHAIN_API_KEY"))


def trace_chat(
    thread_id: str,
    user_message: str,
    assistant_response: str,
) -> None:
    """Trace a chat interaction with LangSmith.

    Uses the langsmith SDK to create a manual run trace for the
    completed chat interaction.
    """
    if not _langsmith_enabled:
        logger.debug("LangSmith not configured — skipping trace")
        return

    try:
        from langsmith import Client
        from langsmith.run_trees import RunTree

        rt = RunTree(
            name="chat",
            run_type="chain",
            inputs={
                "thread_id": thread_id,
                "message": user_message,
            },
            outputs={
                "response": assistant_response,
            },
        )
        rt.end()
        rt.post()
    except Exception as e:
        logger.warning(f"Failed to trace to LangSmith: {e}")
