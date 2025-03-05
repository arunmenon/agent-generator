from fastapi import APIRouter, HTTPException, Query, Body
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
        
        # Insert crew metadata - use the process type from the crew plan
        crew_name = f"Flow-Generated Crew: {task[:30]}..."
        process_type = getattr(crew_plan, 'process', 'sequential')
        c.execute("""
            INSERT INTO crew_metadata (crew_name, process, manager_llm, is_active)
            VALUES (?, ?, ?, ?)
        """, (crew_name, process_type, "gpt-4o", 1))
        
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
            agent_name = task.name.split("_")[0] if "_" in task.name else task.name
            c.execute("""
                INSERT INTO task (crew_id, name, description, agent_name, context_tasks)
                VALUES (?, ?, ?, ?, ?)
            """, (crew_id, task.name, task.purpose, agent_name, context_tasks))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success", 
            "crew_id": crew_id,
            "message": f"Crew created successfully using Multi-Crew Flow approach with {process_type} process"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating crew: {str(e)}")

@router.post("/flow/debug", response_model=Dict[str, Any])
def debug_crew_flow(
    task: str = Body(..., embed=True),
    model_name: str = Body("gpt-4o", embed=True),
    temperature: float = Body(0.7, embed=True)
):
    """Debug endpoint that returns the full analysis process without saving to the database."""
    config = {
        "model_name": model_name,
        "temperature": temperature
    }
    
    try:
        # Initialize the flow but capture intermediate state for debugging
        from src.agent_creator.flow_crew import MultiCrewFlow
        
        flow = MultiCrewFlow(user_task=task, config=config)
        result = flow.kickoff()
        
        # Return debug information
        return {
            "status": "success",
            "task": task,
            "analysis": flow.state.analysis_result.dict() if flow.state.analysis_result else None,
            "planning": flow.state.planning_result.dict() if flow.state.planning_result else None,
            "implementation": flow.state.implementation_result.dict() if flow.state.implementation_result else None,
            "evaluation": flow.state.evaluation_result.dict() if flow.state.evaluation_result else None,
            "iterations": {
                "analysis": flow.state.analysis_iterations,
                "planning": flow.state.planning_iterations,
                "implementation": flow.state.implementation_iterations,
                "evaluation": flow.state.evaluation_iterations
            },
            "final_crew_plan": {
                "agents": [agent.dict() for agent in result.agents],
                "tasks": [task.dict() for task in result.tasks],
                "process": getattr(result, "process", "sequential")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in flow debugging: {str(e)}")