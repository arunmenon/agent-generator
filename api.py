"""
Unified API server for agent generator
"""

from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
import uvicorn
import json
import os
import time
import sqlite3

# Import flow creation functionality from the main implementation
from src.agent_creator.flow.multi_crew_flow import create_crew_with_flow, MultiCrewFlow

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
    return {"message": "Agent Generator API is running"}

# Flow creation endpoint
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
        
        # For debugging - print basic information
        agent_count = len(crew_plan.agents) if hasattr(crew_plan, 'agents') and crew_plan.agents else 0
        task_count = len(crew_plan.tasks) if hasattr(crew_plan, 'tasks') and crew_plan.tasks else 0
        print(f"Created crew plan with {agent_count} agents and {task_count} tasks")
                
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
        
        # Insert agents
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
        
        # Insert tasks
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
            "message": f"Crew created successfully with domain: {domain}, process areas: {', '.join(process_areas)}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating crew: {str(e)}")

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
        # Initialize the flow
        flow = MultiCrewFlow(user_task=task, config=config)
        result = flow.kickoff()
        
        return {
            "status": "success",
            "task": task,
            "domain": domain,
            "problem_context": problem_context,
            "crew_plan": result.model_dump() if hasattr(result, "model_dump") else vars(result),
            "message": "Debug flow completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in flow debugging: {str(e)}")

# Crews listing endpoint
@app.get("/crews")
def list_crews():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT crew_id, crew_name, process, manager_llm, is_active FROM crew_metadata ORDER BY crew_id ASC")
    rows = c.fetchall()
    conn.close()

    crews = []
    for row in rows:
        crew_id, crew_name, process, manager_llm, is_active = row
        crews.append({
            "crew_id": crew_id,
            "crew_name": crew_name if crew_name else "",
            "process": process if process else "",
            "manager_llm": manager_llm,
            "is_active": bool(is_active)
        })
    return crews

# Crew details endpoint
@app.get("/crews/{crew_id}")
def get_crew(crew_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get crew metadata
    c.execute("""
        SELECT crew_name, process, input_schema, manager_llm, is_active
        FROM crew_metadata
        WHERE crew_id=?
    """, (crew_id,))
    crew_row = c.fetchone()
    if not crew_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Crew not found")

    (crew_name, process, input_schema_json, manager_llm, is_active) = crew_row

    # Get agents
    c.execute("""
        SELECT name, role, goal, llm, tools, backstory
        FROM agent
        WHERE crew_id=?
    """, (crew_id,))
    agent_rows = c.fetchall()
    agents = []
    for (name, role, goal, llm, tools_json, backstory) in agent_rows:
        agents.append({
            "name": name,
            "role": role,
            "goal": goal,
            "llm": llm,
            "tools": [] if tools_json is None else json.loads(tools_json),
            "backstory": backstory or ""
        })

    # Get tasks
    c.execute("""
        SELECT name, description, expected_output, agent_name, context_tasks
        FROM task
        WHERE crew_id=?
    """, (crew_id,))
    task_rows = c.fetchall()
    tasks = []
    for (name, description, expected_output, agent_name, context_tasks) in task_rows:
        context_list = json.loads(context_tasks) if context_tasks else []
        tasks.append({
            "name": name,
            "description": description,
            "expected_output": expected_output,
            "agent": agent_name,
            "context_tasks": context_list
        })

    conn.close()

    # Construct crew data
    crew_data = {
        "crew_id": crew_id,
        "crew_name": crew_name if crew_name else "",
        "process": process if process else "",
        "manager_llm": manager_llm,
        "is_active": bool(is_active),
        "agents": agents,
        "tasks": tasks,
        "input_schema": {} if not input_schema_json else json.loads(input_schema_json)
    }
    return crew_data

# Delete crew endpoint
@app.delete("/crews/{crew_id}")
def delete_crew(crew_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if crew exists
    c.execute("SELECT crew_id FROM crew_metadata WHERE crew_id=?", (crew_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Crew not found")

    # Delete agents
    c.execute("DELETE FROM agent WHERE crew_id=?", (crew_id,))
    # Delete tasks
    c.execute("DELETE FROM task WHERE crew_id=?", (crew_id,))
    # Delete crew metadata
    c.execute("DELETE FROM crew_metadata WHERE crew_id=?", (crew_id,))

    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Crew {crew_id} deleted successfully"}

# Database initialization
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create crew_metadata table
    c.execute("""
    CREATE TABLE IF NOT EXISTS crew_metadata(
        crew_id INTEGER PRIMARY KEY AUTOINCREMENT,
        crew_name TEXT,
        process TEXT,
        input_schema TEXT,
        output_schema TEXT,
        manager_llm TEXT,
        domain TEXT,
        problem_context TEXT,
        input_context TEXT,
        output_context TEXT,
        is_active BOOLEAN DEFAULT 1
    );
    """)
    
    # Create agent table
    c.execute("""
    CREATE TABLE IF NOT EXISTS agent(
        agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
        crew_id INTEGER,
        name TEXT,
        role TEXT,
        goal TEXT,
        llm TEXT,
        tools TEXT,
        backstory TEXT
    );
    """)
    
    # Create task table
    c.execute("""
    CREATE TABLE IF NOT EXISTS task(
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        crew_id INTEGER,
        name TEXT,
        description TEXT,
        expected_output TEXT,
        agent_name TEXT,
        context_tasks TEXT
    );
    """)
    
    conn.commit()
    conn.close()

# Startup event to initialize database
@app.on_event("startup")
async def startup_event():
    init_db()

# Run the application if this file is executed directly
if __name__ == "__main__":
    print("Starting Agent Generator API server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)