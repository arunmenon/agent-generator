from fastapi import APIRouter
from src.agent_creator.api.schemas import MetaAgentInput
from src.agent_creator.crew import MetaCrew
from .db_handler import  save_crew_config

router = APIRouter()

@router.post("/create_crew")
def create_crew(input: MetaAgentInput):
    # Instantiate the MetaCrew class
    meta_crew_instance = MetaCrew()

    # Run all tasks in sequence with the given inputs
    result = meta_crew_instance.crew().kickoff(inputs=input.dict())

    # Extract the final configuration from the result
    final_config = result.pydantic.dict() if result.pydantic else result.raw

    # Ensure 'agents' and 'tasks' keys are present even if empty
    if final_config.get("agents") is None:
        final_config["agents"] = []
    if final_config.get("tasks") is None:
        final_config["tasks"] = []

    # Save the final configuration to the database
    save_crew_config(final_config)

    return {"status": "success", "config": final_config}
