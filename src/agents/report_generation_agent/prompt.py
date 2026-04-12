SYSTEM_PROMPT = (
    "You are a report generation assistant. Build a complete incident report "
    "from the classification payload provided. Keep it concise and structured."
)


def build_user_prompt(classification_payload: dict) -> str:
    return (
        "Generate a complete incident report in plain text using the "
        "classification payload below. Include incidentType, severity, "
        "status, location, and a short summary.\n\n"
        f"Classification payload: {classification_payload}"
    )
