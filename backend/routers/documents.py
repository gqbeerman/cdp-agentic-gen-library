"""Document management endpoints — upload, list, delete."""

import os
import uuid

from fastapi import APIRouter, Request, HTTPException, UploadFile, File, BackgroundTasks
from supabase import create_client, Client

from middleware.auth import get_user_id
from services import ingestion_service

router = APIRouter(prefix="/api/documents", tags=["documents"])

_supabase: Client | None = None

# Allowed MIME types
ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/markdown",
    "text/plain",
    "text/html",
}

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".md", ".txt", ".html"}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def _get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        )
    return _supabase


@router.get("")
async def list_documents(request: Request):
    """List all documents for the authenticated user."""
    user_id = get_user_id(request)

    result = (
        _get_supabase()
        .table("documents")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.post("/upload")
async def upload_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload a document to Supabase Storage and track it."""
    user_id = get_user_id(request)

    # Validate file extension
    filename = file.filename or "unnamed"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read file content
    content = await file.read()
    file_size = len(content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 50 MB)")

    # Generate document ID and storage path
    doc_id = str(uuid.uuid4())
    storage_path = f"{user_id}/{doc_id}/{filename}"

    # Upload to Supabase Storage
    try:
        _get_supabase().storage.from_("documents").upload(
            path=storage_path,
            file=content,
            file_options={"content-type": file.content_type or "application/octet-stream"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage upload failed: {e}")

    # Insert document record
    result = (
        _get_supabase()
        .table("documents")
        .insert(
            {
                "id": doc_id,
                "user_id": user_id,
                "filename": filename,
                "file_type": file.content_type,
                "file_size": file_size,
                "storage_path": storage_path,
                "status": "uploaded",
            }
        )
        .execute()
    )

    # Kick off background processing
    background_tasks.add_task(
        ingestion_service.process_document,
        document_id=doc_id,
        user_id=user_id,
        storage_path=storage_path,
        file_type=file.content_type
    )

    return result.data[0] if result.data else {}


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, request: Request):
    """Delete a document and its stored file."""
    user_id = get_user_id(request)

    # Verify ownership and get storage path
    result = (
        _get_supabase()
        .table("documents")
        .select("id, storage_path")
        .eq("id", doc_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Document not found")

    storage_path = result.data[0]["storage_path"]

    # Delete from Supabase Storage
    try:
        _get_supabase().storage.from_("documents").remove([storage_path])
    except Exception as e:
        # Log but don't fail — the DB row should still be cleaned up
        import logging
        logging.warning(f"Failed to delete storage file: {e}")

    # Delete chunks first to avoid foreign key constraints (if ON DELETE CASCADE is missing)
    try:
        _get_supabase().table("document_chunks").delete().eq("document_id", doc_id).execute()
    except Exception as e:
        import logging
        logging.warning(f"Failed to cleanly delete document chunks: {e}")

    # Delete from database
    _get_supabase().table("documents").delete().eq("id", doc_id).eq(
        "user_id", user_id
    ).execute()

    return {"status": "deleted"}
