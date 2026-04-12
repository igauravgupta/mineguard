SYSTEM_PROMPT = (
    "You are a report generation assistant. Return a JSON object only. "
    "No markdown, no extra text. Keep the report concise and structured."
)


def build_user_prompt(classification_payload: dict, report_date: str) -> str:
    return (
        "Generate a complete incident report as JSON only. Use the "
        "classification payload below. The summary must include the date "
        f"{report_date}. Use this exact JSON shape with double-quoted keys:\n"
        "{\n"
        '  "status": "Active",\n'
        '  "reportDate": "<Month DD, YYYY>",\n'
        '  "incidentType": "...",\n'
        '  "severity": "...",\n'
        '  "location": "...",\n'
        '  "summary": "...",\n'
        '  "keyDetails": ["..."],\n'
        '  "recommendations": ["..."],\n'
        '  "notification": "...",\n'
        '  "disclaimer": "..."\n'
        "}\n\n"
        f"Classification payload: {classification_payload}"
    )
