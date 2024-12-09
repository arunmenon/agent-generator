# src/my_project/api/routers/meta_agent.py
import json
from fastapi import APIRouter
from ..schemas import MetaAgentInput
from src.agent_creator.crew import MetaCrew
from ..db_handler import save_crew_config

router = APIRouter()

@router.post("/create_crew")
def create_crew(input: MetaAgentInput):
    meta_crew_instance = MetaCrew()
    result = meta_crew_instance.crew().kickoff(inputs=input.dict())
    final_config = result.pydantic.dict() if result.pydantic else result.raw
    if final_config.get("agents") is None:
        final_config["agents"] = []
    if final_config.get("tasks") is None:
        final_config["tasks"] = []
    save_crew_config(final_config)
    return {"status": "success", "config": final_config}
