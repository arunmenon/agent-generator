"""
Implementation Crew for creating executable agent and task definitions.
"""

from crewai import Crew, Process
from langchain.chat_models import ChatOpenAI
from typing import Dict, Any
import json

from ..models import AnalysisOutput, PlanningOutput, ImplementationOutput
from .agents import create_agents
from .tasks import create_tasks

class ImplementationCrew:
    """
    Crew for implementing executable agent and task definitions.
    Uses a sequential process to systematically build the implementation.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the ImplementationCrew with configuration."""
        self.config = config or {}
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize the language model with configuration."""
        return ChatOpenAI(
            base_url=self.config.get("api_base", None),
            api_key=self.config.get("api_key", None),
            model=self.config.get("model_name", "gpt-4o"),
            temperature=self.config.get("temperature", 0.7),
            streaming=False
        )
        
    def crew(self) -> Crew:
        """Create and return a configured ImplementationCrew."""
        # Create agents
        agents = create_agents(self.llm)
        
        # Create tasks
        tasks = create_tasks(agents)
        
        # Create crew with sequential process
        return Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            process=Process.sequential,
            manager_llm=self.llm
        )
        
    def implement(self, user_task: str, analysis_result: AnalysisOutput, 
                 planning_result: PlanningOutput) -> ImplementationOutput:
        """
        Create executable agent and task definitions based on planning results.
        
        Args:
            user_task: The user's task description
            analysis_result: Results from the Analysis Crew
            planning_result: Results from the Planning Crew
            
        Returns:
            ImplementationOutput with executable agent and task definitions
        """
        # Run the crew with user task, analysis and planning as input
        result = self.crew().kickoff(
            inputs={
                "user_task": user_task,
                "analysis_result": analysis_result.dict(),
                "planning_result": planning_result.dict()
            }
        )
        
        # Extract the implementation data, handling both string and dict formats
        if isinstance(result.raw, str):
            try:
                implementation_data = json.loads(result.raw)
            except json.JSONDecodeError:
                # Fallback if the output isn't valid JSON
                implementation_data = {
                    "agents": [],
                    "tasks": [],
                    "workflow": {"sequence": []},
                    "process_type": "sequential",
                    "tools": []
                }
        else:
            implementation_data = result.raw
        
        # Convert to ImplementationOutput model
        return ImplementationOutput(**implementation_data)