# src/my_project/api/db_handler.py
import sqlite3
import json
import os

DB_PATH = os.environ.get("DB_PATH", "crews.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create tables if not exist
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

    c.execute("""
    INSERT INTO crew_metadata (crew_name, process, input_schema_json, planning, manager_llm, user_memory, user_cache, user_knowledge, user_human_input_tasks)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        crew_name,
        process,
        json.dumps(input_schema),
        planning,
        manager_llm,
        user_memory,
        user_cache,
        user_knowledge,
        user_human_input_tasks
    ))
    crew_id = c.lastrowid

    for agent in agents:
        c.execute("""
        INSERT INTO agent (crew_id, name, role, goal, llm, tools_json, memory, cache)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            crew_id,
            agent.get("name"),
            agent.get("role"),
            agent.get("goal"),
            agent.get("llm"),
            json.dumps(agent.get("tools", [])),
            agent.get("memory", False),
            agent.get("cache", False)
        ))

    for task in tasks:
        c.execute("""
        INSERT INTO task (crew_id, name, description, expected_output, agent_name, human_input, context_tasks)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            crew_id,
            task.get("name"),
            task.get("description"),
            task.get("expected_output"),
            task.get("agent"),
            task.get("human_input", False),
            json.dumps(task.get("context_tasks", []))
        ))

    conn.commit()
    conn.close()
