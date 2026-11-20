"""
FastAPI Backend for the HR Policy Assistant React Interface.
Provides streaming SSE chat endpoint, handbook status, re-indexing, and feedback logging.
"""
import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.config import (
    PDF_PATH,
    FEEDBACK_FILE,
    DEFAULT_GROQ_MODEL,
    AVAILABLE_GROQ_MODELS,
    GROQ_API_KEY,
    DEFAULT_TOP_K,
    DEFAULT_SIMILARITY_THRESHOLD,
    CATEGORIES_LIST,
    EMBEDDING_MODEL_NAME
)
from src.retriever import HRRetriever, rewrite_query_with_context
from src.llm import generate_answer_stream, get_groq_client
from src.ingest import index_handbook

app = FastAPI(title="HR Policy Assistant API", version="1.0.0")

# Enable CORS for React frontend (localhost:3000, 5173, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global retriever instance
retriever = HRRetriever()


class ChatRequest(BaseModel):
    query: str
    category: Optional[str] = "All"
    top_k: Optional[int] = DEFAULT_TOP_K
    sim_threshold: Optional[float] = DEFAULT_SIMILARITY_THRESHOLD
    model: Optional[str] = DEFAULT_GROQ_MODEL
    chat_history: Optional[List[Dict[str, str]]] = []
    api_key: Optional[str] = None


class FeedbackRequest(BaseModel):
    query: str
    answer: str
    rating: str  # "up" | "down"
    sources: Optional[List[Dict[str, Any]]] = []


@app.get("/api/status")
def get_status():
    """Returns indexing state, chunk count, and model details."""
    is_indexed = retriever.is_indexed()
    count = retriever.count_chunks() if is_indexed else 0
    key = GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
    has_key = bool(key and key != "your_groq_api_key_here")

    return {
        "indexed": is_indexed,
        "chunk_count": count,
        "pdf_name": PDF_PATH.name if PDF_PATH.exists() else "None",
        "embedding_model": EMBEDDING_MODEL_NAME,
        "default_model": DEFAULT_GROQ_MODEL,
        "available_models": AVAILABLE_GROQ_MODELS,
        "categories": ["All"] + CATEGORIES_LIST,
        "has_api_key": has_key
    }


@app.post("/api/reindex")
def reindex():
    """Triggers handbook re-indexing."""
    if not PDF_PATH.exists():
        raise HTTPException(status_code=404, detail=f"PDF not found at {PDF_PATH}")
    try:
        result = index_handbook(str(PDF_PATH))
        retriever._load_indexes()
        return {
            "status": "success",
            "total_chunks": result["total_chunks"],
            "total_pages": result["total_pages"],
            "category_counts": result["category_counts"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/feedback")
def log_feedback(req: FeedbackRequest):
    """Logs thumbs up/down user feedback to JSON."""
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "query": req.query,
        "answer": req.answer,
        "rating": req.rating,
        "sources": req.sources
    }
    entries = []
    if FEEDBACK_FILE.exists():
        try:
            with open(FEEDBACK_FILE, "r") as f:
                entries = json.load(f)
        except Exception:
            entries = []
    entries.append(entry)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(entries, f, indent=2)
    return {"status": "saved"}


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """
    SSE Streaming Chat Endpoint.
    1. Rewrites follow-up questions
    2. Runs hybrid retrieval (Vector + BM25 RRF)
    3. Sends retrieved sources as the first SSE event
    4. Streams answer tokens
    """
    # 1. Rewrite query if context exists
    groq_client = get_groq_client(req.api_key)
    search_query = rewrite_query_with_context(
        query=req.query,
        chat_history=req.chat_history or [],
        groq_client=groq_client,
        model=req.model or DEFAULT_GROQ_MODEL
    )

    # 2. Hybrid Retrieval with Category filter
    retrieved_chunks = retriever.hybrid_search(
        query=search_query,
        top_k=req.top_k or DEFAULT_TOP_K,
        category=req.category,
        similarity_threshold=req.sim_threshold or DEFAULT_SIMILARITY_THRESHOLD
    )

    async def event_generator():
        # First event: sources metadata
        sources_payload = [
            {
                "id": c.get("id"),
                "section_title": c.get("section_title"),
                "page_number": c.get("page_number"),
                "similarity": c.get("similarity"),
                "category": c.get("category"),
                "text": c.get("text", "")[:350] + "..." if len(c.get("text", "")) > 350 else c.get("text", "")
            }
            for c in retrieved_chunks
        ]
        yield f"event: sources\ndata: {json.dumps(sources_payload)}\n\n"

        # Token streaming
        token_stream = generate_answer_stream(
            query=req.query,
            retrieved_chunks=retrieved_chunks,
            chat_history=req.chat_history,
            model=req.model or DEFAULT_GROQ_MODEL,
            api_key=req.api_key
        )

        for token in token_stream:
            # Send token SSE event
            yield f"event: token\ndata: {json.dumps(token)}\n\n"
            await asyncio.sleep(0.01)  # smooth streaming

        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# Mount React built frontend static files if dist exists
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
