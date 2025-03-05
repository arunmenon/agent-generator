#\!/bin/bash
source venv_crewai/bin/activate
python -m uvicorn src.agent_creator.api.api:app --reload
