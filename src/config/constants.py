import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


class Constants:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "")
    LOGGER_NAME = os.getenv("LOGGER_NAME", "mineguard")

    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "")

    MONGO_URI = os.getenv("MONGO_URI", "")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "mineguard")
    MONGO_REPORTS_COLLECTION = os.getenv("MONGO_REPORTS_COLLECTION", "incident_reports")

    REPORT_API_BASE_URL = os.getenv("REPORT_API_BASE_URL", "http://localhost:8000")

    SRC_DIR = Path(__file__).resolve().parents[1]
    BASE_DIR = SRC_DIR.parent
    LAWS_DIR = SRC_DIR / "rag" / "data" / "laws"
    EMBEDDINGS_DIR = SRC_DIR / "rag" / "laws_rag" / "embeddings"
    POLICIES_DIR = SRC_DIR / "rag" / "data" / "policies"
    POLICIES_EMBEDDINGS_DIR = SRC_DIR / "rag" / "policies_rag" / "embeddings"

    EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    BATCH_SIZE = 64

    MIN_TEXT_LENGTH = 50
    MIN_PRINTABLE_RATIO = 0.9
    MIN_ASCII_RATIO = 0.7
