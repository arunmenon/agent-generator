"""
Implementation Crew for creating executable agent and task definitions.
"""

from crewai import Crew, Process
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
        from crewai import LLM
        
        return LLM(
            provider="openai",
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
        # Extract domain context from analysis result
        domain = analysis_result.domain
        process_areas = analysis_result.process_areas
        problem_context = analysis_result.problem_context
        input_context = analysis_result.input_context
        output_context = analysis_result.output_context
        constraints = analysis_result.constraints
        
        # Run the crew with user task, analysis, planning, and domain context as input
        result = self.crew().kickoff(
            inputs={
                "user_task": user_task,
                "analysis_result": analysis_result,  # Pass Pydantic object directly, don't use dict()
                "planning_result": planning_result,  # CrewAI can work with Pydantic objects directly
                "domain": domain,
                "process_areas": process_areas,
                "problem_context": problem_context,
                "input_context": input_context,
                "output_context": output_context,
                "constraints": constraints
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