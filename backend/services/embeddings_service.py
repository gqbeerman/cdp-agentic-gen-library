import os
from openai import OpenAI
from typing import List

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate vector embeddings for a list of text chunks using OpenAI.
    """
    if not texts:
        return []
        
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # We use text-embedding-3-small as our default embedding model
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    
    # The response is a list of Embedding objects, we just need the float arrays
    return [item.embedding for item in response.data]
