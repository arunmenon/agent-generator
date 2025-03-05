"""
Evaluation Crew for assessing and validating agent crew implementations.
"""

from crewai import Crew, Process
from typing import Dict, Any
import json

from ..models import AnalysisOutput, PlanningOutput, ImplementationOutput, EvaluationOutput
from .agents import create_agents
from .tasks import create_tasks

class EvaluationCrew:
    """
    Crew for evaluating the quality and completeness of agent crew implementations.
    Uses a hierarchical process with a QA manager overseeing specialized testers.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the EvaluationCrew with configuration."""
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
        """Create and return a configured EvaluationCrew."""
        # Create agents
        agents = create_agents(self.llm)
        
        # Create tasks
        tasks = create_tasks(agents)
        
        # Create crew with hierarchical process for delegation
        return Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            process=Process.hierarchical,
            manager_llm=self.llm
        )
        
    def evaluate(self, user_task: str, analysis_result: AnalysisOutput, 
                planning_result: PlanningOutput, 
                implementation_result: ImplementationOutput) -> EvaluationOutput:
        """
        Evaluate the quality and completeness of an implementation.
        
        Args:
            user_task: The user's task description
            analysis_result: Results from the Analysis Crew
            planning_result: Results from the Planning Crew
            implementation_result: Results from the Implementation Crew
            
        Returns:
            EvaluationOutput with assessment results and recommendations
        """
        # Run the crew with all previous results as input
        result = self.crew().kickoff(
            inputs={
                "user_task": user_task,
                "analysis_result": analysis_result.dict(),
                "planning_result": planning_result.dict(),
                "implementation_result": implementation_result.dict()
            }
        )
        
        # Extract the evaluation data, handling both string and dict formats
        if isinstance(result.raw, str):
            try:
                evaluation_data = json.loads(result.raw)
            except json.JSONDecodeError:
                # Fallback if the output isn't valid JSON
                evaluation_data = {
                    "strengths": [],
                    "weaknesses": [],
                    "missing_elements": [],
                    "recommendations": [],
                    "overall_score": 5,
                    "improvement_area": "none"
                }
        else:
            evaluation_data = result.raw
        
        # Convert to EvaluationOutput model
        return EvaluationOutput(**evaluation_data)