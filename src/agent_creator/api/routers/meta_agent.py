# src/my_project/api/routers/meta_agent.py

import json
from fastapi import APIRouter, HTTPException
from ..schemas import MetaAgentInput
from src.agent_creator.crew import MetaCrew
from ..db_handler import save_crew_config

router = APIRouter()

@router.post("/create_crew")
def create_crew(input: MetaAgentInput):
    # 1) Run the meta-crew to generate final_config
    meta_crew_instance = MetaCrew()
    result = meta_crew_instance.crew().kickoff(inputs=input.dict())

    # 2) Extract final config as dict
    final_config = result.pydantic.dict() if result.pydantic else result.raw

    # 3) Ensure 'agents' and 'tasks' exist (fallback to empty lists)
    if final_config.get("agents") is None:
        final_config["agents"] = []
    if final_config.get("tasks") is None:
        final_config["tasks"] = []

    # ------------------
    # 4) Validation snippet
    # ------------------

    # (a) Make sure each agent has a 'name'
    for agent in final_config["agents"]:
        if not agent.get("name"):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Agent with role='{agent.get('role','<no role>')}' "
                    "is missing the 'name' field. Please ensure 'name' is populated."
                )
            )

    # Collect agent names in a set
    agent_names = {agent["name"] for agent in final_config["agents"]}

    # (b) Ensure each task.agent references a valid agent name
    for task in final_config["tasks"]:
        if not task.get("agent"):
            raise HTTPException(
                status_code=400,
                detail=f"Task '{task.get('name','<unnamed>')}' is missing 'agent' field."
            )
        if task["agent"] not in agent_names:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Task '{task.get('name','<unnamed>')}' references agent '{task['agent']}' "
                    f"which is not in the agent 'name' list: {sorted(agent_names)}"
                )
            )

    # ------------------
    # 5) Save the validated config
    # ------------------
    save_crew_config(final_config)
    return {"status": "success", "config": final_config}
