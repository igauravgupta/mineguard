from langchain_litellm import ChatLiteLLM

from config.constants import Constants


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

        self.api_key = Constants.GROQ_API_KEY
        self.model_name = Constants.LLM_MODEL_NAME

        if not self.api_key:
            raise ValueError("GROQ_API_KEY is required to initialize the LLM client")
        if not self.model_name:
            raise ValueError("LLM_MODEL_NAME is required to initialize the LLM client")

        self.model = ChatLiteLLM(model_name=self.model_name, api_key=self.api_key)
        self.__class__._initialized = True

    def generate_response(self, prompt: str) -> str:
        """Generate a response from the configured LLM client."""
        response = self.model.invoke(prompt)
        return response.content