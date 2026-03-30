INTENTS = (
    "legal query",
    "incident reporting",
)

SYSTEM_PROMPT = (
    "You are an intent classifier for legal queries and incident reports. "
    "Return exactly one label from this list:\n"
    "- legal query\n"
    "- incident reporting\n\n"
    "Only output the label and nothing else."
)


def build_user_prompt(user_query: str) -> str:
    return (
        "Classify the user query into one label from the system prompt list.\n\n"
        f"User query: {user_query}"
    )
