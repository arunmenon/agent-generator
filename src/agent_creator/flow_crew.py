import json
from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field

# Import existing models
from src.agent_creator.crew import AgentDefinition, TaskDefinition

# Define CrewPlan model
class CrewPlan:
    """A plan for a crew with agents, tasks and process type."""
    
    def __init__(self, agents: List[AgentDefinition], tasks: List[TaskDefinition], process: str = "sequential"):
        self.agents = agents
        self.tasks = tasks
        self.process = process

# Define simplified models (without BaseModel inheritance)
class AnalysisResult:
    """Results from the Analysis Crew."""
    def __init__(self, 
                 constraints: List[str] = None,
                 requirements: List[str] = None, 
                 complexity: int = 5,
                 domain_knowledge: List[str] = None,
                 time_sensitivity: Dict[str, Any] = None,
                 success_criteria: List[str] = None,
                 recommended_process_type: str = "sequential"):
        self.constraints = constraints or []
        self.requirements = requirements or []
        self.complexity = complexity
        self.domain_knowledge = domain_knowledge or []
        self.time_sensitivity = time_sensitivity or {}
        self.success_criteria = success_criteria or []
        self.recommended_process_type = recommended_process_type
    
    def dict(self):
        return {
            "constraints": self.constraints,
            "requirements": self.requirements,
            "complexity": self.complexity,
            "domain_knowledge": self.domain_knowledge,
            "time_sensitivity": self.time_sensitivity,
            "success_criteria": self.success_criteria,
            "recommended_process_type": self.recommended_process_type
        }

class PlanningResult:
    """Results from the Planning Crew."""
    def __init__(self,
                 selected_algorithm: str,
                 algorithm_justification: str,
                 candidate_plans: List[Dict[str, Any]] = None,
                 selected_plan: Dict[str, Any] = None,
                 verification_score: int = 0):
        self.selected_algorithm = selected_algorithm
        self.algorithm_justification = algorithm_justification
        self.candidate_plans = candidate_plans or []
        self.selected_plan = selected_plan or {}
        self.verification_score = verification_score
    
    def dict(self):
        return {
            "selected_algorithm": self.selected_algorithm,
            "algorithm_justification": self.algorithm_justification,
            "candidate_plans": self.candidate_plans,
            "selected_plan": self.selected_plan,
            "verification_score": self.verification_score
        }

class ImplementationResult:
    """Results from the Implementation Crew."""
    def __init__(self,
                 agents: List[Dict[str, Any]] = None,
                 tasks: List[Dict[str, Any]] = None,
                 workflow: Dict[str, Any] = None,
                 process_type: str = "sequential",
                 tools: List[Dict[str, Any]] = None):
        self.agents = agents or []
        self.tasks = tasks or []
        self.workflow = workflow or {}
        self.process_type = process_type
        self.tools = tools or []
    
    def dict(self):
        return {
            "agents": self.agents,
            "tasks": self.tasks,
            "workflow": self.workflow,
            "process_type": self.process_type,
            "tools": self.tools
        }

class EvaluationResult:
    """Results from the Evaluation Crew."""
    def __init__(self,
                 strengths: List[str] = None,
                 weaknesses: List[str] = None,
                 missing_elements: List[str] = None,
                 recommendations: List[str] = None,
                 overall_score: int = 0,
                 improvement_area: str = ""):
        self.strengths = strengths or []
        self.weaknesses = weaknesses or []
        self.missing_elements = missing_elements or []
        self.recommendations = recommendations or []
        self.overall_score = overall_score
        self.improvement_area = improvement_area
    
    def dict(self):
        return {
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "missing_elements": self.missing_elements,
            "recommendations": self.recommendations,
            "overall_score": self.overall_score,
            "improvement_area": self.improvement_area
        }

class MultiCrewState:
    """State model for multi-crew workflow processes."""
    def __init__(self):
        self.id = "mock-flow-id"
        self.analysis_result = None
        self.planning_result = None
        self.implementation_result = None
        self.evaluation_result = None
        self.final_plan = None
        
        # Iteration tracking
        self.analysis_iterations = 0
        self.planning_iterations = 0
        self.implementation_iterations = 0
        self.evaluation_iterations = 0
        
        # History tracking
        self.iteration_history = []


class MultiCrewFlow:
    """Mock implementation of the flow that orchestrates multiple specialized crews."""
    
    def __init__(self, user_task: str, config: Dict[str, Any] = None):
        """Initialize the flow with user task and configuration."""
        self.user_task = user_task
        self.config = config or {}
        self.state = MultiCrewState()
        
        # Default config values
        self.model = self.config.get("model_name", "gpt-4o")
        self.temperature = self.config.get("temperature", 0.7)
    
    def kickoff(self):
        """Kickoff the flow process with a mock implementation."""
        print(f"Starting mock Multi-Crew Flow for task: {self.user_task}")
        
        # Run a simulated flow without real LLM calls
        agents = [
            AgentDefinition(
                name="Customer Service Agent",
                role="Handle customer inquiries and provide helpful responses",
                goal="Ensure customer satisfaction",
                backstory="Experienced in customer support with deep product knowledge"
            ),
            AgentDefinition(
                name="Product Specialist",
                role="Provide detailed product information",
                goal="Give accurate product details and recommendations",
                backstory="Expert in the product catalog and features"
            ),
            AgentDefinition(
                name="Returns Handler",
                role="Process return requests efficiently",
                goal="Make the returns process smooth and transparent",
                backstory="Knowledgeable about company return policies and procedures"
            )
        ]
        
        tasks = [
            TaskDefinition(
                name="Greet and identify customer needs",
                purpose="Establish rapport and understand customer requirements",
                dependencies=[],
                complexity="Low"
            ),
            TaskDefinition(
                name="Provide product information",
                purpose="Answer detailed questions about products",
                dependencies=["Greet and identify customer needs"],
                complexity="Medium"
            ),
            TaskDefinition(
                name="Process return requests",
                purpose="Handle returns efficiently according to policy",
                dependencies=["Greet and identify customer needs"],
                complexity="Medium"
            )
        ]
        
        # Create crew plan
        crew_plan = CrewPlan(
            agents=agents, 
            tasks=tasks,
            process="sequential"
        )
        
        # Store in state
        self.state.final_plan = crew_plan
        
        # Log completion
        print("Mock flow complete. Created a customer service crew.")
        
        return crew_plan


def create_crew_with_flow(user_task: str, config: Dict[str, Any] = None) -> CrewPlan:
    """Creates a crew plan using the Multi-Crew Flow approach."""
    flow = MultiCrewFlow(user_task=user_task, config=config or {})
    result = flow.kickoff()
    
    # Result is the CrewPlan
    return result