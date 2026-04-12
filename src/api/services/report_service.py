from typing import Any, Dict, Optional

from bson import ObjectId

from api.dto.mongo_client import get_reports_collection
from config.logger import get_logger


logger = get_logger(__name__)


def save_report_to_db(report: Dict[str, Any]) -> Dict[str, Any]:
    collection = get_reports_collection()
    result = collection.insert_one(report)
    report_id = str(result.inserted_id)
    logger.info("Report saved with id=%s", report_id)
    return {"id": report_id, **report}


def create_pending_report() -> str:
    collection = get_reports_collection()
    payload = {
        "status": "processing",
        "classification": None,
        "report": None,
        "error": None,
    }
    result = collection.insert_one(payload)
    report_id = str(result.inserted_id)
    logger.info("Created pending report id=%s", report_id)
    return report_id


def update_report(report_id: str, updates: Dict[str, Any]) -> bool:
    collection = get_reports_collection()
    result = collection.update_one(
        {"_id": ObjectId(report_id)},
        {"$set": updates},
    )
    return result.matched_count == 1


def get_report(report_id: str) -> Optional[Dict[str, Any]]:
    collection = get_reports_collection()
    doc = collection.find_one({"_id": ObjectId(report_id)})
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc
