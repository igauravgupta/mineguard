SYSTEM_PROMPT = (
    "You are a senior consultant who answers user questions using provided "
    "retrieval results from policies and laws. The retrieval data will be "
    "given in the user prompt. If the retrieval results are insufficient, "
    "you may use web search results if they are provided. Base your answer on "
    "the evidence and keep it concise."
)


def build_user_prompt(
    user_query: str,
    retrieval_payload: dict,
    web_results: list,
) -> str:
    return (
        "Answer the user question using the retrieval results below. "
        "If web results are provided, you may use them to fill gaps.\n\n"
        f"User query: {user_query}\n\n"
        f"Retrieval results: {retrieval_payload}\n\n"
        f"Web results: {web_results}"
    )
