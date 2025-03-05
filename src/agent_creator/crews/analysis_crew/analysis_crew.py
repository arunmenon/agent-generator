"""
Analysis Crew implementation for user task analysis.
"""

from crewai import Crew, Process
from typing import Dict, Any, Optional
import json
import logging

# Get logger
logger = logging.getLogger(__name__)

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
        import os
        
        # Print debug info
        logger.info(f"Initializing LLM with config: {self.config}")
        logger.info(f"OPENAI_API_KEY environment variable set: {'Yes' if os.environ.get('OPENAI_API_KEY') else 'No'}")
        
        # Use environment variable as fallback if not in config
        api_key = self.config.get("api_key", os.environ.get("OPENAI_API_KEY"))
        
        # Get supported parameters
        try:
            from inspect import signature
            llm_sig = signature(LLM)
            logger.info(f"LLM constructor parameters: {list(llm_sig.parameters.keys())}")
        except Exception as e:
            logger.error(f"Failed to get supported params: {str(e)}")
        
        try:
            # Create LLM with minimal parameters
            llm = LLM(model=self.config.get("model_name", "gpt-4o"))
            logger.info("Successfully created LLM with minimal parameters")
            return llm
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}", exc_info=True)
            
            # Fallback to default parameters
            return LLM(model="gpt-4o")
        
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
        
    def analyze(
        self, 
        user_task: str,
        domain: str = "",
        process_areas: List[str] = None,
        problem_context: str = "",
        input_context: str = "",
        output_context: str = "",
        constraints: List[str] = None
    ) -> AnalysisOutput:
        """
        Analyze the user task and return structured analysis.
        
        Args:
            user_task: The user's task description
            domain: The domain or industry context
            process_areas: Specific process areas within the domain
            problem_context: Detailed context about the problem being solved
            input_context: Description of the inputs available to the system
            output_context: Description of the expected outputs from the system
            constraints: Limitations or requirements that must be followed
            
        Returns:
            AnalysisOutput containing analysis results
        """
        # Prepare inputs with additional context
        inputs = {
            "user_task": user_task,
            "domain": domain,
            "process_areas": process_areas or [],
            "problem_context": problem_context,
            "input_context": input_context,
            "output_context": output_context,
            "constraints": constraints or []
        }
        
        # Run the crew with the enriched context
        result = self.crew().kickoff(inputs=inputs)
        
        # Extract the analysis data, handling both string and dict formats
        if isinstance(result.raw, str):
            try:
                analysis_data = json.loads(result.raw)
            except json.JSONDecodeError:
                # Fallback if the output isn't valid JSON
                analysis_data = {
                    "constraints": constraints or [],
                    "requirements": [],
                    "complexity": 5,
                    "domain_knowledge": [],
                    "time_sensitivity": {"is_critical": False, "reasoning": ""},
                    "success_criteria": [],
                    "recommended_process_type": "sequential",
                    "domain": domain,
                    "process_areas": process_areas or [],
                    "problem_context": problem_context,
                    "input_context": input_context,
                    "output_context": output_context
                }
        else:
            analysis_data = result.raw
        
        # Convert to AnalysisOutput model
        return AnalysisOutput(**analysis_data)