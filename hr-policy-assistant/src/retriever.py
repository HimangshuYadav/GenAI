"""
Retriever module: Hybrid Search (Vector + BM25) with Reciprocal Rank Fusion (RRF),
category filtering, similarity thresholding, and query rewriting.
"""
import re
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

from src.config import (
    CHROMA_PERSIST_DIRECTORY,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    BM25_DATA_FILE,
    DEFAULT_TOP_K,
    DEFAULT_SIMILARITY_THRESHOLD,
    RRF_K,
    CATEGORIES_LIST
)

# Singleton caches
_embedder_instance = None
_chroma_client_instance = None


def get_embedder() -> SentenceTransformer:
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedder_instance


def get_chroma_client() -> chromadb.PersistentClient:
    global _chroma_client_instance
    if _chroma_client_instance is None:
        CHROMA_PERSIST_DIRECTORY.mkdir(parents=True, exist_ok=True)
        _chroma_client_instance = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIRECTORY))
    return _chroma_client_instance


class HRRetriever:
    """
    Handles hybrid retrieval across employee handbook chunks using
    cosine vector similarity and BM25 with Reciprocal Rank Fusion.
    """

    def __init__(self):
        self.client = get_chroma_client()
        self.embedder = get_embedder()
        self.collection = None
        self.bm25_data = None
        self._load_indexes()

    def _load_indexes(self):
        """Loads or reloads the ChromaDB collection and BM25 index."""
        try:
            self.collection = self.client.get_collection(name=COLLECTION_NAME)
        except Exception:
            self.collection = None

        if BM25_DATA_FILE.exists():
            try:
                with open(BM25_DATA_FILE, "rb") as f:
                    self.bm25_data = pickle.load(f)
            except Exception:
                self.bm25_data = None
        else:
            self.bm25_data = None

    def is_indexed(self) -> bool:
        """Returns True if collection exists and has at least 1 document."""
        self._load_indexes()
        if self.collection is None:
            return False
        try:
            return self.collection.count() > 0
        except Exception:
            return False

    def count_chunks(self) -> int:
        if self.collection is None:
            return 0
        try:
            return self.collection.count()
        except Exception:
            return 0

    def vector_search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes vector cosine similarity search in ChromaDB.
        """
        if self.collection is None or self.collection.count() == 0:
            return []

        query_embedding = self.embedder.encode([query], normalize_embeddings=True).tolist()
        
        where_filter = None
        if category and category.lower() != "all" and category in CATEGORIES_LIST:
            where_filter = {"category": category}

        total_docs = self.collection.count()
        n_results = min(top_k * 3, total_docs)

        kwargs = {
            "query_embeddings": query_embedding,
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = self.collection.query(**kwargs)

        hits = []
        if results and results["ids"] and len(results["ids"][0]) > 0:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            dists = results["distances"][0]

            for rank, (doc_id, doc, meta, dist) in enumerate(zip(ids, docs, metas, dists)):
                # Chroma cosine distance = 1 - cosine_similarity
                cosine_sim = max(0.0, min(1.0, 1.0 - dist))
                hits.append({
                    "id": doc_id,
                    "text": doc,
                    "metadata": meta,
                    "similarity": round(cosine_sim, 4),
                    "vector_rank": rank + 1
                })
        return hits

    def bm25_search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes BM25 keyword matching over tokenized chunks.
        """
        if self.bm25_data is None:
            return []

        bm25: BM25Okapi = self.bm25_data["bm25"]
        ids = self.bm25_data["ids"]
        docs = self.bm25_data["documents"]
        metas = self.bm25_data["metadatas"]

        query_tokens = re.findall(r"\w+", query.lower())
        if not query_tokens:
            return []

        scores = bm25.get_scores(query_tokens)
        
        # Rank all scored documents
        scored_docs = []
        for idx, score in enumerate(scores):
            if score <= 0:
                continue
            meta = metas[idx]
            if category and category.lower() != "all" and category in CATEGORIES_LIST:
                if meta.get("category") != category:
                    continue
            scored_docs.append({
                "id": ids[idx],
                "text": docs[idx],
                "metadata": meta,
                "bm25_score": float(score)
            })

        scored_docs.sort(key=lambda x: x["bm25_score"], reverse=True)
        for rank, item in enumerate(scored_docs[:top_k * 3]):
            item["bm25_rank"] = rank + 1

        return scored_docs[:top_k * 3]

    def hybrid_search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        category: Optional[str] = None,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD
    ) -> List[Dict[str, Any]]:
        """
        Performs Hybrid Search combining Vector cosine similarity and BM25 keyword ranking
        via Reciprocal Rank Fusion (RRF). Filters out chunks failing similarity threshold.
        """
        self._load_indexes()
        if not self.is_indexed():
            return []

        vec_hits = self.vector_search(query, top_k=top_k, category=category)
        bm25_hits = self.bm25_search(query, top_k=top_k, category=category)

        # Build candidate pool indexed by ID
        candidates: Dict[str, Dict[str, Any]] = {}

        # Process vector hits (weight 1.0)
        for hit in vec_hits:
            doc_id = hit["id"]
            rrf_vec = 1.0 / (RRF_K + hit["vector_rank"])
            candidates[doc_id] = {
                "id": doc_id,
                "text": hit["text"],
                "metadata": hit["metadata"],
                "similarity": hit["similarity"],
                "rrf_score": rrf_vec,
                "page_number": hit["metadata"].get("page_number", 1),
                "section_title": hit["metadata"].get("section_title", "Handbook"),
                "category": hit["metadata"].get("category", "General")
            }

        # Process BM25 hits (weight 0.6)
        for hit in bm25_hits:
            doc_id = hit["id"]
            rrf_bm25 = 0.6 / (RRF_K + hit["bm25_rank"])
            if doc_id in candidates:
                candidates[doc_id]["rrf_score"] += rrf_bm25
            else:
                # Approximate cosine similarity if missing from vector top results
                candidates[doc_id] = {
                    "id": doc_id,
                    "text": hit["text"],
                    "metadata": hit["metadata"],
                    "similarity": 0.38,  # placeholder baseline for strong BM25 hits
                    "rrf_score": rrf_bm25,
                    "page_number": hit["metadata"].get("page_number", 1),
                    "section_title": hit["metadata"].get("section_title", "Handbook"),
                    "category": hit["metadata"].get("category", "General")
                }

        # Sort candidates by combined RRF score
        sorted_candidates = sorted(candidates.values(), key=lambda x: x["rrf_score"], reverse=True)

        # Check threshold: if the top hit has very low similarity, treat as not found
        if not sorted_candidates:
            return []

        # Filter candidates meeting similarity threshold
        filtered = [
            c for c in sorted_candidates
            if c["similarity"] >= similarity_threshold
        ]

        # If vector similarity threshold was too strict but BM25 had strong exact matches,
        # allow top 1 if confidence exists
        if not filtered and sorted_candidates:
            top_cand = sorted_candidates[0]
            if top_cand.get("similarity", 0) >= (similarity_threshold - 0.05):
                filtered = [top_cand]

        return filtered[:top_k]


def rewrite_query_with_context(
    query: str,
    chat_history: List[Dict[str, str]],
    groq_client=None,
    model: str = "llama-3.3-70b-versatile"
) -> str:
    """
    Rewrites follow-up questions into standalone queries using the last 2-3 chat turns.
    Example: 'what about for managers?' -> 'What are the travel hotel limits for managers?'
    """
    if not chat_history or len(chat_history) < 2 or groq_client is None:
        return query

    # Only rewrite if query looks like a follow-up or is short
    is_short = len(query.split()) <= 7
    followup_signals = [
        "what about", "how about", "and for", "can i", "is there",
        "does it", "what if", "carry over", "explain more", "how much", "who"
    ]
    has_signal = any(sig in query.lower() for sig in followup_signals)

    if not (is_short or has_signal):
        return query

    # Format recent 2-3 turns
    recent_history = chat_history[-4:]
    history_lines = []
    for turn in recent_history:
        role = "User" if turn.get("role") == "user" else "Assistant"
        content = turn.get("content", "").replace("\n", " ")
        if len(content) > 180:
            content = content[:180] + "..."
        history_lines.append(f"{role}: {content}")
    history_str = "\n".join(history_lines)

    prompt = (
        "You are an assistant that reformulates follow-up questions into standalone search queries "
        "for a company HR employee handbook search engine.\n\n"
        f"Chat History:\n{history_str}\n\n"
        f"Follow-up Question: {query}\n\n"
        "Instructions: Rewrite the follow-up question into a complete, standalone question/search query "
        "incorporating the referenced subject from the history. "
        "Do NOT answer the question. Return ONLY the rewritten query text."
    )

    try:
        completion = groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=60
        )
        rewritten = completion.choices[0].message.content.strip().strip('"').strip("'")
        if rewritten and len(rewritten) > 3:
            return rewritten
    except Exception:
        pass

    return query

