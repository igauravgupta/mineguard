import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


class Constants:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "")
    LOGGER_NAME = os.getenv("LOGGER_NAME", "mineguard")

    SRC_DIR = Path(__file__).resolve().parents[1]
    BASE_DIR = SRC_DIR.parent
    LAWS_DIR = SRC_DIR / "rag" / "data" / "laws"
    EMBEDDINGS_DIR = SRC_DIR / "rag" / "laws_rag" / "embeddings"

    EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    BATCH_SIZE = 64

    MIN_TEXT_LENGTH = 50
    MIN_PRINTABLE_RATIO = 0.9
    MIN_ASCII_RATIO = 0.7
