"""
Streamlit Web Application: HR Policy Assistant
Featuring custom CSS (Inter font, Light/Dark mode, clean rounded cards),
hybrid search, topic filtering, query rewriting, streaming responses,
collapsible sources with similarity scores, and persistent thumbs feedback.
"""
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import streamlit as st

# Configure page layout first
st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.config import (
    PDF_PATH,
    FEEDBACK_FILE,
    DEFAULT_GROQ_MODEL,
    AVAILABLE_GROQ_MODELS,
    GROQ_API_KEY,
    DEFAULT_TOP_K,
    DEFAULT_SIMILARITY_THRESHOLD,
    CATEGORIES_LIST,
    HR_CONTACT_EMAIL,
    DISCLAIMER_NOTE
)
from src.retriever import HRRetriever, rewrite_query_with_context
from src.llm import generate_answer_stream, get_groq_client
from src.ingest import index_handbook


# ================= INITIALIZE STATE =================
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

if "selected_category" not in st.session_state:
    st.session_state["selected_category"] = "All"

if "api_key" not in st.session_state:
    st.session_state["api_key"] = GROQ_API_KEY

if "retriever" not in st.session_state:
    st.session_state["retriever"] = HRRetriever()

if "pending_prompt" not in st.session_state:
    st.session_state["pending_prompt"] = None


# ================= FEEDBACK HELPER =================
def save_feedback(query: str, answer: str, rating: str, sources: List[Dict[str, Any]]):
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "answer": answer,
        "rating": rating,
        "sources": [
            {
                "section": s.get("section_title"),
                "page": s.get("page_number"),
                "similarity": s.get("similarity")
            }
            for s in sources
        ]
    }
    existing_entries = []
    if FEEDBACK_FILE.exists():
        try:
            with open(FEEDBACK_FILE, "r") as f:
                existing_entries = json.load(f)
        except Exception:
            existing_entries = []
    existing_entries.append(feedback_entry)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(existing_entries, f, indent=2)


# ================= CUSTOM CSS & THEME =================
def inject_custom_css(dark_mode: bool):
    if dark_mode:
        bg_main = "#0f172a"
        bg_card = "#1e293b"
        text_primary = "#f8fafc"
        text_secondary = "#94a3b8"
        border_color = "#334155"
        accent_color = "#3b82f6"
        accent_light = "#1e3a8a"
        user_bubble = "#1e293b"
        bot_bubble = "#0b1329"
    else:
        bg_main = "#f8fafc"
        bg_card = "#ffffff"
        text_primary = "#0f172a"
        text_secondary = "#64748b"
        border_color = "#e2e8f0"
        accent_color = "#2563eb"
        accent_light = "#eff6ff"
        user_bubble = "#f1f5f9"
        bot_bubble = "#ffffff"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif !important;
    }}

    /* Hide Streamlit header, menu, footer */
    #MainMenu {{visibility: hidden !important;}}
    header {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display: none !important;}}

    /* Global page styling */
    .stApp {{
        background-color: {bg_main};
        color: {text_primary};
    }}

    /* App Header Banner */
    .app-header-container {{
        background: linear-gradient(135deg, {accent_color} 0%, #1e40af 100%);
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 24px;
        color: white;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.15);
    }}
    .app-header-title {{
        font-size: 26px;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .app-header-tagline {{
        font-size: 14px;
        opacity: 0.9;
        margin-top: 6px;
        margin-bottom: 0;
    }}

    /* Status Pill */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-top: 10px;
    }}
    .status-dot-active {{
        height: 8px;
        width: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        display: inline-block;
    }}
    .status-dot-inactive {{
        height: 8px;
        width: 8px;
        background-color: #f59e0b;
        border-radius: 50%;
        display: inline-block;
    }}

    /* Example Cards */
    .welcome-card-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 16px;
        margin: 20px 0;
    }}
    .welcome-card {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 18px;
        transition: all 0.2s ease-in-out;
        cursor: pointer;
    }}
    .welcome-card:hover {{
        border-color: {accent_color};
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
        transform: translateY(-2px);
    }}
    .welcome-card-topic {{
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: {accent_color};
        margin-bottom: 6px;
    }}
    .welcome-card-query {{
        font-size: 13.5px;
        font-weight: 500;
        color: {text_primary};
        line-height: 1.4;
    }}

    /* Source Citation Cards */
    .source-box {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-left: 4px solid {accent_color};
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        font-size: 13px;
    }}
    .source-header {{
        display: flex;
        justify-content: space-between;
        font-weight: 600;
        color: {accent_color};
        margin-bottom: 6px;
    }}
    .source-badge {{
        background: {accent_light};
        color: {accent_color};
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }}
    .source-snippet {{
        color: {text_secondary};
        font-family: monospace;
        font-size: 12px;
        white-space: pre-wrap;
    }}

    /* Sidebar Clean styling */
    section[data-testid="stSidebar"] {{
        background-color: {bg_card};
        border-right: 1px solid {border_color};
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ================= SIDEBAR COMPONENT =================
def render_sidebar(retriever: HRRetriever):
    with st.sidebar:
        st.markdown("### ⚙️ Assistant Controls")

        # Dark mode toggle
        dark_toggle = st.toggle("🌙 Dark Mode", value=st.session_state["dark_mode"])
        if dark_toggle != st.session_state["dark_mode"]:
            st.session_state["dark_mode"] = dark_toggle
            st.rerun()

        st.markdown("---")

        # Topic Filter Chips
        st.markdown("#### 🏷️ Topic Quick Filter")
        categories_options = ["All"] + CATEGORIES_LIST
        selected_cat = st.radio(
            "Filter retrieval context:",
            categories_options,
            index=categories_options.index(st.session_state["selected_category"]),
            help="Restricts RAG retrieval to specific policy sections"
        )
        if selected_cat != st.session_state["selected_category"]:
            st.session_state["selected_category"] = selected_cat

        st.markdown("---")

        # Action Buttons
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state["messages"] = []
                st.rerun()
        with col_btn2:
            reindex_clicked = st.button("🔄 Re-index", use_container_width=True, help="Re-index handbook PDF into ChromaDB")

        if reindex_clicked:
            if not PDF_PATH.exists():
                st.error(f"Handbook PDF not found at: `{PDF_PATH}`. Please place it in `data/` folder.")
            else:
                with st.spinner("Re-indexing handbook PDF into ChromaDB & BM25..."):
                    try:
                        result = index_handbook(str(PDF_PATH))
                        retriever._load_indexes()
                        st.success(f"Indexed {result['total_chunks']} chunks from {result['total_pages']} pages!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ingestion failed: {e}")

        # Settings Expander
        with st.expander("🛠️ Advanced Settings", expanded=False):
            st.markdown("**LLM & Retrieval Configuration**")
            
            # API Key Input
            custom_key = st.text_input(
                "Groq API Key",
                type="password",
                value=st.session_state["api_key"],
                help="Set GROQ_API_KEY. Stored only in your current session."
            )
            if custom_key != st.session_state["api_key"]:
                st.session_state["api_key"] = custom_key

            # Model Dropdown
            selected_model = st.selectbox(
                "Groq Model",
                AVAILABLE_GROQ_MODELS,
                index=0,
                help="Select LLM model for answer generation"
            )

            # Top-k slider
            top_k = st.slider(
                "Top-K Chunks",
                min_value=1,
                max_value=10,
                value=DEFAULT_TOP_K,
                help="Number of chunks retrieved for context"
            )

            # Similarity Threshold
            sim_threshold = st.slider(
                "Similarity Threshold",
                min_value=0.10,
                max_value=0.80,
                value=DEFAULT_SIMILARITY_THRESHOLD,
                step=0.05,
                help="Minimum cosine similarity required to consider chunks relevant"
            )

        # Document Status Info
        st.markdown("---")
        st.markdown("#### 📄 Document Info")
        pdf_name = PDF_PATH.name if PDF_PATH.exists() else "No PDF found"
        st.caption(f"**Source:** `{pdf_name}`")
        st.caption(f"**Chunks:** `{retriever.count_chunks()}` indexed")
        st.caption(f"**Embeddings:** `bge-small-en-v1.5`")
        st.caption(f"**Vector Store:** `ChromaDB` (persistent)")

    return selected_model, top_k, sim_threshold


# ================= MAIN UI COMPONENT =================
def main():
    inject_custom_css(st.session_state["dark_mode"])
    retriever: HRRetriever = st.session_state["retriever"]

    # Render Sidebar
    selected_model, top_k, sim_threshold = render_sidebar(retriever)

    # App Header
    is_indexed = retriever.is_indexed()
    chunk_count = retriever.count_chunks()
    
    status_dot = "status-dot-active" if is_indexed else "status-dot-inactive"
    status_text = f"Handbook Indexed ({chunk_count} chunks)" if is_indexed else "Handbook Not Indexed (Click Re-index)"

    st.markdown(
        f"""
        <div class="app-header-container">
            <div class="app-header-title">
                <span>💼</span> NovaPay HR Policy Assistant
            </div>
            <p class="app-header-tagline">
                Instant, authoritative answers from the official Employee Handbook with verifiable citations
            </p>
            <div class="status-badge">
                <span class="{status_dot}"></span> {status_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Check if API key is configured
    current_key = (st.session_state["api_key"] or GROQ_API_KEY).strip()
    if not current_key or current_key == "your_groq_api_key_here":
        st.warning(
            "🔑 **Groq API Key Required:** Please configure `GROQ_API_KEY` in `.env` "
            "or enter it in the **Sidebar Settings** (under Advanced Settings) to generate answers."
        )

    # Empty Chat Welcome State: 6 Clickable Example Cards
    if len(st.session_state["messages"]) == 0:
        st.markdown("### 👋 Welcome! Select a topic or ask any handbook question below:")
        
        example_questions = [
            ("💰 Compensation", "What are the rules and cycle for annual performance calibration and promotion?"),
            ("📈 ESOP & Equity", "What is the vesting schedule and cliff for Band-3 engineers?"),
            ("🍽️ Cafeteria", "What are the cafeteria operating hours and meal facilities provided?"),
            ("✈️ Travel", "What is the maximum daily hotel lodging reimbursement cap for international travel in Tier-1 cities?"),
            ("🏖️ Leave", "What are the parental and paternity leave entitlements and time limits?"),
            ("🏥 Benefits", "What are the attendance expectations and home-office ergonomic stipend policies?")
        ]

        # Render 2 rows of 3 columns
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3, col1, col2, col3]
        
        for idx, (topic, q_text) in enumerate(example_questions):
            col = cols[idx]
            with col:
                st.markdown(f"**{topic}**")
                if st.button(f"👉 {q_text}", key=f"ex_btn_{idx}", use_container_width=True):
                    st.session_state["pending_prompt"] = q_text
                    st.rerun()

        st.markdown("---")

    # Render Existing Chat History
    for msg_idx, msg in enumerate(st.session_state["messages"]):
        with st.chat_message(msg["role"], avatar="🧑‍💼" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])

            # If message is assistant and has sources, show expandable sources section
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander(f"📚 View {len(msg['sources'])} Cited Sources", expanded=False):
                    for s_idx, src in enumerate(msg["sources"], 1):
                        sim_pct = int(src.get("similarity", 0) * 100)
                        st.markdown(
                            f"""
                            <div class="source-box">
                                <div class="source-header">
                                    <span>#{s_idx} • {src.get('section_title', 'Handbook')}</span>
                                    <span class="source-badge">Page {src.get('page_number', '?')} • Match: {sim_pct}%</span>
                                </div>
                                <div class="source-snippet">{src.get('text', '')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                # Feedback Buttons
                fb_col1, fb_col2, fb_col3 = st.columns([1, 1, 10])
                with fb_col1:
                    if st.button("👍", key=f"fb_up_{msg_idx}", help="Helpful answer"):
                        save_feedback(msg.get("user_query", ""), msg["content"], "up", msg["sources"])
                        st.toast("Thank you for your feedback! 👍")
                with fb_col2:
                    if st.button("👎", key=f"fb_down_{msg_idx}", help="Needs improvement"):
                        save_feedback(msg.get("user_query", ""), msg["content"], "down", msg["sources"])
                        st.toast("Thank you for your feedback! 👎")

    # Handle incoming input (from chat_input or clicked example card)
    prompt = st.chat_input("Ask a question about employee policies, benefits, travel, or leave...")
    if st.session_state["pending_prompt"]:
        prompt = st.session_state["pending_prompt"]
        st.session_state["pending_prompt"] = None

    if prompt:
        # Display user message
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💼"):
            st.markdown(prompt)

        # Assistant generation
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Searching employee handbook..."):
                # 1. Query rewriting for follow-ups
                groq_client = get_groq_client(st.session_state["api_key"])
                search_query = rewrite_query_with_context(
                    query=prompt,
                    chat_history=st.session_state["messages"][:-1],
                    groq_client=groq_client,
                    model=selected_model
                )

                # 2. Hybrid Retrieval with Category Filter
                cat_filter = st.session_state["selected_category"]
                retrieved_chunks = retriever.hybrid_search(
                    query=search_query,
                    top_k=top_k,
                    category=cat_filter,
                    similarity_threshold=sim_threshold
                )

            # 3. Stream Response
            response_container = st.empty()
            full_response = ""

            stream = generate_answer_stream(
                query=prompt,
                retrieved_chunks=retrieved_chunks,
                chat_history=st.session_state["messages"][:-1],
                model=selected_model,
                api_key=st.session_state["api_key"]
            )

            for chunk_token in stream:
                full_response += chunk_token
                response_container.markdown(full_response + "▌")
            response_container.markdown(full_response)

            # 4. Show Sources below streamed answer
            if retrieved_chunks and "I couldn't find this in the employee handbook" not in full_response:
                with st.expander(f"📚 View {len(retrieved_chunks)} Cited Sources", expanded=False):
                    for s_idx, src in enumerate(retrieved_chunks, 1):
                        sim_pct = int(src.get("similarity", 0) * 100)
                        st.markdown(
                            f"""
                            <div class="source-box">
                                <div class="source-header">
                                    <span>#{s_idx} • {src.get('section_title', 'Handbook')}</span>
                                    <span class="source-badge">Page {src.get('page_number', '?')} • Match: {sim_pct}%</span>
                                </div>
                                <div class="source-snippet">{src.get('text', '')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            # Store in session state
            st.session_state["messages"].append({
                "role": "assistant",
                "content": full_response,
                "sources": retrieved_chunks,
                "user_query": prompt
            })


if __name__ == "__main__":
    main()

