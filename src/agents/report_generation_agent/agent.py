from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional

from langchain.agents import create_agent

from agents.report_generation_agent.prompt import SYSTEM_PROMPT, build_user_prompt
from config.logger import get_logger
from providers.llm import LLMProvider
from providers.smtp_client import SmtpClientAdapter


logger = get_logger(__name__)


def _save_report_dummy(report: Dict[str, Any]) -> bool:
    logger.info("Saving report to database (dummy)")
    logger.debug("Report payload: %s", report)
    return True


class ReportGenerationAgent:
    """Generate incident reports, store them, and notify recipients."""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.llm = LLMProvider()
        self.agent = create_agent(
            model=self.llm.get_chat_model(),
            tools=[],
            system_prompt=SYSTEM_PROMPT,
        )
        self.smtp_client = SmtpClientAdapter()

    def generate_report(self, classification_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not classification_payload:
            self.logger.error("Missing classification payload")
            return None

        prompt = build_user_prompt(classification_payload)
        try:
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": prompt}]}
            )
            output = result.get("output", "")
            if not output and isinstance(result.get("messages"), list):
                last_message = result["messages"][-1]
                output = getattr(last_message, "content", "") or last_message.get(
                    "content", ""
                )

            report = {
                "classification": classification_payload,
                "report": output,
            }

            recipients = classification_payload.get("notifyEmails", [])
            subject = "Incident Report Notification"
            body = output or json.dumps(report, indent=2)

            with ThreadPoolExecutor(max_workers=2) as executor:
                executor.submit(self.smtp_client.send_email, recipients, subject, body)
                executor.submit(_save_report_dummy, report)

            return report
        except Exception as exc:
            self.logger.error("Report generation failed: %s", exc)
            return None
