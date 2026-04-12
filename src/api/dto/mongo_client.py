from pymongo import MongoClient

from config.constants import Constants
from config.logger import get_logger


logger = get_logger(__name__)


def get_mongo_client() -> MongoClient:
    if not Constants.MONGO_URI:
        raise ValueError("MONGO_URI is not configured")
    return MongoClient(Constants.MONGO_URI)


def get_reports_collection():
    client = get_mongo_client()
    db_name = Constants.MONGO_DB_NAME or "mineguard"
    collection_name = Constants.MONGO_REPORTS_COLLECTION or "incident_reports"
    return client[db_name][collection_name]
