from fastapi import APIRouter, BackgroundTasks, HTTPException

from api.schemas.incident import IncidentRequest, IncidentJobResponse
from api.services.incident_service import classify_and_generate_report_async


router = APIRouter(prefix="/incident", tags=["incident"])


@router.post("/classify", response_model=IncidentJobResponse)
def classify_incident(payload: IncidentRequest, background_tasks: BackgroundTasks):
    report_id = classify_and_generate_report_async(
        description=payload.description,
        images_base64=payload.images_base64,
        background_tasks=background_tasks,
    )
    if report_id is None:
        raise HTTPException(status_code=500, detail="Incident processing failed")
    return {"id": report_id, "status": "processing"}
