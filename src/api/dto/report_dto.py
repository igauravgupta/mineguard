from typing import Any, Dict

from config.logger import get_logger


logger = get_logger(__name__)


def save_report(report: Dict[str, Any]) -> bool:
    logger.info("Saving report to database (dummy)")
    logger.debug("Report payload: %s", report)
    return True
