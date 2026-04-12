from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from langchain.agents import create_agent

from agents.report_generation_agent.prompt import SYSTEM_PROMPT, build_user_prompt
from config.logger import get_logger
from providers.llm import LLMProvider
from providers.smtp_client import SmtpClientAdapter


def _current_report_date() -> str:
    return datetime.now(timezone.utc).strftime("%B %d, %Y")


def _ensure_summary_date(summary: str, report_date: str) -> str:
    if not summary:
        return f"On {report_date}, incident summary not provided."
    if report_date.lower() in summary.lower():
        return summary
    return f"On {report_date}, {summary.lstrip()}"


def _build_plain_text_report(report: Dict[str, Any]) -> str:
    def _safe_str(value: Any) -> str:
        if value is None:
            return ""
        return str(value)

    lines = [
        f"Status: {_safe_str(report.get('status'))}",
        f"Report Date: {_safe_str(report.get('reportDate'))}",
        f"Incident Type: {_safe_str(report.get('incidentType'))}",
        f"Severity: {_safe_str(report.get('severity'))}",
        f"Location: {_safe_str(report.get('location'))}",
        "",
        "Summary:",
        _safe_str(report.get("summary")),
        "",
        "Key Details:",
    ]
    for item in report.get("keyDetails", []):
        if item is None:
            continue
        lines.append(f"- {_safe_str(item)}")
    lines.extend(["", "Recommendations:"])
    for item in report.get("recommendations", []):
        if item is None:
            continue
        lines.append(f"- {_safe_str(item)}")
    lines.extend([
        "",
        "Notification:",
        _safe_str(report.get("notification")),
        "",
        "Disclaimer:",
        _safe_str(report.get("disclaimer")),
    ])
    return "\n".join(lines).strip()


def _build_html_report(report: Dict[str, Any]) -> str:
    def _safe_str(value: Any) -> str:
        if value is None:
            return ""
        return str(value)

    def _list_items(items: list[str]) -> str:
        if not items:
            return "<li>None provided.</li>"
        safe_items = [item for item in items if item is not None]
        if not safe_items:
            return "<li>None provided.</li>"
        return "".join(f"<li>{_safe_str(item)}</li>" for item in safe_items)

    return f"""
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Incident Report</title>
    </head>
    <body style="margin:0;padding:0;background:#f5f3ee;font-family:Arial,Helvetica,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f3ee;padding:24px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,0.08);">
                        <tr>
                            <td style="padding:28px 32px;background:#1d2b2a;color:#ffffff;">
                                <div style="font-size:12px;letter-spacing:1.4px;text-transform:uppercase;opacity:0.8;">Incident Report</div>
                                <div style="font-size:24px;font-weight:700;margin:6px 0 0;">{_safe_str(report.get('incidentType'))}</div>
                                <div style="font-size:14px;opacity:0.9;margin-top:6px;">Severity: {_safe_str(report.get('severity'))} &bull; Status: {_safe_str(report.get('status'))}</div>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:24px 32px;">
                                <table width="100%" cellpadding="0" cellspacing="0" style="font-size:14px;color:#1d2b2a;">
                                    <tr>
                                        <td style="padding:6px 0;"><strong>Report Date:</strong> {_safe_str(report.get('reportDate'))}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding:6px 0;"><strong>Location:</strong> {_safe_str(report.get('location'))}</td>
                                    </tr>
                                </table>
                                <div style="margin:18px 0 6px;font-weight:700;color:#1d2b2a;">Summary</div>
                                <div style="color:#3f4c4a;line-height:1.6;">{_safe_str(report.get('summary'))}</div>

                                <div style="margin:18px 0 6px;font-weight:700;color:#1d2b2a;">Key Details</div>
                                <ul style="margin:0;padding-left:18px;color:#3f4c4a;line-height:1.6;">
                                    {_list_items(report.get('keyDetails', []))}
                                </ul>

                                <div style="margin:18px 0 6px;font-weight:700;color:#1d2b2a;">Recommendations</div>
                                <ul style="margin:0;padding-left:18px;color:#3f4c4a;line-height:1.6;">
                                    {_list_items(report.get('recommendations', []))}
                                </ul>

                                <div style="margin:18px 0 6px;font-weight:700;color:#1d2b2a;">Notification</div>
                                <div style="color:#3f4c4a;line-height:1.6;">{_safe_str(report.get('notification'))}</div>

                                <div style="margin:18px 0 6px;font-weight:700;color:#1d2b2a;">Disclaimer</div>
                                <div style="color:#3f4c4a;line-height:1.6;">{_safe_str(report.get('disclaimer'))}</div>
                            </td>
                        </tr>
                    </table>
                    <div style="font-size:11px;color:#7a7a7a;margin-top:12px;">This message was generated by MineGuard.</div>
                </td>
            </tr>
        </table>
    </body>
</html>
""".strip()


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

    def generate_report(
        self,
        classification_payload: Dict[str, Any],
        report_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        if not classification_payload:
            self.logger.error("Missing classification payload")
            return None

        report_date = _current_report_date()
        prompt = build_user_prompt(classification_payload, report_date)
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

            parsed_report: Dict[str, Any]
            try:
                parsed_report = json.loads(output)
            except json.JSONDecodeError:
                parsed_report = {
                    "status": "Active",
                    "reportDate": report_date,
                    "incidentType": classification_payload.get("incidentType", ""),
                    "severity": classification_payload.get("severity", ""),
                    "location": classification_payload.get("location", ""),
                    "summary": output.strip() or "Incident report generated.",
                    "keyDetails": [],
                    "recommendations": [],
                    "notification": "Notification has been issued to relevant stakeholders.",
                    "disclaimer": "This report is automatically generated and requires review.",
                }

            parsed_report["status"] = "Active"
            parsed_report["reportDate"] = report_date
            parsed_report["incidentType"] = parsed_report.get(
                "incidentType", classification_payload.get("incidentType", "")
            )
            parsed_report["severity"] = parsed_report.get(
                "severity", classification_payload.get("severity", "")
            )
            parsed_report["location"] = parsed_report.get(
                "location", classification_payload.get("location", "")
            )
            parsed_report["summary"] = _ensure_summary_date(
                parsed_report.get("summary", ""), report_date
            )
            parsed_report["notification"] = parsed_report.get(
                "notification", "Notification has been issued to relevant stakeholders."
            )
            parsed_report["disclaimer"] = parsed_report.get(
                "disclaimer", "This report is automatically generated and requires review."
            )
            parsed_report["keyDetails"] = list(parsed_report.get("keyDetails", []) or [])
            parsed_report["recommendations"] = list(
                parsed_report.get("recommendations", []) or []
            )

            report_payload = {
                "classification": classification_payload,
                "report": parsed_report,
                "generatedAt": datetime.now(timezone.utc).isoformat(),
            }

            recipients = classification_payload.get("notifyEmails", [])
            incident_type = parsed_report.get("incidentType", "Incident")
            severity = parsed_report.get("severity", "")
            subject = f"{incident_type} Report - {severity}"
            plain_body = _build_plain_text_report(parsed_report)
            html_body = _build_html_report(parsed_report)
            email_sent = self.smtp_client.send_email(
                recipients,
                subject,
                plain_body,
                html_body=html_body,
            )
            if email_sent:
                report_payload["notificationSent"] = True
                report_payload["sentAt"] = datetime.now(timezone.utc).isoformat()
            else:
                report_payload["notificationSent"] = False

            return report_payload
        except Exception as exc:
            self.logger.error("Report generation failed: %s", exc)
            return None
