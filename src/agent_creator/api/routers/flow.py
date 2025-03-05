from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, Optional, List
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
async def create_crew_with_flow_api(request_data: Dict[str, Any] = Body(...)):
    """Create a new crew configuration using the Flow-based approach."""
    # Extract values from the request body
    task = request_data.get("task")
    domain = request_data.get("domain") 
    problem_context = request_data.get("problem_context")
    input_context = request_data.get("input_context")
    output_context = request_data.get("output_context")
    process_areas = request_data.get("process_areas", [])
    constraints = request_data.get("constraints", [])
    model_name = request_data.get("model_name", "gpt-4o")
    temperature = request_data.get("temperature", 0.7)
    
    # Validate required fields
    if not all([task, domain, problem_context, input_context, output_context]):
        raise HTTPException(status_code=422, detail="Missing required fields")
        
    config = {
        "model_name": model_name,
        "temperature": temperature,
        "domain": domain,
        "process_areas": process_areas or [],
        "problem_context": problem_context,
        "input_context": input_context,
        "output_context": output_context,
        "constraints": constraints or []
    }
    
    try:
        # Create crew plan using the flow approach
        crew_plan = create_crew_with_flow(task, config)
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Insert crew metadata - use the process type from the crew plan
        crew_name = crew_plan.name
        process_type = crew_plan.process
        
        # Convert input and output schemas to JSON strings
        input_schema_json = json.dumps(crew_plan.input_schema.model_dump() if crew_plan.input_schema else {})
        output_schema_json = json.dumps(crew_plan.output_schema.model_dump() if crew_plan.output_schema else {})
        
        c.execute("""
            INSERT INTO crew_metadata (
                crew_name, process, manager_llm, is_active, 
                domain, problem_context, input_context, output_context,
                input_schema, output_schema)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            crew_name, process_type, "gpt-4o", 1, 
            crew_plan.domain, crew_plan.problem_context, 
            crew_plan.input_context, crew_plan.output_context,
            input_schema_json, output_schema_json
        ))
        
        crew_id = c.lastrowid
        
        # Insert agents - use the model_dump to preserve interpolation placeholders
        for agent in crew_plan.agents:
            agent_data = agent.model_dump()
            c.execute("""
                INSERT INTO agent (crew_id, name, role, goal, llm, backstory, tools)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                crew_id, 
                agent_data["name"], 
                agent_data["role"], 
                agent_data["goal"], 
                "gpt-4o", 
                agent_data["backstory"],
                json.dumps(agent_data.get("tools", []))
            ))
        
        # Insert tasks - use the model_dump to preserve interpolation placeholders
        for task in crew_plan.tasks:
            task_data = task.model_dump()
            context_tasks = json.dumps(task_data.get("context", []))
            c.execute("""
                INSERT INTO task (crew_id, name, description, agent_name, context_tasks, expected_output)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                crew_id, 
                task.name, 
                task_data["description"], 
                task_data["agent"], 
                context_tasks,
                task_data.get("expected_output", "")
            ))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success", 
            "crew_id": crew_id,
            "crew_name": crew_name,
            "domain": crew_plan.domain,
            "process": process_type,
            "agents_count": len(crew_plan.agents),
            "tasks_count": len(crew_plan.tasks),
            "input_schema": crew_plan.input_schema.model_dump() if crew_plan.input_schema else {},
            "output_schema": crew_plan.output_schema.model_dump() if crew_plan.output_schema else {},
            "message": f"Crew created successfully using Multi-Crew Flow approach with {process_type} process"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating crew: {str(e)}")

@router.post("/debug", response_model=Dict[str, Any])
async def debug_crew_flow(request_data: Dict[str, Any] = Body(...)):
    """Debug endpoint that returns the full analysis process without saving to the database."""
    # Extract values from the request body
    task = request_data.get("task")
    domain = request_data.get("domain") 
    problem_context = request_data.get("problem_context")
    input_context = request_data.get("input_context")
    output_context = request_data.get("output_context")
    process_areas = request_data.get("process_areas", [])
    constraints = request_data.get("constraints", [])
    model_name = request_data.get("model_name", "gpt-4o")
    temperature = request_data.get("temperature", 0.7)
    
    # Validate required fields
    if not all([task, domain, problem_context, input_context, output_context]):
        raise HTTPException(status_code=422, detail="Missing required fields")
        
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
    
    try:
        # Add a small delay to simulate processing
        time.sleep(2)
        
        # Initialize the flow
        print("[DEBUG] Initializing MultiCrewFlow with kickoff()")
        try:
            flow = MultiCrewFlow(user_task=task, config=config)
            # The real CrewAI Flow implementation uses kickoff() method, but we may need to catch errors
            # if the Flow implementation isn't fully compatible
            result = flow.kickoff()
            print(f"[DEBUG] Flow kickoff complete, result type: {type(result)}")
        except AttributeError as e:
            print(f"[DEBUG] Flow kickoff error: {str(e)}")
            # Fallback to manual execution
            flow = MultiCrewFlow(user_task=task, config=config)
            result = flow.run_analysis_crew()
            print(f"[DEBUG] Fallback execution complete, result type: {type(result)}")
        
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
            "domain": domain,
            "problem_context": problem_context,
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
                "name": f"Generated Crew for {domain}",
                "description": f"A crew designed to solve {problem_context}", 
                "process": getattr(result, "process", "sequential"),
                "domain": domain,
                "problem_context": problem_context,
                "input_context": input_context,
                "output_context": output_context,
                "context": {
                    "domain": domain,
                    "problem_context": problem_context,
                    "input_context": input_context, 
                    "output_context": output_context,
                    "process_areas": process_areas,
                    "constraints": constraints
                },
                "agents": [agent.model_dump() for agent in result.agents],
                "tasks": [task.model_dump() for task in result.tasks],
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": f"The domain context ({domain})",
                            "example": domain
                        },
                        "problem_context": {
                            "type": "string",
                            "description": "Detailed description of the problem being solved",
                            "example": problem_context
                        },
                        "input_data": {
                            "type": "object",
                            "description": f"The input data: {input_context}",
                            "example": {"sample": "data"}
                        }
                    },
                    "required": ["domain", "problem_context", "input_data"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "result": {
                            "type": "object",
                            "description": f"The output result: {output_context}",
                            "example": {"status": "success", "data": {}}
                        }
                    }
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in flow debugging: {str(e)}")