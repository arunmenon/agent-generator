#\!/bin/bash
source venv_crewai/bin/activate
pip install crewai
pip install "crewai[tools]"
pip install fastapi uvicorn
pip install -e .
echo "CrewAI environment is set up and activated\!"
