"""
Fixed API implementation using direct routes for testing
"""

from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
import uvicorn
import json
import os
import time
import sqlite3

# Import relevant modules (we'll mock the flow functionality)
# from src.agent_creator.flow_crew import create_crew_with_flow, MultiCrewFlow

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
DB_PATH = os.environ.get("DB_PATH", "crews.db")

# Root endpoint
@app.get("/")
def root():
    return {"message": "Fixed API is working"}

# Mimicking the flow/create endpoint
@app.post("/flow/create")
async def create_flow(
    task: str = Body(...),
    domain: str = Body(...),
    problem_context: str = Body(...),
    input_context: str = Body(...),
    output_context: str = Body(...),
    process_areas: List[str] = Body([]),
    constraints: List[str] = Body([]),
    model_name: str = Body("gpt-4o"),
    temperature: float = Body(0.7)
):
    """Create a new crew using the flow-based approach."""
    # Mock the configuration
    config = {
        "model_name": model_name,
        "temperature": temperature,
        "domain": domain,
        "process_areas": process_areas,
        "problem_context": problem_context,
        "input_context": input_context,
        "output_context": output_context,
        "constraints": constraints
    }
    
    # Simple response
    return {
        "status": "success", 
        "crew_id": 456,
        "crew_name": f"Generated Crew for {domain}",
        "domain": domain,
        "process": "sequential",
        "agents_count": 3,
        "tasks_count": 4,
        "message": f"Crew created successfully with domain: {domain}, process areas: {', '.join(process_areas)}"
    }

# Debug endpoint
@app.post("/flow/debug")
async def debug_flow(
    task: str = Body(...),
    domain: str = Body(...),
    problem_context: str = Body(...),
    input_context: str = Body(...),
    output_context: str = Body(...),
    process_areas: List[str] = Body([]),
    constraints: List[str] = Body([]),
    model_name: str = Body("gpt-4o"),
    temperature: float = Body(0.7)
):
    """Debug endpoint that returns the full analysis process without saving to the database."""
    # Add a small delay to simulate processing
    time.sleep(1)
    
    return {
        "status": "success",
        "task": task,
        "domain": domain,
        "problem_context": problem_context,
        "analysis": {
            "constraints": constraints,
            "complexity": 6,
            "domain_knowledge": [domain],
            "success_criteria": ["Test criteria"]
        },
        "message": "Debug flow endpoint working with direct FastAPI route"
    }

if __name__ == "__main__":
    print("Starting fixed API server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)