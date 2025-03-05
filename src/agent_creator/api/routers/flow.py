from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
import sqlite3
import os
import json

from src.agent_creator.flow_crew import create_crew_with_flow

DB_PATH = os.environ.get("DB_PATH", "crews.db")
router = APIRouter()

@router.post("/flow", response_model=Dict[str, Any])
def create_crew_with_flow_api(
    task: str,
    model_name: Optional[str] = Query("gpt-4o", description="The LLM to use"),
    temperature: Optional[float] = Query(0.7, description="LLM temperature parameter")
):
    """Create a new crew configuration using the Flow-based approach."""
    config = {
        "model_name": model_name,
        "temperature": temperature
    }
    
    try:
        # Create crew plan using the flow approach
        crew_plan = create_crew_with_flow(task, config)
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Insert crew metadata
        crew_name = f"Flow-Generated Crew: {task[:30]}..."
        c.execute("""
            INSERT INTO crew_metadata (crew_name, process, manager_llm, is_active)
            VALUES (?, ?, ?, ?)
        """, (crew_name, "sequential", "gpt-4o", 1))
        
        crew_id = c.lastrowid
        
        # Insert agents
        for agent in crew_plan.agents:
            c.execute("""
                INSERT INTO agent (crew_id, name, role, goal, llm, backstory)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (crew_id, agent.name, agent.role, agent.goal, "gpt-4o", agent.backstory))
        
        # Insert tasks
        for task in crew_plan.tasks:
            context_tasks = json.dumps(task.dependencies) if task.dependencies else "[]"
            c.execute("""
                INSERT INTO task (crew_id, name, description, agent_name, context_tasks)
                VALUES (?, ?, ?, ?, ?)
            """, (crew_id, task.name, task.purpose, task.name.split("_")[0], context_tasks))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success", 
            "crew_id": crew_id,
            "message": "Crew created successfully using Flow approach"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating crew: {str(e)}")