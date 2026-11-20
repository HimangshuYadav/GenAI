"""
Ingestion pipeline: parses handbook PDF, detects headings and sections,
chunks text and tables, generates local sentence embeddings,
and stores in ChromaDB & BM25 index idempotently.
"""
import os
import re
import sys
import pickle
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple

import pymupdf
import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

from src.config import (
    PDF_PATH,
    CHROMA_PERSIST_DIRECTORY,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    BM25_DATA_FILE,
    infer_category,
    CATEGORIES_LIST
)


def extract_tables_from_page(page: pymupdf.Page) -> List[Tuple[str, pymupdf.Rect]]:
    """
    Extracts tables from a PyMuPDF page as formatted Markdown strings,
    returning a list of (markdown_table, bounding_box).
    """
    tables_found = []
    try:
        tabs = page.find_tables()
        for tab in tabs:
            extracted = tab.extract()
            if not extracted or len(extracted) < 2:
                continue
            
            headers = [str(c or "").strip().replace("\n", " ") for c in extracted[0]]
            md_lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
            
            for row in extracted[1:]:
                clean_row = [str(c or "").strip().replace("\n", " ") for c in row]
                md_lines.append("| " + " | ".join(clean_row) + " |")
                
            md_table = "\n".join(md_lines)
            tables_found.append((md_table, tab.bbox))
    except Exception:
        pass
    return tables_found


def is_heading_span(span: Dict[str, Any], text: str) -> Tuple[bool, int]:
    """
    Determines if a span represents a heading based on font size, bold flag,
    and heading regex patterns.
    """
    clean = text.strip()
    if not clean or len(clean) > 140:
        return False, 0
    
    font_name = str(span.get("font", "")).lower()
    font_size = span.get("size", 10.0)
    flags = span.get("flags", 0)
    is_bold = (flags & 2 != 0) or ("bold" in font_name) or ("black" in font_name)

    if re.match(r"^CHAPTER \d+ \| MODULE", clean, re.IGNORECASE):
        return True, 1
    if re.match(r"^SECTION \d+(\.\d+)?:?", clean, re.IGNORECASE):
        return True, 1
    if re.match(r"^\d+\.\s+[A-Z]", clean):
        return True, 2
    if re.match(r"^\d+\.\d+\s+[A-Z]", clean):
        return True, 2

    if font_size >= 15 or (is_bold and font_size >= 13):
        return True, 1
    elif font_size >= 12 or (is_bold and font_size >= 11):
        return True, 2
    
    return False, 0


def recursive_split(text: str, max_tokens: int = 700, overlap_tokens: int = 100) -> List[str]:
    """
    Recursively splits text into chunks under max_tokens with overlap.
    Approximates 1 token ≈ 4 characters.
    """
    max_chars = max_tokens * 4
    overlap_chars = overlap_tokens * 4
    
    if len(text) <= max_chars:
        return [text.strip()] if text.strip() else []

    separators = ["\n\n", "\n• ", "\n- ", "\n", ". ", " "]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        
        if end < len(text):
            split_idx = -1
            search_window = text[start:end]
            for sep in separators:
                pos = search_window.rfind(sep)
                if pos > max_chars // 3:
                    split_idx = start + pos + len(sep)
                    break
            
            if split_idx != -1 and split_idx > start:
                chunk = text[start:split_idx].strip()
                chunks.append(chunk)
                start = max(start + 1, split_idx - overlap_chars)
            else:
                chunk = text[start:end].strip()
                chunks.append(chunk)
                start = max(start + 1, end - overlap_chars)
        else:
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            break
            
    return chunks


def parse_pdf_to_sections(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Parses a PDF document, extracting text, headings, and tables by section.
    Preserves exact page numbers and hierarchical section titles.
    Filters out boilerplate headers and footers.
    """
    doc = pymupdf.open(pdf_path)
    parsed_sections = []
    
    current_chapter = "Employee Handbook Overview"
    current_sub = ""
    current_text_buffer = []
    current_page = 1
    
    # Boilerplate patterns to ignore
    boilerplate_patterns = [
        re.compile(r"^Document Page \d+ of \d+", re.IGNORECASE),
        re.compile(r"^NovaPay Global Human Resources.*Corpus", re.IGNORECASE),
        re.compile(r"^Page \d+ of \d+ \| Confidential", re.IGNORECASE),
        re.compile(r"^={5,}$")
    ]

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page_num = page_idx + 1
        
        # 1. Extract markdown tables
        tables = extract_tables_from_page(page)
        table_bboxes = [bbox for _, bbox in tables]
        
        for md_table, _ in tables:
            active_section = f"{current_chapter} - {current_sub}" if current_sub else current_chapter
            parsed_sections.append({
                "page_number": page_num,
                "section_title": active_section,
                "text": md_table,
                "is_table": True
            })

        # 2. Extract text blocks / lines
        text_content = page.get_text()
        raw_lines = [l.strip() for l in text_content.split("\n") if l.strip()]

        for line in raw_lines:
            # Check boilerplate
            if any(bp.search(line) for bp in boilerplate_patterns):
                continue
            
            # Check heading markers
            is_chap = bool(re.match(r"^CHAPTER \d+ \| MODULE", line, re.IGNORECASE))
            is_sec = bool(re.match(r"^SECTION \d+(\.\d+)?:?", line, re.IGNORECASE))
            is_clause = bool(re.match(r"^\d+\.\s+[A-Z]", line))

            if is_chap or is_sec or is_clause:
                # Flush existing buffer
                if current_text_buffer:
                    sec_text = "\n".join(current_text_buffer).strip()
                    if sec_text:
                        active_sec = f"{current_chapter} - {current_sub}" if current_sub else current_chapter
                        parsed_sections.append({
                            "page_number": current_page,
                            "section_title": active_sec,
                            "text": sec_text,
                            "is_table": False
                        })
                    current_text_buffer = []
                
                current_page = page_num
                if is_chap:
                    current_chapter = line
                    current_sub = ""
                elif is_sec:
                    current_chapter = line
                    current_sub = ""
                else:
                    current_sub = line
                continue

            current_text_buffer.append(line)
            current_page = page_num

    # Flush remaining buffer
    if current_text_buffer:
        sec_text = "\n".join(current_text_buffer).strip()
        if sec_text:
            active_sec = f"{current_chapter} - {current_sub}" if current_sub else current_chapter
            parsed_sections.append({
                "page_number": current_page,
                "section_title": active_sec,
                "text": sec_text,
                "is_table": False
            })

    doc.close()
    return parsed_sections


def chunk_sections(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Converts extracted sections into fine-grained chunks (~600-800 tokens max),
    attaching metadata: page_number, section_title, category, chunk_id.
    """
    final_chunks = []
    chunk_counter = 0

    for sec in sections:
        text = sec["text"].strip()
        page_num = sec["page_number"]
        sec_title = sec["section_title"]
        is_table = sec.get("is_table", False)

        if not text:
            continue

        category = infer_category(text, heading=sec_title)

        if is_table:
            chunk_counter += 1
            doc_text = f"Table from {sec_title} (p. {page_num}):\n{text}"
            final_chunks.append({
                "chunk_id": f"chunk_p{page_num}_{chunk_counter}",
                "text": doc_text,
                "page_number": page_num,
                "section_title": sec_title,
                "category": category,
                "is_table": True
            })
        else:
            sub_chunks = recursive_split(text, max_tokens=700, overlap_tokens=100)
            for sub_text in sub_chunks:
                chunk_counter += 1
                doc_text = f"Section: {sec_title} (p. {page_num})\n{sub_text}"
                final_chunks.append({
                    "chunk_id": f"chunk_p{page_num}_{chunk_counter}",
                    "text": doc_text,
                    "page_number": page_num,
                    "section_title": sec_title,
                    "category": category,
                    "is_table": False
                })

    return final_chunks


def index_handbook(pdf_path: str = None) -> Dict[str, Any]:
    """
    Main ingestion function:
    1. Parses PDF
    2. Chunks text & tables
    3. Computes embeddings using BAAI/bge-small-en-v1.5
    4. Stores idempotent collection in ChromaDB
    5. Builds & saves BM25 index for hybrid search
    """
    target_pdf = Path(pdf_path) if pdf_path else PDF_PATH
    if not target_pdf.exists():
        raise FileNotFoundError(f"Handbook PDF not found at: {target_pdf}")

    print(f"📖 Parsing handbook PDF from: {target_pdf} ...")
    raw_sections = parse_pdf_to_sections(str(target_pdf))
    chunks = chunk_sections(raw_sections)

    if not chunks:
        raise ValueError(f"No extractable text or tables found in: {target_pdf}")

    total_pages = max(c["page_number"] for c in chunks)
    print(f"🧩 Created {len(chunks)} chunks across {total_pages} pages.")

    # Category stats
    cat_counts = {}
    for c in chunks:
        cat_counts[c["category"]] = cat_counts.get(c["category"], 0) + 1
    for cat, count in sorted(cat_counts.items()):
        print(f"   • {cat}: {count} chunks")

    # Load SentenceTransformer model
    print(f"⚡ Loading local embedding model: {EMBEDDING_MODEL_NAME} ...")
    embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    
    texts_to_embed = [c["text"] for c in chunks]
    print(f"🔢 Generating embeddings for {len(texts_to_embed)} chunks...")
    embeddings = embedder.encode(texts_to_embed, show_progress_bar=False, normalize_embeddings=True)

    # Initialize ChromaDB persistent client
    CHROMA_PERSIST_DIRECTORY.mkdir(parents=True, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIRECTORY))

    # Idempotent collection reset
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
        print(f"🔄 Replaced existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    ids = [c["chunk_id"] for c in chunks]
    metadatas = [{
        "page_number": int(c["page_number"]),
        "section_title": str(c["section_title"]),
        "category": str(c["category"]),
        "is_table": bool(c.get("is_table", False)),
        "source": str(target_pdf.name)
    } for c in chunks]

    collection.add(
        ids=ids,
        documents=texts_to_embed,
        metadatas=metadatas,
        embeddings=embeddings.tolist()
    )
    print(f"💾 Stored {len(ids)} chunks in ChromaDB at {CHROMA_PERSIST_DIRECTORY}")

    # Build and save BM25 corpus data for hybrid search
    print("🔍 Building BM25 index for hybrid retrieval...")
    tokenized_corpus = [
        re.findall(r"\w+", doc_text.lower())
        for doc_text in texts_to_embed
    ]
    bm25_index = BM25Okapi(tokenized_corpus)

    bm25_payload = {
        "bm25": bm25_index,
        "tokenized_corpus": tokenized_corpus,
        "ids": ids,
        "documents": texts_to_embed,
        "metadatas": metadatas
    }
    with open(BM25_DATA_FILE, "wb") as f:
        pickle.dump(bm25_payload, f)
    print(f"📦 BM25 index saved to {BM25_DATA_FILE}")

    return {
        "status": "success",
        "total_chunks": len(chunks),
        "total_pages": total_pages,
        "category_counts": cat_counts
    }


def main():
    parser = argparse.ArgumentParser(description="Ingest Employee Handbook PDF into ChromaDB & BM25")
    parser.add_argument("--pdf", type=str, default=str(PDF_PATH), help="Path to handbook PDF")
    args = parser.parse_args()

    try:
        result = index_handbook(args.pdf)
        print("\n✅ Ingestion completed successfully!")
        print(f"Total Chunks: {result['total_chunks']}")
        print(f"Total Pages:  {result['total_pages']}")
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
