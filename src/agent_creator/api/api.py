# src/my_project/api/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .meta_agent import meta_agent
from db_handler import init_db

app = FastAPI()

# Set allowed origins to match your frontend (http://localhost:3000)
# For development, you can set ["*"] to allow all origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB, if needed
init_db()

# Include routers
app.include_router(meta_agent.router, prefix="/meta-agent", tags=["meta-agent"])

# Additional routers can be included as needed
