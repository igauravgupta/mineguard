from fastapi import FastAPI

from api.routes.incident import router as incident_router


app = FastAPI(title="MineGuard API")
app.include_router(incident_router)
