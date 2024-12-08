# src/my_project/api/routers/meta_agent.py
from fastapi import APIRouter
from schemas import MetaAgentInput
from agent_creator.crew import MetaCrew
from api.db_handler import save_crew_config

router = APIRouter()

@router.post("/create_crew")
def create_crew(input: MetaAgentInput):
    meta_crew_instance = MetaCrew()
    result = meta_crew_instance.crew().kickoff(inputs=input.dict())
    final_config = result.pydantic.dict() if result.pydantic else result.raw
    save_crew_config(final_config)
    return {"status": "success", "config": final_config}
