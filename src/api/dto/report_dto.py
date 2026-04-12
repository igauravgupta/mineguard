from typing import Any, Dict

from api.services.report_service import save_report_to_db


def save_report(report: Dict[str, Any]) -> Dict[str, Any]:
    return save_report_to_db(report)
