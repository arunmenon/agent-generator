"""
Planning Crew implementation for hierarchical plan generation.
"""

from crewai import Crew, Process
from langchain.chat_models import ChatOpenAI
from typing import Dict, Any
import json

from ..models import AnalysisOutput, PlanningOutput
from .agents import create_agents
from .tasks import create_tasks

class PlanningCrew:
    """
    Crew for generating plans using various algorithms.
    Uses a hierarchical process with a manager and algorithm specialists.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the PlanningCrew with configuration."""
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
        """Create and return a configured PlanningCrew."""
        # Create agents
        agents = create_agents(self.llm)
        
        # Create tasks
        tasks = create_tasks(agents)
        
        # Create crew with hierarchical process
        return Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            process=Process.hierarchical,
            manager_llm=self.llm
        )
        
    def plan(self, user_task: str, analysis_result: AnalysisOutput) -> PlanningOutput:
        """
        Generate plans based on user task and analysis.
        
        Args:
            user_task: The user's task description
            analysis_result: Results from the Analysis Crew as AnalysisOutput
            
        Returns:
            PlanningOutput containing planning results
        """
        # Run the crew with user task and analysis as input
        result = self.crew().kickoff(
            inputs={
                "user_task": user_task,
                "analysis_result": analysis_result.dict()
            }
        )
        
        # Extract the planning data, handling both string and dict formats
        if isinstance(result.raw, str):
            try:
                planning_data = json.loads(result.raw)
            except json.JSONDecodeError:
                # Fallback if the output isn't valid JSON
                planning_data = {
                    "selected_algorithm": "Best-of-N Planning",
                    "algorithm_justification": "Default approach for planning",
                    "candidate_plans": [],
                    "selected_plan": {},
                    "verification_score": 5
                }
        else:
            planning_data = result.raw
        
        # Convert to PlanningOutput model
        return PlanningOutput(**planning_data)