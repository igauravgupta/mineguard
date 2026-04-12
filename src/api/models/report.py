from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class IncidentReport:
    classification: Dict[str, Any]
    report: Dict[str, Any]
