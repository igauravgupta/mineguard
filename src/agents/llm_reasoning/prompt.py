SYSTEM_PROMPT = (
    "You are a senior consultant who answers user questions using provided "
    "retrieval results from policies and laws. The retrieval data will be "
    "given in the user prompt. If the retrieval results are insufficient, "
    "you may call the web search tool. Base your answer on the retrieval "
    "evidence and keep it concise."
)


def build_user_prompt(user_query: str, retrieval_payload: dict) -> str:
    return (
        "Answer the user question using the retrieval results below. "
        "If you need more context, use web search.\n\n"
        f"User query: {user_query}\n\n"
        f"Retrieval results: {retrieval_payload}"
    )
