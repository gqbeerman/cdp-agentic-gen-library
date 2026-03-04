import os
from openai import OpenAI
from typing import List

# Target dimension for all embeddings (must match pgvector RPC and existing data)
TARGET_DIMENSIONS = 1536


def get_embeddings(texts: List[str], model: str | None = None, openrouter_api_key: str | None = None, provider_keys: dict[str, str] | None = None) -> List[List[float]]:
    """
    Generate vector embeddings for a list of text chunks.
    Routes to OpenRouter for models with '/' in the name, otherwise uses OpenAI.
    Falls back to env vars when frontend doesn't pass settings.
    """
    if not texts:
        return []
    
    # Resolve embedding model: frontend param → env var → default
    embedding_model = (model.strip() if model and model.strip() else None) \
        or os.getenv("EMBEDDING_MODEL") \
        or "text-embedding-3-small"
    
    # Resolve OpenRouter key: frontend param → provider_keys → env var
    or_key = openrouter_api_key \
        or (provider_keys.get("openrouter") if provider_keys else None) \
        or os.getenv("OPENROUTER_API_KEY")
    if or_key:
        or_key = or_key.strip() if or_key.strip() else None
    
    print(f"[Embeddings] model={embedding_model}, or_key={'present' if or_key else 'missing'}, has_slash={'/' in embedding_model}")
    
    # Route based on model name
    if "/" in embedding_model and or_key:
        # OpenRouter model (e.g. qwen/qwen3-embedding-8b)
        print(f"[Embeddings] Using OpenRouter model: {embedding_model}")
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=or_key
        )
        response = client.embeddings.create(
            input=texts,
            model=embedding_model,
            dimensions=TARGET_DIMENSIONS,
        )
        return [item.embedding for item in response.data]
    else:
        # OpenAI model
        openai_key = (provider_keys.get("openai") if provider_keys else None) or os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=openai_key)
        
        try:
            response = client.embeddings.create(
                input=texts,
                model=embedding_model
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            error_str = str(e)
            # If OpenAI quota is exhausted, fall back to OpenRouter
            if ("429" in error_str or "insufficient_quota" in error_str) and or_key:
                print(f"[Embeddings] OpenAI quota exhausted, falling back to qwen/qwen3-embedding-8b via OpenRouter")
                fallback_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=or_key
                )
                response = fallback_client.embeddings.create(
                    input=texts,
                    model="qwen/qwen3-embedding-8b",
                    dimensions=TARGET_DIMENSIONS,
                )
                return [item.embedding for item in response.data]
            else:
                raise
