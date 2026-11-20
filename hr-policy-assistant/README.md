# 💼 HR Policy Assistant (RAG-Based Employee Handbook System)

An enterprise-ready, retrieval-augmented generation (RAG) assistant that answers employee questions strictly from official company employee handbooks and HR policy manuals, complete with verifiable citations, hybrid search, category filtering, and a modern Streamlit web interface.

---

## 📌 Architecture & Tech Stack

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Language** | Python 3.11+ | Tested on Python 3.12 |
| **LLM** | Groq API (`groq` SDK) | Model `llama-3.3-70b-versatile` (configurable), `temp=0.1` |
| **Embeddings** | Local `sentence-transformers` | `BAAI/bge-small-en-v1.5` (133MB, runs fully local, no cloud embeddings) |
| **Vector Database** | ChromaDB (`chromadb`) | Local persistent storage at `./chroma_db` (cosine similarity) |
| **Lexical Search** | BM25 (`rank-bm25`) | Hybrid Vector + BM25 retrieval via Reciprocal Rank Fusion (RRF) |
| **PDF Parsing** | PyMuPDF (`pymupdf`) | Hierarchical chapter/section detection, table preservation, page tracking |
| **UI (React)** | React 18 + Vite | Standalone modern SPA with real-time SSE streaming, Inter typography, dark mode |
| **UI (Streamlit)** | Streamlit | Python native dashboard with custom CSS & dark mode toggle |

---

## 📂 Project Structure

```text
hr-policy-assistant/
├── data/
│   ├── novapay_global_hr_manual_50p.pdf  # 50-page official HR reference manual
│   ├── handbook.pdf                      # Active handbook symlink/copy
│   └── feedback.json                     # Persistent thumbs up/down logs
├── src/
│   ├── __init__.py
│   ├── config.py                         # Environment variables, categories, constants
│   ├── ingest.py                         # PDF parsing, section chunking, embedding, ChromaDB & BM25 indexing
│   ├── retriever.py                      # Vector search, BM25, RRF hybrid fusion, query rewriting
│   └── llm.py                            # Groq client, streaming, strict grounding prompt
├── app.py                                # Streamlit UI with custom CSS & dark mode toggle
├── test_assistant.py                     # 15-question automated verification suite
├── requirements.txt                      # Pinned Python package dependencies
├── .env.example                          # Environment template
├── .env                                  # Local environment configuration
├── TEST_REPORT.md                        # Quality check report (15/15 passed)
└── README.md                             # Documentation & setup guide
```

---

## 🚀 Setup & Installation

### 1. Clone & Navigate to Project Directory
```bash
cd hr-policy-assistant
```

### 2. Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate      # On Linux/macOS
# .\venv\Scripts\activate     # On Windows
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` and set your Groq API key:
```ini
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
PDF_PATH=./data/novapay_global_hr_manual_50p.pdf
```
> **Note:** If you don't set `GROQ_API_KEY` in `.env`, you can also enter it directly into the **Sidebar Settings** inside the Streamlit web app.

### 5. Ingest and Index the Employee Handbook
Run the ingestion pipeline via the CLI:
```bash
python -m src.ingest
```
Expected output:
```text
📖 Parsing handbook PDF from: data/novapay_global_hr_manual_50p.pdf ...
🧩 Created 194 chunks across 50 pages.
   • Compensation: 37 chunks
   • ESOP: 1 chunks
   • General: 154 chunks
   • Leave: 1 chunks
   • Travel: 1 chunks
⚡ Loading local embedding model: BAAI/bge-small-en-v1.5 ...
💾 Stored 194 chunks in ChromaDB at ./chroma_db
📦 BM25 index saved to ./chroma_db/bm25_data.pkl
✅ Ingestion completed successfully!
```

---

## 💻 Running the Web Applications

### Option A: Modern React Interface (Recommended)
You can run the React UI in production mode or development mode:

**1. Production Mode (Single Command):**
The FastAPI backend serves the compiled production React app directly:
```bash
python3 -m uvicorn src.api:app --host 0.0.0.0 --port 8080
```
Open **`http://localhost:8080`** in your browser.

**2. Development Mode (Hot-Reloading):**
In one terminal, start the API:
```bash
python3 -m uvicorn src.api:app --host 0.0.0.0 --port 8080
```
In a second terminal, start the React Vite dev server:
```bash
cd frontend && npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

### Option B: Streamlit Interface
To use the Streamlit application instead:
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

### UI Highlights:
- **Header & Status Indicator:** Displays whether the handbook is currently indexed (`🟢 Handbook Indexed (194 chunks)`).
- **Light / Dark Mode:** Toggle at the top of the sidebar.
- **Topic Quick Filters:** Select chips (`Compensation`, `ESOP`, `Cafeteria`, `Travel`, `Leave`, `Benefits`, `All`) to narrow the context pool.
- **Empty State Quick Cards:** Click any of the 6 topic cards to instantly ask common policy questions.
- **Token-by-Token Streaming:** Fast response streaming using Groq's high-speed inference.
- **Collapsible Sources:** Expandable source panel showing excerpt text, exact page numbers, section headers, and percentage relevance matches.
- **Feedback Buttons:** 👍 / 👎 rating stored locally to `data/feedback.json`.
- **Re-Index Button:** Re-processes the handbook directly from the UI with one click.

---

## 🧪 Verification & Quality Checks

Run the automated 15-question evaluation suite:
```bash
python test_assistant.py
```

### Test Results Summary:
- **In-Scope Tests (12/12 Passed):**
  - **Compensation:** Promotion cycles and performance calibration (p. 1, p. 21).
  - **ESOPs:** 4-year vesting, 1-year cliff, 25% initial vest, quarterly installments for Band-3 engineers (p. 11).
  - **Travel:** $350 USD/night hotel lodging cap for Tier-1 international cities (London, NY, Tokyo, Zurich, Singapore), VP Finance approval requirement (p. 27).
  - **Leave:** 6 weeks (30 working days) 100% paid paternity leave, valid within 6 months of childbirth/adoption (p. 39).
  - **Benefits:** Hybrid attendance expectations and home-office ergonomic stipends (p. 4).
  - **Cafeteria:** Correctly identifies absent policy in current manual and triggers fallback without hallucination.
- **Out-of-Scope Tests (3/3 Passed):**
  - General knowledge / sports ("Who won the cricket match?") -> Strictly returns:
    `"I couldn't find this in the employee handbook. Please contact HR at hr@company.com."`
- **Total:** **15 / 15 Passed (100%)**. See [TEST_REPORT.md](TEST_REPORT.md) for complete question-by-question trace logs.

---

## 🛡️ Grounding & Anti-Hallucination Rules

The system prompt enforces strict constraints:
1. **Strict Grounding:** The assistant answers exclusively using retrieved context. It never uses pre-trained general knowledge for company policy.
2. **Missing Information Policy:** When a policy is not documented in the handbook, it replies strictly with:
   `"I couldn't find this in the employee handbook. Please contact HR at hr@company.com."`
3. **Structured Format:** Short summary first, followed by bulleted details quoting exact figures, caps, timelines, and bands.
4. **Citations:** Every fact is cited as `(Section Name, p. X)`.
5. **HR Authority Note:** Appends a standard disclaimer that HR is the final authority on policy interpretation.

---

## ⚠️ Limitations & Considerations

1. **Scanned Documents:** The PDF parser expects digital text. Scanned document images without an embedded text layer require pre-OCR processing (e.g. `pytesseract` or Google Cloud Vision).
2. **Groq API Rate Limits:** Free-tier Groq API keys have rate limits (requests per minute). The UI handles rate limits gracefully with retry prompts.
3. **Complex Nested Tables:** Extremely wide or merged-cell tables are converted to Markdown; while row integrity is maintained, complex multi-header spans may require verification against the original PDF.
4. **Policy Scope:** Policy interpretations are strictly informational; final authority rests with the Human Resources department.

