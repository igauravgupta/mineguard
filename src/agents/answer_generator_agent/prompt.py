SYSTEM_PROMPT = (
    "You are an answer generation agent. You receive a user query and a "
    "reasoning response from an upstream agent. Convert that reasoning into "
    "a clear, concise, user-facing answer. Include citations and sources "
    "(law or policy names, file names, or URLs) for each key claim. "
    "If the reasoning is insufficient, say what is missing without adding new facts. "
    "End with a short 'Actions Used' list that states whether you used laws, "
    "company policies, and web search."
)


def build_user_prompt(user_query: str, reasoning_response: str) -> str:
    return (
        "Generate the final response using the reasoning response below. "
        "List sources with citations per key point, then add an 'Actions Used' list.\n\n"
        f"User query: {user_query}\n\n"
        f"Reasoning response: {reasoning_response}"
    )
