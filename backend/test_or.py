import openai
import json

key = "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"
url = "https://openrouter.ai/api/v1"

client = openai.OpenAI(
    base_url=url, 
    api_key=key,
    default_headers={
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "CDP Agentic Gen Library",
    }
)

try:
    response = client.chat.completions.create(
        model="meta-llama/llama-3.2-3b-instruct:free",
        messages=[{"role": "user", "content": "which llm are you?"}]
    )
    print("Response from meta-llama/llama-3.2-3b-instruct:free:")
    print(response.choices[0].message.content)
except Exception as e:
    print("Error:", e)
