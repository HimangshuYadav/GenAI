"""
Configuration and constants for the HR Policy Assistant.
"""
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Base directory: hr-policy-assistant root
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent

# Load .env file from project root
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv(find_dotenv())

# File & Directory Paths
DATA_DIR = PROJECT_ROOT / "data"

# Auto-detect handbook PDF
default_pdf_candidate = DATA_DIR / "novapay_global_hr_manual_50p.pdf"
if not default_pdf_candidate.exists():
    default_pdf_candidate = DATA_DIR / "handbook.pdf"

PDF_PATH = Path(os.getenv("PDF_PATH", str(default_pdf_candidate)))
CHROMA_PERSIST_DIRECTORY = Path(os.getenv("CHROMA_PERSIST_DIRECTORY", str(PROJECT_ROOT / "chroma_db")))
FEEDBACK_FILE = DATA_DIR / "feedback.json"
BM25_DATA_FILE = CHROMA_PERSIST_DIRECTORY / "bm25_data.pkl"

# Model & LLM Settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
AVAILABLE_GROQ_MODELS = [
    "qwen/qwen3.8-27b",
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.1-8b-instant"
]

# Embeddings & Vector Store
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
COLLECTION_NAME = "hr_handbook"

# Retrieval Settings
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("DEFAULT_SIMILARITY_THRESHOLD", "0.35"))
RRF_K = 60  # Reciprocal Rank Fusion constant

# HR Support & Disclaimer
HR_CONTACT_EMAIL = os.getenv("HR_CONTACT_EMAIL", "hr@company.com")
DISCLAIMER_NOTE = (
    "ℹ️ *Note: This response is for informational purposes only. "
    "Human Resources is the final authority on policy interpretation.*"
)

# Policy Topic Categories & Keywords
CATEGORY_KEYWORDS = {
    "Compensation": [
        "compensation", "salary", "pay", "bonus", "appraisal", "overtime",
        "allowance", "payroll", "ctc", "hra", "wage", "direct deposit",
        "employment grades", "performance calibration", "promotion cycles"
    ],
    "ESOP": [
        "esop", "stock", "equity", "shares", "vesting", "cliff",
        "exercise", "grant", "409a", "options", "shareholder", "band-3"
    ],
    "Cafeteria": [
        "cafeteria", "canteen", "dining", "food", "meal", "lunch",
        "dinner", "breakfast", "snacks", "beverage", "dietary",
        "guest dining", "barista", "pantry", "tea", "coffee"
    ],
    "Travel": [
        "travel", "reimbursement", "per diem", "flight", "hotel",
        "mileage", "lodging", "cab", "conveyance", "expense claim",
        "air travel", "receipt", "tier-1 international"
    ],
    "Leave": [
        "leave", "vacation", "sick", "casual", "maternity", "paternity",
        "bereavement", "pto", "comp-off", "compensatory", "holiday",
        "time-off", "encashment", "absence", "sabbatical"
    ],
    "Benefits": [
        "benefit", "benefits", "insurance", "mediclaim", "dental",
        "vision", "wellness", "gym", "stipend", "mental health",
        "eap", "education", "learning", "counseling", "ergonomic"
    ],
    "General": [
        "policy", "conduct", "working hours", "remote", "hybrid",
        "notice period", "probation", "ethics", "whistleblower",
        "clean desk", "insider trading", "posh", "anti-harassment",
        "exit clearance", "buyout"
    ]
}

CATEGORIES_LIST = [
    "Compensation",
    "ESOP",
    "Cafeteria",
    "Travel",
    "Leave",
    "Benefits",
    "General"
]

def infer_category(text: str, heading: str = "") -> str:
    """
    Infers policy category based on keyword density in text and heading.
    Heading matches receive 4x weight.
    """
    combined = f"{heading} {heading} {heading} {text}".lower()
    scores = {cat: 0 for cat in CATEGORIES_LIST}
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in combined:
                heading_matches = heading.lower().count(kw)
                body_matches = text.lower().count(kw)
                scores[cat] += (heading_matches * 4) + body_matches
                
    best_cat = max(scores, key=scores.get)
    if scores[best_cat] > 0:
        return best_cat
    return "General"
