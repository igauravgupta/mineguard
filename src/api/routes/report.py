from fastapi import APIRouter, HTTPException

from api.schemas.report import ReportRequest, ReportResponse, ReportStatusResponse
from api.services.report_service import get_report, save_report_to_db


router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportResponse)
def create_report(payload: ReportRequest):
    try:
        saved = save_report_to_db(payload.model_dump())
        return saved
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{report_id}", response_model=ReportStatusResponse)
def get_report_status(report_id: str):
    report = get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
