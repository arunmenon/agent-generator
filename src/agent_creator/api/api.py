# src/my_project/api/api.py
from fastapi import FastAPI
from .routers import meta_agent
from .db_handler import init_db

app = FastAPI()

# Initialize DB, if needed
init_db()

# Include routers
app.include_router(meta_agent.router, prefix="/meta-agent", tags=["meta-agent"])

# Additional routers can be included as needed
