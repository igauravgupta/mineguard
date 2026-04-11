SYSTEM_PROMPT = (
    "You are an answer generation agent. You receive a user query and a "
    "reasoning response from an upstream agent. Convert that reasoning into "
    "a clear, concise, user-facing answer. If the reasoning is insufficient, "
    "say what is missing without adding new facts."
)


def build_user_prompt(user_query: str, reasoning_response: str) -> str:
    return (
        "Generate the final response using the reasoning response below.\n\n"
        f"User query: {user_query}\n\n"
        f"Reasoning response: {reasoning_response}"
    )
