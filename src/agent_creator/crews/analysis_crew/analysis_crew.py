"""
Analysis Crew implementation for user task analysis.
"""

from crewai import Crew, Process
from typing import Dict, Any, Optional
import json

from ..models import AnalysisOutput
from .agents import create_agents
from .tasks import create_tasks

class AnalysisCrew:
    """
    Crew for analyzing user task requirements and constraints.
    Uses a sequential process to systematically analyze the user's request.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the AnalysisCrew with configuration."""
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
        """Create and return a configured AnalysisCrew."""
        # Create agents
        agents = create_agents(self.llm)
        
        # Create tasks
        tasks = create_tasks(agents)
        
        # Create crew
        return Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            process=Process.sequential,
            manager_llm=self.llm
        )
        
    def analyze(self, user_task: str) -> AnalysisOutput:
        """
        Analyze the user task and return structured analysis.
        
        Args:
            user_task: The user's task description
            
        Returns:
            AnalysisOutput containing analysis results
        """
        # Run the crew with the user task as input
        result = self.crew().kickoff(inputs={"user_task": user_task})
        
        # Extract the analysis data, handling both string and dict formats
        if isinstance(result.raw, str):
            try:
                analysis_data = json.loads(result.raw)
            except json.JSONDecodeError:
                # Fallback if the output isn't valid JSON
                analysis_data = {
                    "constraints": [],
                    "requirements": [],
                    "complexity": 5,
                    "domain_knowledge": [],
                    "time_sensitivity": {"is_critical": False, "reasoning": ""},
                    "success_criteria": [],
                    "recommended_process_type": "sequential"
                }
        else:
            analysis_data = result.raw
        
        # Convert to AnalysisOutput model
        return AnalysisOutput(**analysis_data)