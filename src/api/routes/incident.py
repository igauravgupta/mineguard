from fastapi import APIRouter, HTTPException

from api.schemas.incident import IncidentRequest, IncidentResponse
from api.services.incident_service import classify_and_generate_report


router = APIRouter(prefix="/incident", tags=["incident"])


@router.post("/classify", response_model=IncidentResponse)
def classify_incident(payload: IncidentRequest):
    report = classify_and_generate_report(
        description=payload.description,
        images_base64=payload.images_base64,
    )
    if report is None:
        raise HTTPException(status_code=500, detail="Incident processing failed")
    return report
