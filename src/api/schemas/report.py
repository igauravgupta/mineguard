from typing import Any, Dict

from pydantic import BaseModel


class ReportRequest(BaseModel):
    classification: Dict[str, Any]
    report: Dict[str, Any]
    generatedAt: str | None = None
    notificationSent: bool | None = None
    sentAt: str | None = None


class ReportResponse(BaseModel):
    id: str
    classification: Dict[str, Any]
    report: Dict[str, Any]
    generatedAt: str | None = None
    notificationSent: bool | None = None
    sentAt: str | None = None


class ReportStatusResponse(BaseModel):
    id: str
    status: str
    classification: Dict[str, Any] | None = None
    report: Dict[str, Any] | None = None
    generatedAt: str | None = None
    notificationSent: bool | None = None
    sentAt: str | None = None
    error: str | None = None
