from langchain_litellm import ChatLiteLLM

from config.constants import Constants
from config.logger import get_logger


class LLMProvider:
    """Singleton wrapper around the LLM client configured from env constants."""

    _instance = None
    _initialized = False

    def __new__(cls):
        # Ensure only one instance exists across the app.
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the LLM client once using centralized config."""
        if self.__class__._initialized:
            return

        self.logger = get_logger()

        self.api_key = Constants.GROQ_API_KEY
        self.model_name = Constants.LLM_MODEL_NAME

        if not self.api_key:
            self.logger.error("Missing GROQ_API_KEY")
            raise ValueError("GROQ_API_KEY is required to initialize the LLM client")
        if not self.model_name:
            self.logger.error("Missing LLM_MODEL_NAME")
            raise ValueError("LLM_MODEL_NAME is required to initialize the LLM client")

        self.model = ChatLiteLLM(model_name=self.model_name, api_key=self.api_key)
        self.logger.info("LLM client initialized with model: %s", self.model_name)
        self.__class__._initialized = True

    def generate_response(self, prompt: str) -> str:
        """Generate a response from the configured LLM client."""
        self.logger.info("Sending prompt to LLM")
        response = self.model.invoke(prompt)
        self.logger.info("Received response from LLM")
        return response.content

    def get_chat_model(self) -> ChatLiteLLM:
        """Return the underlying chat model for LangChain agents/tool calls."""
        return self.model