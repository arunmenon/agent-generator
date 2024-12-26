# src/my_project/api/db_handler.py

import sqlite3
import json
import os

DB_PATH = os.environ.get("DB_PATH", "crews.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS crew_metadata(
        crew_id INTEGER PRIMARY KEY AUTOINCREMENT,
        crew_name TEXT,
        process TEXT,
        input_schema_json TEXT,
        planning BOOLEAN,
        manager_llm TEXT,
        user_memory BOOLEAN,
        user_cache BOOLEAN,
        user_knowledge BOOLEAN,
        user_human_input_tasks BOOLEAN,
        is_active BOOLEAN DEFAULT 1
    );
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS agent(
        agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
        crew_id INTEGER,
        name TEXT,
        role TEXT,
        goal TEXT,
        llm TEXT,
        tools_json TEXT,
        memory BOOLEAN,
        cache BOOLEAN
    );
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS task(
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        crew_id INTEGER,
        name TEXT,
        description TEXT,
        expected_output TEXT,
        agent_name TEXT,
        human_input BOOLEAN,
        context_tasks TEXT
    );
    """)
    conn.commit()
    conn.close()

def save_crew_config(config: dict):
    """
    Persists the final config into the DB.
    'human_input' remains a boolean, but if the final JSON has a dictionary
    in 'human_input', we move it to a sub-field (e.g. input_fields) and set
    'human_input' = True.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    crew_data = config.get('crew', {})
    input_schema = config.get('input_schema_json', {})
    agents = config.get('agents', [])
    tasks = config.get('tasks', [])

    crew_name = crew_data.get("name", "")
    process = crew_data.get("process", "sequential")
    planning = crew_data.get("planning", False)
    manager_llm = crew_data.get("manager_llm")
    user_memory = crew_data.get("user_memory", False)
    user_cache = crew_data.get("user_cache", False)
    user_knowledge = crew_data.get("user_knowledge", False)
    user_human_input_tasks = crew_data.get("user_human_input_tasks", False)

    # Validate each task's agent is in the 'agents' list
    agent_names = {agent.get("name") for agent in agents if agent.get("name")}
    for task in tasks:
        task_agent = task.get("agent")
        if not task_agent:
            raise ValueError(
                f"Task '{task.get('name','<unnamed>')}' has no 'agent' field."
            )
        if task_agent not in agent_names:
            raise ValueError(
                f"Task '{task.get('name','<unnamed>')}' references agent '{task_agent}', "
                "which is not present in the 'agents' list."
            )

    # Insert into crew_metadata (note we JSON-serialize manager_llm)
    c.execute("""
    INSERT INTO crew_metadata (crew_name, process, input_schema_json, planning, manager_llm,
                               user_memory, user_cache, user_knowledge, user_human_input_tasks)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        crew_name,
        process,
        json.dumps(input_schema),
        planning,
        json.dumps(manager_llm),  # safe even if manager_llm is None/dict/string
        user_memory,
        user_cache,
        user_knowledge,
        user_human_input_tasks
    ))
    crew_id = c.lastrowid

    # Insert agents
    for agent in agents:
        c.execute("""
        INSERT INTO agent (crew_id, name, role, goal, llm, tools_json, memory, cache)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            crew_id,
            agent.get("name"),
            agent.get("role"),
            agent.get("goal"),
            json.dumps(agent.get("llm")),
            json.dumps(agent.get("tools", [])),
            agent.get("memory", False),
            agent.get("cache", False)
        ))

    # Insert tasks
    for task in tasks:
        # Step 1: retrieve 'human_input'
        hi_value = task.get("human_input", False)
        # Step 2: if it's a dict, move it to a sub-field (like input_fields)
        if isinstance(hi_value, dict):
            # set human_input -> True
            # store hi_value in e.g. "input_fields" inside the context
            hi_bool = True
            input_fields_dict = hi_value
        else:
            # presumably just a boolean
            hi_bool = bool(hi_value)
            input_fields_dict = None

        # Step 3: Possibly store that dict in the "context_tasks" or a new sub-field
        context_list = task.get("context_tasks", [])
        # If we have a dict for human_input, embed it
        if input_fields_dict:
            # You can store it in context. Up to you. We'll nest it as 'input_fields'
            context_list.append({"input_fields": input_fields_dict})

        c.execute("""
        INSERT INTO task (crew_id, name, description, expected_output,
                          agent_name, human_input, context_tasks)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            crew_id,
            task.get("name"),
            task.get("description"),
            task.get("expected_output"),
            task.get("agent"),
            hi_bool,                  # only True/False
            json.dumps(context_list)  # store as JSON
        ))

    conn.commit()
    conn.close()
