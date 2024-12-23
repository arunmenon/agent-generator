# src/my_project/api/services/crew_service.py
import sqlite3
import os
from typing import Dict, Any
from crewai import Agent, Task, Crew, Process

DB_PATH = os.environ.get("DB_PATH", "crews.db")

in_memory_crews = {}  # crew_id -> Crew object

def load_crew_config(crew_id: int) -> dict:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT crew_name, process, input_schema_json, planning, manager_llm, user_memory, user_cache, user_knowledge, user_human_input_tasks, is_active
        FROM crew_metadata
        WHERE crew_id=?
    """, (crew_id,))
    crew_row = c.fetchone()
    if not crew_row:
        conn.close()
        return None

    (crew_name, process, input_schema_json, planning, manager_llm,
     user_memory, user_cache, user_knowledge, user_human_input_tasks, is_active) = crew_row

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
            "backstory": ""
        })

    c.execute("""
        SELECT name, description, expected_output, agent_name, human_input, context_tasks
        FROM task
        WHERE crew_id=?
    """, (crew_id,))
    task_rows = c.fetchall()
    tasks = []
    for (tname, description, expected_output, agent_name, human_input, context_tasks) in task_rows:
        context_list = eval(context_tasks) if context_tasks else []
        tasks.append({
            "name": tname,
            "description": description,
            "expected_output": expected_output,
            "agent": agent_name,
            "human_input": bool(human_input),
            "context_tasks": context_list
        })

    conn.close()

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

def build_crew_from_config(config: dict) -> Crew:
    crew_info = config.get("crew", {})
    process_str = crew_info.get("process", "sequential")
    process = Process.sequential if process_str == "sequential" else Process.hierarchical

    agent_list = []
    for a in config.get("agents", []):
        agent_obj = Agent(
            role=a["role"],
            goal=a["goal"],
            backstory=a.get("backstory",""),
            llm=a.get("llm","openai/gpt-4"),
            tools=[],  # If tools needed, handle here
            memory=a.get("memory",False),
            cache=a.get("cache",False),
            verbose=False,
            allow_delegation=False,
            max_iter=5,
            respect_context_window=True,
            use_system_prompt=True,
            max_retry_limit=2,
        )
        agent_list.append((a["name"], agent_obj))

    agent_map = {name: obj for (name, obj) in agent_list}

    task_list = []
    for t in config.get("tasks", []):
        assigned_agent = agent_map.get(t["agent"], None)
        task_obj = Task(
            description=t["description"],
            expected_output=t["expected_output"],
            agent=assigned_agent,
            human_input=t.get("human_input",False),
            context=[]
        )
        task_list.append(task_obj)

    crew_obj = Crew(
        agents=[obj for (_,obj) in agent_list],
        tasks=task_list,
        process=process,
        verbose=False
    )
    return crew_obj

def load_all_crews_from_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT crew_id FROM crew_metadata")
    rows = c.fetchall()
    conn.close()

    for (crew_id,) in rows:
        config = load_crew_config(crew_id)
        if config:
            crew_obj = build_crew_from_config(config)
            in_memory_crews[crew_id] = crew_obj

def run_crew_from_memory(crew_id: int, inputs: Dict[str, Any]) -> Dict[str, Any]:
    from fastapi import HTTPException
    if crew_id not in in_memory_crews:
        raise HTTPException(status_code=404, detail="Crew not found in memory")
    result = in_memory_crews[crew_id].kickoff(inputs=inputs)
    if result.pydantic:
        return result.pydantic.dict()
    elif result.json_dict:
        return result.json_dict
    else:
        return {"raw": result.raw}
