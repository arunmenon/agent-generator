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
        
        # LiteLLM client has issues with provider and streaming parameters
        return LLM(
            model=self.config.get("model_name", "gpt-4o"),
            temperature=self.config.get("temperature", 0.7)
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
        
    def evaluate(self, user_task: str, analysis_result: Dict[str, Any], 
                planning_result: Dict[str, Any], 
                implementation_result: Dict[str, Any]) -> EvaluationOutput:
        """
        Evaluate the quality and completeness of an implementation.
        
        Args:
            user_task: The user's task description
            analysis_result: Results from the Analysis Crew (as dictionary)
            planning_result: Results from the Planning Crew (as dictionary)
            implementation_result: Results from the Implementation Crew (as dictionary)
            
        Returns:
            EvaluationOutput with assessment results and recommendations
        """
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
            
            # Run the crew with all previous results and context as input
            result = self.crew().kickoff(
                inputs={
                    "user_task": user_task,
                    "analysis_result": analysis_result,  # Pass the dictionary
                    "planning_result": planning_result,  # Pass the dictionary
                    "implementation_result": implementation_result,  # Pass the dictionary
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