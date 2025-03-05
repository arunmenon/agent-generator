"""
Planning Crew implementation for hierarchical plan generation.
"""

from crewai import Crew, Process
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
        from crewai import LLM
        import os
        
        # Use environment variable as fallback if not in config
        api_key = self.config.get("api_key", os.environ.get("OPENAI_API_KEY"))
        
        try:
            # LiteLLM client has issues with provider and streaming parameters
            return LLM(
                model=self.config.get("model_name", "gpt-4o"),
                temperature=self.config.get("temperature", 0.7)
            )
        except Exception as e:
            print(f"Error initializing LLM: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Fallback to default parameters
            return LLM(model="gpt-4o")
        
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
        
    def plan(self, user_task: str, analysis_result: Dict[str, Any]) -> PlanningOutput:
        """
        Generate plans based on user task and analysis.
        
        Args:
            user_task: The user's task description
            analysis_result: Results from the Analysis Crew (as dictionary)
            
        Returns:
            PlanningOutput containing planning results
        """
        # Handle case where analysis_result might be a dict or an object
        try:
            # Extract domain context from analysis result
            if isinstance(analysis_result, dict):
                domain = analysis_result.get('domain', '')
                process_areas = analysis_result.get('process_areas', [])
                problem_context = analysis_result.get('problem_context', '')
                input_context = analysis_result.get('input_context', '')
                output_context = analysis_result.get('output_context', '')
                constraints = analysis_result.get('constraints', [])
            else:
                # If somehow we still get an object
                domain = getattr(analysis_result, 'domain', '')
                process_areas = getattr(analysis_result, 'process_areas', [])
                problem_context = getattr(analysis_result, 'problem_context', '')
                input_context = getattr(analysis_result, 'input_context', '')
                output_context = getattr(analysis_result, 'output_context', '')
                constraints = getattr(analysis_result, 'constraints', [])
            
            # Run the crew with user task, analysis, and domain context as input
            result = self.crew().kickoff(
                inputs={
                    "user_task": user_task,
                    "analysis_result": analysis_result,  # Pass the dictionary
                    "domain": domain,
                    "process_areas": process_areas,
                    "problem_context": problem_context,
                    "input_context": input_context,
                    "output_context": output_context,
                    "constraints": constraints
                }
            )
        except Exception as e:
            print(f"Error extracting analysis data: {str(e)}")
            # Fallback to just using the user task
            result = self.crew().kickoff(
                inputs={
                    "user_task": user_task,
                    "domain": "",
                    "process_areas": [],
                    "problem_context": "",
                    "input_context": "",
                    "output_context": "",
                    "constraints": []
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