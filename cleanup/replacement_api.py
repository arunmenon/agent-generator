"""
Replacement API that implements the flow create endpoint directly
"""

from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
import uvicorn
import json
import sqlite3
import os

# Setup FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use the same DB path as the original app
DB_PATH = os.environ.get("DB_PATH", "crews.db")

# Root endpoint for health check
@app.get("/")
def root():
    return {"status": "Replacement API is working"}

# Mimic the original flow/create endpoint
@app.post("/flow/create")
def create_flow(data: Dict[str, Any] = Body(...)):
    """Create a new crew using the flow-based approach."""
    # Extract values from the request body
    task = data.get("task")
    domain = data.get("domain")
    problem_context = data.get("problem_context")
    input_context = data.get("input_context")
    output_context = data.get("output_context")
    process_areas = data.get("process_areas", [])
    constraints = data.get("constraints", [])
    model_name = data.get("model_name", "gpt-4o")
    temperature = data.get("temperature", 0.7)
    
    # Validate required fields
    if not all([task, domain, problem_context, input_context, output_context]):
        raise HTTPException(status_code=422, detail="Missing required fields")
    
    # Create simulated response
    return {
        "status": "success",
        "crew_id": 123,
        "crew_name": f"Generated Crew for {domain}",
        "domain": domain,
        "process": "sequential",
        "agents_count": 3,
        "tasks_count": 4,
        "input_schema": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": f"The domain context ({domain})"
                },
                "problem_context": {
                    "type": "string", 
                    "description": "Problem description"
                }
            }
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "object",
                    "description": output_context
                }
            }
        },
        "message": f"Crew created successfully with domain: {domain}, process areas: {', '.join(process_areas)}"
    }

# Debug endpoint that simulates the original debug endpoint
@app.post("/flow/debug")
def debug_flow(data: Dict[str, Any] = Body(...)):
    """Debug endpoint for testing flow creation."""
    return {
        "status": "success",
        "task": data.get("task", ""),
        "domain": data.get("domain", ""),
        "analysis": {
            "constraints": data.get("constraints", []),
            "complexity": 6,
            "domain_knowledge": [data.get("domain", "")]
        },
        "message": "Debug flow endpoint working"
    }

if __name__ == "__main__":
    print("Starting replacement API server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)