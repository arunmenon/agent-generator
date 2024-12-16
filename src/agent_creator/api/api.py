# src/my_project/api/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import crews
from .routers import meta_agent
from .db_handler import init_db

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize DB, if needed
init_db()

# Include routers
app.include_router(meta_agent.router, prefix="/meta-agent", tags=["meta-agent"])
app.include_router(crews.router, tags=["crews"]) 

# Additional routers can be included as needed
