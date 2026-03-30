from langchain.agents import create_agent

from config.logger import get_logger
from providers.llm import LLMProvider
from agents.quey_understand_agent.prompt import (
    INTENTS,
    SYSTEM_PROMPT,
    build_user_prompt,
)


class QueryUnderstandAgent:
    """Classify user intent for legal queries and incident reports."""

    _INTENTS = INTENTS

    def __init__(self) -> None:
        self.logger = get_logger()
        # TODO: Add Pydantic models when parsing structured outputs or tool calls.
        self.chat_model = LLMProvider().get_chat_model()
        self.agent = create_agent(
            model=self.chat_model,
            tools=[],
            system_prompt=SYSTEM_PROMPT,
        )

    def detect_intent(self, user_query: str) -> str:
        """Return the detected intent label for a user query."""
        prompt = build_user_prompt(user_query)

        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": prompt}]}
        )

        label = result.get("output", "")
        if not label and isinstance(result.get("messages"), list):
            last_message = result["messages"][-1]
            label = getattr(last_message, "content", "") or last_message.get(
                "content", ""
            )

        label = label.strip().lower()
        if label not in self._INTENTS:
            self.logger.warning("Unknown intent label from LLM: %s", label)
            return self._INTENTS[0]

        return label