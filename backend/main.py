import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()  # Must be before router imports so env vars are available

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import chat, threads, documents

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: set LangSmith env vars if not already set
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault(
        "LANGCHAIN_PROJECT",
        os.getenv("LANGCHAIN_PROJECT", "agentic-rag-library"),
    )
    yield


app = FastAPI(title="Agentic RAG Library", lifespan=lifespan)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat.router)
app.include_router(threads.router)
app.include_router(documents.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
