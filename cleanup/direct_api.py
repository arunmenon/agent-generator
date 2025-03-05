"""
Direct API server for testing
"""

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Direct API is working"}

@app.post("/flow/create")
def create_flow(data: Dict[str, Any]):
    """Simplified flow creation endpoint"""
    task = data.get("task", "")
    domain = data.get("domain", "")
    problem_context = data.get("problem_context", "")
    process_areas = data.get("process_areas", [])
    
    return {
        "status": "success",
        "message": "This is a direct API test response",
        "received_data": {
            "task": task,
            "domain": domain,
            "problem_context": problem_context,
            "process_areas": process_areas
        }
    }

if __name__ == "__main__":
    print("Starting direct API server on http://0.0.0.0:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)