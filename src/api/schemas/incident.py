from typing import Any, Dict, List

from pydantic import BaseModel, Field


class IncidentRequest(BaseModel):
    description: str = Field(..., min_length=1)
    images_base64: List[str] = Field(default_factory=list, max_items=5)


class IncidentResponse(BaseModel):
    classification: Dict[str, Any]
    report: str
