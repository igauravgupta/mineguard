import base64
from io import BytesIO
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks

from config.logger import get_logger
from agents.incident_classification_agent import ClassifyIncidentAgent
from agents.report_generation_agent import ReportGenerationAgent
from api.services.report_service import create_pending_report, update_report


logger = get_logger(__name__)


def _decode_images(images_base64: List[str]) -> List[BytesIO]:
    decoded = []
    for item in images_base64:
        try:
            raw = base64.b64decode(item)
            decoded.append(BytesIO(raw))
        except Exception as exc:
            logger.warning("Failed to decode image: %s", exc)
    return decoded


def _process_incident(report_id: str, description: str, images_base64: Optional[List[str]]) -> None:
    try:
        classifier = ClassifyIncidentAgent()
        report_agent = ReportGenerationAgent()

        images = _decode_images(images_base64 or [])
        classification = classifier.classify(description=description, images=images)
        if classification is None:
            update_report(report_id, {"status": "failed", "error": "classification failed"})
            return

        report = report_agent.generate_report(classification)
        if report is None:
            update_report(report_id, {"status": "failed", "error": "report generation failed"})
            return

        update_report(
            report_id,
            {
                "status": "Active",
                "classification": report.get("classification"),
                "report": report.get("report"),
                "generatedAt": report.get("generatedAt"),
                "notificationSent": report.get("notificationSent"),
                "sentAt": report.get("sentAt"),
            },
        )
    except Exception as exc:
        logger.error("Incident processing failed: %s", exc)
        update_report(report_id, {"status": "failed", "error": str(exc)})


def classify_and_generate_report_async(
    description: str,
    images_base64: Optional[List[str]] = None,
    background_tasks: Optional[BackgroundTasks] = None,
) -> Optional[str]:
    report_id = create_pending_report()
    if background_tasks is None:
        return None
    background_tasks.add_task(_process_incident, report_id, description, images_base64)
    return report_id
