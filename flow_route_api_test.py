"""
Minimal API test to properly include the flow router
"""

from fastapi import FastAPI, APIRouter, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uvicorn

# Create the main app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a router for flow endpoints
flow_router = APIRouter()

@flow_router.post("/create")
async def create_flow(data: Dict[str, Any] = Body(...)):
    """Test flow/create endpoint"""
    return {
        "status": "success",
        "message": "Flow create endpoint is working",
        "received_data": data
    }

@flow_router.post("/debug")
async def debug_flow(data: Dict[str, Any] = Body(...)):
    """Test flow/debug endpoint"""
    return {
        "status": "success",
        "message": "Flow debug endpoint is working",
        "received_data": data
    }

# Include the router with proper prefix
app.include_router(flow_router, prefix="/flow", tags=["flow"])

# Root endpoint for health check
@app.get("/")
async def root():
    return {"status": "API is working"}

if __name__ == "__main__":
    print("Starting flow route test API server on http://0.0.0.0:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)