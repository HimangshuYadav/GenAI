# GenAI Projects

This repository hosts Generative AI and Retrieval-Augmented Generation (RAG) applications.

## Projects

### 💼 [HR Policy Assistant](./hr-policy-assistant)
An enterprise RAG assistant that answers employee questions strictly from company employee handbooks and HR policy manuals with verifiable citations, hybrid search, category filtering, and both React & Streamlit interfaces.

- **Frontend:** React 18 + Vite (Inter font, dark mode, collapsible citations, real-time SSE token streaming) and Streamlit dashboard.
- **Backend:** FastAPI with SSE streaming & Python RAG pipeline.
- **LLM:** Groq API (`llama-3.3-70b-versatile` / `qwen/qwen3.8-27b`) with strict anti-hallucination prompting (`temp=0.1`).
- **Embeddings:** Local `BAAI/bge-small-en-v1.5` (via `sentence-transformers`, running 100% locally).
- **Vector Store:** ChromaDB persistent collection with BM25 Reciprocal Rank Fusion (RRF).
- **PDF Ingestion:** PyMuPDF (`pymupdf`) with chapter/section hierarchy detection, Markdown table preservation, and page tracking.

👉 See the complete documentation and setup guide in the [HR Policy Assistant README](./hr-policy-assistant/README.md).
