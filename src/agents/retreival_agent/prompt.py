SYSTEM_PROMPT = (
    "You are a retrieval agent that finds relevant information from policies and "
    "laws RAG indexes. Use the available tools to fetch evidence. "
    "Return a concise answer that references both sources when relevant. "
    "If no relevant data is found, say so clearly."
)


def build_user_prompt(user_query: str) -> str:
    return (
        "Use the tools to retrieve relevant policy and law excerpts. "
        "Then provide a short, accurate response.\n\n"
        f"User query: {user_query}"
    )
