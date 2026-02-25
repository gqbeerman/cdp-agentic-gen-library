import os
from supabase import create_client, Client
from typing import List, Dict, Any
from io import BytesIO

# Parsers
import pypdf
import docx
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Local services
from . import embeddings_service

# Initialize a standard Supabase service client using the service role key
# so the background task has permissions to download the file and insert chunks
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Important: Use service role key for background tasks
supabase: Client = create_client(supabase_url, supabase_key)

def process_document(document_id: str, user_id: str, storage_path: str, file_type: str):
    """
    Background task to download a document, parse text, chunk it, embed it,
    and store it in the pgvector database.
    """
    try:
        # 1. Mark as processing
        supabase.table("documents").update({"status": "processing"}).eq("id", document_id).execute()
        
        # 2. Download file from Storage
        file_bytes = supabase.storage.from_("documents").download(storage_path)
        
        # 3. Extract text
        text_content = _extract_text(file_bytes, file_type)
        if not text_content.strip():
            raise ValueError("No text could be extracted from this document.")
            
        # 4. Chunk text
        # These numbers can be tuned based on the embedding model and retrieval strategy
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        chunks = text_splitter.split_text(text_content)
        
        if not chunks:
            raise ValueError("Document yielded 0 chunks.")
            
        # 5. Generate embeddings
        # The embedding service expects a list of strings and returns a list of float arrays
        embeddings = embeddings_service.get_embeddings(chunks)
        
        # 6. Store in pgvector
        chunk_records = []
        for i, chunk in enumerate(chunks):
            chunk_records.append({
                "document_id": document_id,
                "user_id": user_id,
                "content": chunk,
                "embedding": embeddings[i],
                "metadata": {
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                    # Could add more metadata here later like title, headers, etc.
                }
            })
            
        # Insert all chunks in a single operation
        supabase.table("document_chunks").insert(chunk_records).execute()
        
        # 7. Mark as ready
        supabase.table("documents").update({
            "status": "ready",
            "chunk_count": len(chunks)
        }).eq("id", document_id).execute()
        
    except Exception as e:
        # If anything fails, mark the document as error
        error_msg = str(e)
        print(f"Error processing document {document_id}: {error_msg}")
        supabase.table("documents").update({
            "status": "error",
            "error_message": error_msg
        }).eq("id", document_id).execute()


def _extract_text(file_bytes: bytes, file_type: str) -> str:
    """Helper to route parsing logic to the correct library based on MIME type."""
    file_io = BytesIO(file_bytes)
    
    if file_type == "application/pdf":
        reader = pypdf.PdfReader(file_io)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
        
    elif "wordprocessingml.document" in file_type: # DOCX
        doc = docx.Document(file_io)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
    elif "html" in file_type:
        soup = BeautifulSoup(file_io, "html.parser")
        return soup.get_text(separator="\n", strip=True)
        
    else:
        # Fallback to plain text decoding (txt, md, csv)
        return file_bytes.decode("utf-8")
