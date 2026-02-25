from typing import List, Dict, Any
from pydantic import BaseModel, Field

from supabase import create_client, Client
import os

from services import embeddings_service

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key)

class SearchKnowledgeBaseArgs(BaseModel):
    query: str = Field(..., description="The search query to look up in the knowledge base. This should be a concise statement or question capturing the user's intent.")

async def search_knowledge_base(query: str, user_id: str, limit: int = 5) -> str:
    """
    Search the vector database for chunks most similar to the query.
    """
    try:
        print(f"[Tool] Executing search_knowledge_base for query: '{query}'")
        
        # 1. Embed the search query
        query_embedding = embeddings_service.get_embeddings([query])[0]
        
        # 2. Call the RPC function via Supabase
        response = supabase.rpc(
            "match_document_chunks",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.1, # Allow looser matches for testing
                "match_count": limit,
                "p_user_id": user_id
            }
        ).execute()
        
        results = response.data
        if not results:
            return "No relevant information found in the knowledge base."
            
        # 3. Format the returned chunks into a string for the LLM
        formatted_chunks = []
        for i, match in enumerate(results):
            content = match.get("content", "").strip()
            similarity = match.get("similarity", 0)
            metadata = match.get("metadata", {})
            
            # Extract page number or default to chunk index
            page_num = metadata.get("page")
            if page_num is not None:
                source_info = f"[Page {page_num} | Chunk {i+1} | Sim: {similarity:.2f}]"
            else:
                source_info = f"[Section {i+1} | Sim: {similarity:.2f}]"
            
            formatted_chunks.append(f"{source_info}\n{content}")
            
        final_str = "\n\n---\n\n".join(formatted_chunks)
        return f"Found {len(results)} relevant passages in the knowledge base:\n\n{final_str}"
        
    except Exception as e:
        print(f"[Tool Error] search_knowledge_base failed: {e}")
        return f"Error executing search: {str(e)}"

# Define the tool schema for OpenAI
retrieval_tool_schema = {
    "type": "function",
    "function": {
        "name": "search_knowledge_base",
        "description": "Searches the user's uploaded documents for relevant information. Call this tool when the user asks a question that requires specific knowledge or facts that might be in their files.",
        "parameters": SearchKnowledgeBaseArgs.model_json_schema()
    }
}
