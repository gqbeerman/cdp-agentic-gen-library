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
        extracted_docs = _extract_text(file_bytes, file_type)
        if not extracted_docs:
            raise ValueError("No text could be extracted from this document.")
            
        # 4. Chunk text
        # These numbers can be tuned based on the embedding model and retrieval strategy
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        
        texts = [doc["text"] for doc in extracted_docs]
        metadatas = [doc["metadata"] for doc in extracted_docs]
        
        # This preserves the metadata for each generated chunk
        chunked_docs = text_splitter.create_documents(texts, metadatas=metadatas)
        
        if not chunked_docs:
            raise ValueError("Document yielded 0 chunks.")
            
        # 5. Generate embeddings
        # The embedding service expects a list of strings and returns a list of float arrays
        chunks = [doc.page_content for doc in chunked_docs]
        embeddings = embeddings_service.get_embeddings(chunks)
        
        # 6. Store in pgvector
        chunk_records = []
        for i, doc in enumerate(chunked_docs):
            # Base metadata with chunk indices
            meta = {
                "chunk_index": i,
                "total_chunks": len(chunked_docs)
            }
            # Add the preserved document metadata (e.g. page number)
            meta.update(doc.metadata)
            
            chunk_records.append({
                "document_id": document_id,
                "user_id": user_id,
                "content": doc.page_content,
                "embedding": embeddings[i],
                "metadata": meta
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


def _extract_text(file_bytes: bytes, file_type: str) -> List[Dict[str, Any]]:
    """Helper to route parsing logic to the correct library based on MIME type.
    Returns a list of dicts containing 'text' and 'metadata'.
    """
    file_io = BytesIO(file_bytes)
    documents = []
    
    if file_type == "application/pdf":
        reader = pypdf.PdfReader(file_io)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                documents.append({"text": text, "metadata": {"page": i + 1}})
                
    elif "wordprocessingml.document" in file_type: # DOCX
        doc = docx.Document(file_io)
        # For DOCX, we treat paragraphs dynamically as "sections" or just aggregate
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
        if text:
            documents.append({"text": text, "metadata": {}})
        
    elif "html" in file_type:
        soup = BeautifulSoup(file_io, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        if text:
            documents.append({"text": text, "metadata": {}})
        
    else:
        # Fallback to plain text decoding (txt, md, csv)
        text = file_bytes.decode("utf-8")
        if text.strip():
            documents.append({"text": text, "metadata": {}})
            
    return documents
