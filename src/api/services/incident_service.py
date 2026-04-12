import base64
from io import BytesIO
from typing import Any, Dict, List, Optional

from config.logger import get_logger
from agents.incident_classification_agent import ClassifyIncidentAgent
from agents.report_generation_agent import ReportGenerationAgent


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


def classify_and_generate_report(
    description: str,
    images_base64: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    classifier = ClassifyIncidentAgent()
    report_agent = ReportGenerationAgent()

    images = _decode_images(images_base64 or [])
    classification = classifier.classify(description=description, images=images)
    if classification is None:
        return None

    report = report_agent.generate_report(classification)
    if report is None:
        return None

    return report
