from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, Optional
import sqlite3
import os
import json
import time

# Import the flow_crew module
from src.agent_creator.flow_crew import create_crew_with_flow
from src.agent_creator.flow_crew import MultiCrewFlow

DB_PATH = os.environ.get("DB_PATH", "crews.db")
router = APIRouter()

@router.post("/create", response_model=Dict[str, Any])
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

@router.post("/debug", response_model=Dict[str, Any])
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
        # Add a small delay to simulate processing
        time.sleep(2)
        
        # Initialize the flow
        flow = MultiCrewFlow(user_task=task, config=config)
        result = flow.kickoff()
        
        # Create a mock analysis result
        mock_analysis = {
            "constraints": ["Must respond within 5 seconds", "Must be accurate"],
            "requirements": ["Product knowledge", "Returns policy understanding"],
            "complexity": 6,
            "domain_knowledge": ["E-commerce", "Customer service"],
            "time_sensitivity": {"is_critical": True, "reasoning": "Customer satisfaction depends on quick responses"},
            "success_criteria": ["Accurate information provided", "Customer issue resolved"],
            "recommended_process_type": "sequential"
        }
        
        # Create a mock planning result
        mock_planning = {
            "selected_algorithm": "Best-of-N Planning",
            "algorithm_justification": "Well-suited for customer service workflows with clear steps",
            "candidate_plans": [
                {"name": "Sequential Approach", "score": 8},
                {"name": "Hierarchical Structure", "score": 6}
            ],
            "selected_plan": {
                "name": "Sequential Customer Service",
                "description": "A straightforward sequential approach"
            },
            "verification_score": 8
        }
        
        # Create a mock implementation result
        mock_implementation = {
            "agents": [vars(agent) for agent in result.agents],
            "tasks": [vars(task) for task in result.tasks],
            "workflow": {"sequence": ["Greet", "Answer", "Process"]},
            "process_type": "sequential",
            "tools": []
        }
        
        # Create a mock evaluation result
        mock_evaluation = {
            "strengths": ["Clear task division", "Specialized agents"],
            "weaknesses": ["Limited handling of complex queries"],
            "missing_elements": ["Escalation process for difficult cases"],
            "recommendations": ["Add escalation mechanism"],
            "overall_score": 8,
            "improvement_area": "none"
        }
        
        # Return debug information
        return {
            "status": "success",
            "task": task,
            "analysis": mock_analysis,
            "planning": mock_planning,
            "implementation": mock_implementation,
            "evaluation": mock_evaluation,
            "iterations": {
                "analysis": 1,
                "planning": 1,
                "implementation": 1,
                "evaluation": 1
            },
            "final_crew_plan": {
                "agents": [vars(agent) for agent in result.agents],
                "tasks": [vars(task) for task in result.tasks],
                "process": getattr(result, "process", "sequential")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in flow debugging: {str(e)}")