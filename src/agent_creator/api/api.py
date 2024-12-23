# src/my_project/api/api.py
from fastapi import FastAPI
from .db_handler import init_db
from .routers import meta_agent, crews
from .services.crew_service import load_all_crews_from_db

app = FastAPI()

app.include_router(meta_agent.router, prefix="/meta-agent", tags=["meta-agent"])
app.include_router(crews.router, tags=["crews"])

@app.on_event("startup")
def startup_event():
    init_db()
    load_all_crews_from_db()
