import os
from openai import OpenAI
from typing import List

def get_embeddings(texts: List[str], model: str | None = None, openrouter_api_key: str | None = None, provider_keys: dict[str, str] | None = None) -> List[List[float]]:
    """
    Generate vector embeddings for a list of text chunks using OpenAI or OpenRouter.
    """
    if not texts:
        return []
        
    # We use text-embedding-3-small as our default embedding model
    embedding_model = model or "text-embedding-3-small"
    
    or_key = openrouter_api_key or (provider_keys.get("openrouter") if provider_keys else None)
    if or_key and "/" in embedding_model:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=or_key
        )
    else:
        openai_key = provider_keys.get("openai") if provider_keys else None
        client = OpenAI(api_key=openai_key or os.getenv("OPENAI_API_KEY"))
    
    response = client.embeddings.create(
        input=texts,
        model=embedding_model
    )
    
    # The response is a list of Embedding objects, we just need the float arrays
    return [item.embedding for item in response.data]
