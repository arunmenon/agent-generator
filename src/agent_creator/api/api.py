# src/my_project/api/api.py
from fastapi import FastAPI
from .db_handler import init_db
from fastapi.middleware.cors import CORSMiddleware
from .routers import meta_agent, crews, flow
from .services.crew_service import load_all_crews_from_db

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],    # critical to allow OPTIONS, POST, etc.
    allow_headers=["*"],
)

app.include_router(meta_agent.router, prefix="/meta-agent", tags=["meta-agent"])
app.include_router(crews.router, tags=["crews"])
app.include_router(flow.router, tags=["flow"])

@app.on_event("startup")
def startup_event():
    init_db()
    load_all_crews_from_db()
