# src/my_project/api/routers/crews.py
from fastapi import APIRouter, HTTPException
import sqlite3
import os
from typing import List, Dict, Any

DB_PATH = os.environ.get("DB_PATH", "crews.db")
router = APIRouter()

@router.get("/crews", response_model=List[Dict[str, Any]])
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

@router.get("/crews/{crew_id}", response_model=Dict[str, Any])
def get_crew(crew_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get crew metadata
    c.execute("""
        SELECT crew_name, process, input_schema_json, planning, manager_llm, user_memory, user_cache, user_knowledge, user_human_input_tasks, is_active
        FROM crew_metadata
        WHERE crew_id=?
    """, (crew_id,))
    crew_row = c.fetchone()
    if not crew_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Crew not found")

    (crew_name, process, input_schema_json, planning, manager_llm,
     user_memory, user_cache, user_knowledge, user_human_input_tasks, is_active) = crew_row

    # Get agents
    c.execute("""
        SELECT name, role, goal, llm, tools_json, memory, cache
        FROM agent
        WHERE crew_id=?
    """, (crew_id,))
    agent_rows = c.fetchall()
    agents = []
    for (name, role, goal, llm, tools_json, memory, cache) in agent_rows:
        agents.append({
            "name": name,
            "role": role,
            "goal": goal,
            "llm": llm,
            "tools": [] if tools_json is None else (eval(tools_json) if tools_json else []),
            "memory": bool(memory),
            "cache": bool(cache),
            "backstory": ""  # if needed, or fetch from a column if you stored backstory
        })

    # Get tasks
    c.execute("""
        SELECT name, description, expected_output, agent_name, human_input, context_tasks
        FROM task
        WHERE crew_id=?
    """, (crew_id,))
    task_rows = c.fetchall()
    tasks = []
    for (name, description, expected_output, agent_name, human_input, context_tasks) in task_rows:
        context_list = eval(context_tasks) if context_tasks else []
        tasks.append({
            "name": name,
            "description": description,
            "expected_output": expected_output,
            "agent": agent_name,
            "human_input": bool(human_input),
            "context_tasks": context_list
        })

    conn.close()

    # Construct final schema-like JSON
    crew_data = {
        "crew": {
            "name": crew_name if crew_name else "",
            "process": process if process else "",
            "planning": bool(planning),
            "manager_llm": manager_llm,
            "user_memory": bool(user_memory),
            "user_cache": bool(user_cache),
            "user_knowledge": bool(user_knowledge),
            "user_human_input_tasks": bool(user_human_input_tasks)
        },
        "agents": agents,
        "tasks": tasks,
        "input_schema_json": {} if not input_schema_json else eval(input_schema_json)
    }
    return crew_data

@router.delete("/crews/{crew_id}", response_model=Dict[str, Any])
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
