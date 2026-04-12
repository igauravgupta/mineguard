from fastapi import FastAPI

from api.routes.incident import router as incident_router
from api.routes.report import router as report_router


app = FastAPI(title="MineGuard API")
app.include_router(incident_router)
app.include_router(report_router)
