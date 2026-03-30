import os
from dotenv import load_dotenv


load_dotenv()


class Constants:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "")
    LOGGER_NAME = os.getenv("LOGGER_NAME", "mineguard")
