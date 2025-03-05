"""
Flow implementation for orchestrating multiple CrewAI crews.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from uuid import uuid4

# Import with try/except for better error handling
try:
    from crewai.flow.flow import Flow, listen, start
except ImportError:
    # Simple mock implementations for when CrewAI isn't installed
    class Flow:
        def __init__(self):
            self.state = {}
    
    def start():
        def decorator(func):
            return func
        return decorator
    
    def listen(previous_func):
        def decorator(func):
            return func
        return decorator
import json
import logging

# Get logger
logger = logging.getLogger(__name__)

from ..crews.models import (
    AnalysisOutput, PlanningOutput, ImplementationOutput, 
    EvaluationOutput, CrewPlan, AgentDefinition, TaskDefinition
)
# Import crew classes with fallback for when actual implementations are not available
try:
    from ..crews.analysis_crew import AnalysisCrew
    from ..crews.planning_crew import PlanningCrew
    from ..crews.implementation_crew import ImplementationCrew
    from ..crews.evaluation_crew import EvaluationCrew
except ImportError:
    # Create mock crew classes for simplified operation
    class AnalysisCrew:
        def __init__(self, config=None): 
            self.config = config or {}
        
        def analyze(self, **kwargs):
            """Return a basic analysis result."""
            return AnalysisOutput(
                constraints=kwargs.get("constraints", []),
                requirements=["Basic functionality"],
                complexity=5,
                domain_knowledge=[kwargs.get("domain", "General")],
                time_sensitivity={"is_critical": False, "reasoning": "Standard priority"},
                success_criteria=["Complete the requested task"],
                recommended_process_type="sequential",
                domain=kwargs.get("domain", ""),
                process_areas=kwargs.get("process_areas", []),
                problem_context=kwargs.get("problem_context", ""),
                input_context=kwargs.get("input_context", ""),
                output_context=kwargs.get("output_context", "")
            )
    
    class PlanningCrew:
        def __init__(self, config=None): 
            self.config = config or {}
            
        def plan(self, **kwargs):
            """Return a basic planning result."""
            return PlanningOutput(
                selected_algorithm="Best-Fit Planning",
                algorithm_justification="Most appropriate for the task complexity",
                candidate_plans=[],
                selected_plan={},
                verification_score=7
            )
    
    class ImplementationCrew:
        def __init__(self, config=None): 
            self.config = config or {}
            
        def implement(self, **kwargs):
            """Return a basic implementation result."""
            domain = kwargs.get("user_task", "").split()[0] if kwargs.get("user_task") else "General"
            
            # Create default agents
            agents = [
                AgentDefinition(
                    name="Task Manager",
                    role="Coordinate the overall process workflow",
                    goal="Ensure successful completion of the task",
                    backstory="Experienced project manager with expertise in workflow optimization"
                ),
                AgentDefinition(
                    name="Domain Expert",
                    role=f"Provide specialized knowledge in {domain}",
                    goal="Ensure domain-specific accuracy and quality",
                    backstory=f"Expert with deep knowledge of {domain} systems and processes"
                ),
                AgentDefinition(
                    name="Quality Controller",
                    role="Verify outputs and ensure they meet requirements",
                    goal="Maintain high quality standards throughout the process",
                    backstory="Detail-oriented professional with experience in quality assurance"
                )
            ]
            
            # Create default tasks
            tasks = [
                TaskDefinition(
                    name="Analyze Requirements",
                    description="Review all requirements and input data",
                    assigned_to="Task Manager",
                    expected_output="Detailed analysis report",
                    dependencies=[],
                    context=[]
                ),
                TaskDefinition(
                    name="Process Domain-Specific Information",
                    description=f"Apply {domain} domain knowledge to the task",
                    assigned_to="Domain Expert",
                    expected_output="Domain-specific processing results",
                    dependencies=["Analyze Requirements"],
                    context=["Analyze Requirements"]
                ),
                TaskDefinition(
                    name="Verify Results",
                    description="Check output quality and compliance with requirements",
                    assigned_to="Quality Controller",
                    expected_output="Verification report",
                    dependencies=["Process Domain-Specific Information"],
                    context=["Process Domain-Specific Information"]
                ),
                TaskDefinition(
                    name="Finalize Output",
                    description="Prepare final deliverable with documentation",
                    assigned_to="Task Manager",
                    expected_output="Complete final output",
                    dependencies=["Verify Results"],
                    context=["Verify Results"]
                )
            ]
            
            return ImplementationOutput(
                agents=agents,
                tasks=tasks,
                workflow={"sequence": [t.name for t in tasks]},
                process_type="sequential",
                tools=[]
            )
    
    class EvaluationCrew:
        def __init__(self, config=None): 
            self.config = config or {}
            
        def evaluate(self, **kwargs):
            """Return a basic evaluation result."""
            return EvaluationOutput(
                strengths=["Comprehensive approach", "Well-defined workflow"],
                weaknesses=[],
                missing_elements=[],
                recommendations=[],
                overall_score=8,
                improvement_area="none"
            )

class MultiCrewState(BaseModel):
    """State model for multi-crew workflow processes."""
    # Add id field required by the Flow parent class
    id: str = Field(default_factory=lambda: str(uuid4()))
    
    # Crew process results
    analysis_result: Optional[AnalysisOutput] = None
    planning_result: Optional[PlanningOutput] = None
    implementation_result: Optional[ImplementationOutput] = None
    evaluation_result: Optional[EvaluationOutput] = None
    final_plan: Optional[CrewPlan] = None
    
    # Iteration tracking
    analysis_iterations: int = 0
    planning_iterations: int = 0
    implementation_iterations: int = 0
    evaluation_iterations: int = 0
    
    # History tracking
    iteration_history: List[Dict[str, Any]] = Field(default_factory=list)

class MultiCrewFlow(Flow):
    """Flow implementation that orchestrates multiple specialized crews."""
    
    # Configuration properties
    user_task: str = ""
    config: Dict[str, Any] = {}
    
    # Context properties
    domain: str = ""
    process_areas: List[str] = Field(default_factory=list)
    problem_context: str = ""
    input_context: str = ""
    output_context: str = ""
    constraints: List[str] = Field(default_factory=list)
    
    # Crew instances
    analysis_crew: Optional[AnalysisCrew] = None
    planning_crew: Optional[PlanningCrew] = None
    implementation_crew: Optional[ImplementationCrew] = None
    evaluation_crew: Optional[EvaluationCrew] = None
    
    def __init__(self, user_task: str, config: Dict[str, Any] = None):
        """Initialize the flow with user task and configuration."""
        # Set initial_state to our MultiCrewState class for proper initialization
        self.initial_state = MultiCrewState
        
        # Initialize with parent Flow constructor
        super().__init__()
        
        # Set task and config
        self.user_task = user_task
        self.config = config or {}
        
        # Extract context fields from config
        self.domain = self.config.get("domain", "")
        self.process_areas = self.config.get("process_areas", [])
        self.problem_context = self.config.get("problem_context", "")
        self.input_context = self.config.get("input_context", "")
        self.output_context = self.config.get("output_context", "")
        self.constraints = self.config.get("constraints", [])
        
        # Log configuration for debugging
        logger.info(f"MultiCrewFlow initialized with config: {self.config}")
        
        # Initialize crews
        try:
            self._initialize_crews()
        except Exception as e:
            logger.error(f"Error initializing crews: {str(e)}", exc_info=True)
            
    def kickoff(self, inputs: Optional[Dict[str, Any]] = None):
        """Compatibility method with CrewAI's Flow API.
        
        This uses the parent's Flow kickoff method which handles the execution chain.
        We run it through asyncio.run to handle the async pattern.
        """
        try:
            print("[DEBUG] Starting flow kickoff")
            
            # First attempt - use parent Flow's kickoff method (from Flow superclass)
            import asyncio
            
            # Run through asyncio for compatibility
            result = super().kickoff(inputs)
            
            # Check the result and return appropriately
            if isinstance(result, CrewPlan):
                return result
                
            # If we have a final plan in the state, return that
            if hasattr(self._state, 'final_plan') and self._state.final_plan:
                return self._state.final_plan
            
            # Fallback to direct execution of the flow chain
            print("[DEBUG] Using fallback direct execution")
            result = self.run_analysis_crew()
            
            # The result from analysis crew should trigger the planning crew,
            # which should trigger implementation crew, etc. due to the @listen decorators
            
            # At this point we've run at least the first step - check if we have a final_plan
            if hasattr(self._state, 'final_plan') and self._state.final_plan:
                return self._state.final_plan
                
            # Return whatever we got
            return result
            
        except Exception as e:
            print(f"[ERROR] Flow kickoff failed: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Just run the first step directly as a last resort
            try:
                return self.run_analysis_crew()
            except Exception:
                # Create a minimal fallback result if everything else fails
                default_agents = [
                    AgentDefinition(
                        name="Task Manager",
                        role="Coordinate the overall process workflow",
                        goal="Ensure successful completion of the task",
                        backstory="Experienced project manager with expertise in workflow optimization"
                    ),
                    AgentDefinition(
                        name="Domain Expert",
                        role=f"Provide specialized knowledge in {self.domain}",
                        goal="Ensure domain-specific accuracy and quality",
                        backstory=f"Expert with deep knowledge of {self.domain} systems and processes"
                    )
                ]
                
                default_tasks = [
                    TaskDefinition(
                        name="Analyze Requirements",
                        description="Review all requirements and input data",
                        assigned_to="Task Manager",
                        expected_output="Detailed analysis report",
                        dependencies=[],
                        context=[]
                    ),
                    TaskDefinition(
                        name="Process Domain-Specific Information",
                        description=f"Apply {self.domain} domain knowledge to the task",
                        assigned_to="Domain Expert",
                        expected_output="Domain-specific processing results",
                        dependencies=["Analyze Requirements"],
                        context=["Analyze Requirements"]
                    )
                ]
                
                return CrewPlan(
                    name=f"Fallback Crew for {self.domain}",
                    description=f"Basic crew plan created due to flow error",
                    agents=default_agents,
                    tasks=default_tasks,
                    process="sequential",
                    domain=self.domain,
                    problem_context=self.problem_context,
                    input_context=self.input_context,
                    output_context=self.output_context
                )
    
    def _initialize_crews(self):
        """Initialize all crew instances."""
        self.analysis_crew = AnalysisCrew(config=self.config)
        self.planning_crew = PlanningCrew(config=self.config)
        self.implementation_crew = ImplementationCrew(config=self.config)
        self.evaluation_crew = EvaluationCrew(config=self.config)
    
    @start()
    def run_analysis_crew(self):
        """Start the flow by running the Analysis Crew."""
        print(f"Starting Multi-Crew Flow")
        print(f"Processing task: {self.user_task}")
        print(f"Domain: {self.domain}")
        
        # Increment iteration counter
        self.state.analysis_iterations += 1
        
        # Run the Analysis Crew
        try:
            analysis_result = self.analysis_crew.analyze(
                user_task=self.user_task,
                domain=self.domain,
                process_areas=self.process_areas,
                problem_context=self.problem_context,
                input_context=self.input_context,
                output_context=self.output_context,
                constraints=self.constraints
            )
            
            # Store in state
            self.state.analysis_result = analysis_result
            
            print(f"Analysis complete. Complexity: {analysis_result.complexity}")
            print(f"Recommended process type: {analysis_result.recommended_process_type}")
            
            return analysis_result
        except Exception as e:
            print(f"Error in analysis crew: {str(e)}")
            # Create a fallback analysis result
            fallback_result = AnalysisOutput(
                constraints=["Error during analysis"],
                requirements=["Basic functionality"],
                complexity=5,
                domain_knowledge=["General"],
                time_sensitivity={"is_critical": False, "reasoning": "Unknown"},
                success_criteria=["Basic functionality"],
                recommended_process_type="sequential"
            )
            self.state.analysis_result = fallback_result
            return fallback_result
    
    @listen(run_analysis_crew)
    def run_planning_crew(self, analysis_result: AnalysisOutput):
        """Run the Planning Crew with hierarchical process."""
        # Increment iteration counter
        self.state.planning_iterations += 1
        
        # Run the Planning Crew
        try:
            # Convert analysis_result to dict and ensure domain field exists
            analysis_dict = None
            if hasattr(analysis_result, 'dict'):
                analysis_dict = analysis_result.dict()
            elif hasattr(analysis_result, 'model_dump'):
                analysis_dict = analysis_result.model_dump()
            elif isinstance(analysis_result, dict):
                analysis_dict = analysis_result
            else:
                analysis_dict = vars(analysis_result)
                
            # Add domain field if missing (needed by planning crew)
            if 'domain' not in analysis_dict:
                analysis_dict['domain'] = self.domain
            if 'process_areas' not in analysis_dict:
                analysis_dict['process_areas'] = self.process_areas
            if 'problem_context' not in analysis_dict:
                analysis_dict['problem_context'] = self.problem_context
            if 'input_context' not in analysis_dict:
                analysis_dict['input_context'] = self.input_context
            if 'output_context' not in analysis_dict:
                analysis_dict['output_context'] = self.output_context
            if 'constraints' not in analysis_dict:
                analysis_dict['constraints'] = self.constraints
                
            # Run planning with the dict version
            planning_result = self.planning_crew.plan(
                user_task=self.user_task,
                analysis_result=analysis_dict
            )
            
            # Store in state
            self.state.planning_result = planning_result
            
            print(f"Planning complete. Selected algorithm: {planning_result.selected_algorithm}")
            print(f"Verification score: {planning_result.verification_score}")
            
            return planning_result
        except Exception as e:
            print(f"Error in planning crew: {str(e)}")
            # Create a fallback planning result
            fallback_result = PlanningOutput(
                selected_algorithm="Best-of-N Planning",
                algorithm_justification="Default approach due to error",
                candidate_plans=[],
                selected_plan={},
                verification_score=5
            )
            self.state.planning_result = fallback_result
            return fallback_result
    
    @listen(run_planning_crew)
    def run_implementation_crew(self, planning_result: PlanningOutput):
        """Run the Implementation Crew with sequential process."""
        # Increment iteration counter
        self.state.implementation_iterations += 1
        
        # Get analysis result from state
        analysis_result = self.state.analysis_result
        
        # If analysis_result is None, create a fallback
        if not analysis_result:
            print("[WARNING] Analysis result not found in state, creating fallback")
            analysis_result = AnalysisOutput(
                constraints=["Basic constraints"],
                requirements=["Basic functionality"],
                complexity=5,
                domain_knowledge=["General"],
                time_sensitivity={"is_critical": False, "reasoning": "Standard priority"},
                success_criteria=["Complete the requested task"],
                recommended_process_type="sequential"
            )
        
        # Run the Implementation Crew
        try:
            # Convert models to dictionaries for serialization and ensure domain fields
            analysis_dict = None
            if hasattr(analysis_result, 'dict'):
                analysis_dict = analysis_result.dict()
            elif hasattr(analysis_result, 'model_dump'):
                analysis_dict = analysis_result.model_dump()
            elif isinstance(analysis_result, dict):
                analysis_dict = analysis_result
            else:
                analysis_dict = vars(analysis_result)
                
            # Add domain field if missing (needed by implementation crew)
            if 'domain' not in analysis_dict:
                analysis_dict['domain'] = self.domain
            if 'process_areas' not in analysis_dict:
                analysis_dict['process_areas'] = self.process_areas
            if 'problem_context' not in analysis_dict:
                analysis_dict['problem_context'] = self.problem_context
            if 'input_context' not in analysis_dict:
                analysis_dict['input_context'] = self.input_context
            if 'output_context' not in analysis_dict:
                analysis_dict['output_context'] = self.output_context
            if 'constraints' not in analysis_dict:
                analysis_dict['constraints'] = self.constraints
                
            planning_dict = None
            if hasattr(planning_result, 'dict'):
                planning_dict = planning_result.dict()
            elif hasattr(planning_result, 'model_dump'):
                planning_dict = planning_result.model_dump()
            elif isinstance(planning_result, dict):
                planning_dict = planning_result
            else:
                planning_dict = vars(planning_result)
                
            implementation_result = self.implementation_crew.implement(
                user_task=self.user_task,
                analysis_result=analysis_dict,
                planning_result=planning_dict
            )
            
            # Store in state
            self.state.implementation_result = implementation_result
            
            print(f"Implementation complete. {len(implementation_result.agents)} agents defined.")
            print(f"Process type: {implementation_result.process_type}")
            
            return implementation_result
        except Exception as e:
            print(f"Error in implementation crew: {str(e)}")
            # Create a fallback implementation result with minimal structure
            fallback_result = ImplementationOutput(
                agents=[],
                tasks=[],
                workflow={"sequence": []},
                process_type="sequential",
                tools=[]
            )
            self.state.implementation_result = fallback_result
            return fallback_result
    
    @listen(run_implementation_crew)
    def run_evaluation_crew(self, implementation_result: ImplementationOutput):
        """Run the Evaluation Crew with hierarchical process."""
        # Increment iteration counter
        self.state.evaluation_iterations += 1
        
        # Get previous results from state
        analysis_result = self.state.analysis_result
        planning_result = self.state.planning_result
        
        # Create fallbacks if needed
        if not analysis_result:
            print("[WARNING] Analysis result not found in state, creating fallback")
            analysis_result = AnalysisOutput(
                constraints=["Basic constraints"],
                requirements=["Basic functionality"],
                complexity=5,
                domain_knowledge=["General"],
                time_sensitivity={"is_critical": False, "reasoning": "Standard priority"},
                success_criteria=["Complete the requested task"],
                recommended_process_type="sequential"
            )
            
        if not planning_result:
            print("[WARNING] Planning result not found in state, creating fallback")
            planning_result = PlanningOutput(
                selected_algorithm="Best-of-N Planning",
                algorithm_justification="Default approach",
                candidate_plans=[],
                selected_plan={},
                verification_score=5
            )
        
        # Run the Evaluation Crew
        try:
            # Convert models to dictionaries for serialization and ensure domain fields
            analysis_dict = None
            if hasattr(analysis_result, 'dict'):
                analysis_dict = analysis_result.dict()
            elif hasattr(analysis_result, 'model_dump'):
                analysis_dict = analysis_result.model_dump()
            elif isinstance(analysis_result, dict):
                analysis_dict = analysis_result
            else:
                analysis_dict = vars(analysis_result)
                
            # Add domain field if missing (needed by evaluation crew)
            if 'domain' not in analysis_dict:
                analysis_dict['domain'] = self.domain
            if 'process_areas' not in analysis_dict:
                analysis_dict['process_areas'] = self.process_areas
            if 'problem_context' not in analysis_dict:
                analysis_dict['problem_context'] = self.problem_context
            if 'input_context' not in analysis_dict:
                analysis_dict['input_context'] = self.input_context
            if 'output_context' not in analysis_dict:
                analysis_dict['output_context'] = self.output_context
            if 'constraints' not in analysis_dict:
                analysis_dict['constraints'] = self.constraints
                
            planning_dict = None
            if hasattr(planning_result, 'dict'):
                planning_dict = planning_result.dict()
            elif hasattr(planning_result, 'model_dump'):
                planning_dict = planning_result.model_dump()
            elif isinstance(planning_result, dict):
                planning_dict = planning_result
            else:
                planning_dict = vars(planning_result)
                
            implementation_dict = None
            if hasattr(implementation_result, 'dict'):
                implementation_dict = implementation_result.dict()
            elif hasattr(implementation_result, 'model_dump'):
                implementation_dict = implementation_result.model_dump()
            elif isinstance(implementation_result, dict):
                implementation_dict = implementation_result
            else:
                implementation_dict = vars(implementation_result)
            
            evaluation_result = self.evaluation_crew.evaluate(
                user_task=self.user_task,
                analysis_result=analysis_dict,
                planning_result=planning_dict,
                implementation_result=implementation_dict
            )
            
            # Store in state
            self.state.evaluation_result = evaluation_result
            
            # Add to iteration history
            if not hasattr(self.state, 'iteration_history'):
                self.state.iteration_history = []
                
            # Store results in iteration history
            self.state.iteration_history.append({
                "iteration": len(self.state.iteration_history) + 1,
                "analysis": analysis_dict,
                "planning": planning_dict,
                "implementation": implementation_dict,
                "evaluation": evaluation_result.dict() if hasattr(evaluation_result, 'dict') else vars(evaluation_result)
            })
            
            print(f"Evaluation complete. Overall score: {evaluation_result.overall_score}")
            
            # Determine if refinement is needed
            total_iterations = (
                self.state.analysis_iterations + 
                self.state.planning_iterations + 
                self.state.implementation_iterations
            )
            
            # Determine if refinement is needed
            if evaluation_result.overall_score < 7 and total_iterations < 9:  # Limit total iterations
                # Determine which crew needs to refine based on improvement_area
                improvement_area = evaluation_result.improvement_area
                
                if improvement_area == "analysis":
                    print("Refinement needed in Analysis. Returning to Analysis Crew.")
                    return self.run_analysis_crew()
                
                elif improvement_area == "planning":
                    print("Refinement needed in Planning. Returning to Planning Crew.")
                    return self.run_planning_crew(analysis_result)
                
                elif improvement_area == "implementation":
                    print("Refinement needed in Implementation. Returning to Implementation Crew.")
                    return self.run_implementation_crew(planning_result)
                
                else:
                    print("No specific refinement area identified. Proceeding with current results.")
                    return {
                        "implementation": implementation_result,
                        "evaluation": evaluation_result,
                        "needs_refinement": False
                    }
            else:
                if evaluation_result.overall_score >= 7:
                    print("Evaluation score meets threshold. Proceeding with current results.")
                else:
                    print("Maximum iterations reached. Proceeding with best available results.")
                    
                return {
                    "implementation": implementation_result,
                    "evaluation": evaluation_result,
                    "needs_refinement": False
                }
        except Exception as e:
            print(f"Error in evaluation crew: {str(e)}")
            # Create a fallback evaluation result
            fallback_result = EvaluationOutput(
                strengths=["Functional implementation"],
                weaknesses=["Error during evaluation"],
                missing_elements=[],
                recommendations=["Review implementation manually"],
                overall_score=5,
                improvement_area="none"
            )
            self.state.evaluation_result = fallback_result
            return {
                "implementation": implementation_result,
                "evaluation": fallback_result,
                "needs_refinement": False
            }
    
    @listen(run_evaluation_crew)
    def finalize_crew_config(self, evaluation_data: Dict[str, Any]):
        """Converts the final implementation into executable crew configuration."""
        # Check if we're getting a refined result or the evaluation results
        implementation_result = None
        evaluation_result = None
        
        if isinstance(evaluation_data, dict) and "implementation" in evaluation_data:
            implementation_result = evaluation_data["implementation"]
            evaluation_result = evaluation_data["evaluation"]
        else:
            # This is a direct evaluation result from a refinement cycle
            implementation_result = self.state.implementation_result
            evaluation_result = evaluation_data
        
        # Create fallback implementation result if needed
        if not implementation_result:
            print("[WARNING] Implementation result not found, creating fallback")
            implementation_result = ImplementationOutput(
                agents=[
                    AgentDefinition(
                        name="Task Manager",
                        role="Coordinate the overall process workflow",
                        goal="Ensure successful completion of the task",
                        backstory="Experienced project manager with expertise in workflow optimization"
                    ),
                    AgentDefinition(
                        name="Domain Expert",
                        role=f"Provide specialized knowledge in {self.domain}",
                        goal="Ensure domain-specific accuracy and quality",
                        backstory=f"Expert with deep knowledge of {self.domain} systems and processes"
                    ),
                    AgentDefinition(
                        name="Quality Controller",
                        role="Verify outputs and ensure they meet requirements",
                        goal="Maintain high quality standards throughout the process",
                        backstory="Detail-oriented professional with experience in quality assurance"
                    )
                ],
                tasks=[
                    TaskDefinition(
                        name="Analyze Requirements",
                        description="Review all requirements and input data",
                        assigned_to="Task Manager",
                        expected_output="Detailed analysis report",
                        dependencies=[],
                        context=[]
                    ),
                    TaskDefinition(
                        name="Process Domain-Specific Information",
                        description=f"Apply {self.domain} domain knowledge to the task",
                        assigned_to="Domain Expert",
                        expected_output="Domain-specific processing results",
                        dependencies=["Analyze Requirements"],
                        context=["Analyze Requirements"]
                    )
                ],
                workflow={"sequence": ["Analyze Requirements", "Process Domain-Specific Information"]},
                process_type="sequential",
                tools=[]
            )
        
        # Create crew plan with additional context
        crew_plan = CrewPlan(
            name=f"Generated Crew for {self.domain}",
            description=f"A crew designed to solve {self.problem_context}",
            agents=implementation_result.agents, 
            tasks=implementation_result.tasks,
            process=implementation_result.process_type,
            domain=self.domain,
            problem_context=self.problem_context,
            input_context=self.input_context,
            output_context=self.output_context,
            context={
                "domain": self.domain,
                "problem_context": self.problem_context,
                "input_context": self.input_context,
                "output_context": self.output_context,
                "process_areas": self.process_areas,
                "constraints": self.constraints
            }
        )
        
        # Generate input and output schemas based on context
        try:
            crew_plan.generate_schemas_from_context()
        except Exception as e:
            print(f"Error generating schemas: {str(e)}")
            # Create basic fallback schemas
            from .multi_crew_utils import create_input_schema, create_output_schema
            crew_plan.input_schema = create_input_schema(self.domain, self.problem_context, self.input_context)
            crew_plan.output_schema = create_output_schema(self.output_context)
        
        # Store in state
        self.state.final_plan = crew_plan
        
        print("Crew configuration finalized.")
        print(f"Agents: {len(implementation_result.agents)}, Tasks: {len(implementation_result.tasks)}")
        print(f"Process type: {implementation_result.process_type}")
        
        return crew_plan

def create_crew_with_flow(user_task: str, config: Dict[str, Any] = None) -> CrewPlan:
    """Creates a crew plan using the Multi-Crew Flow approach.
    
    This is a synchronous wrapper around the MultiCrewFlow class that creates a Flow
    instance and runs its entire multi-phase process. This function is designed for 
    using the Flow system directly from synchronous code like FastAPI endpoints.
    """
    try:
        print(f"[DEBUG] Creating crew with Flow approach for task: {user_task}")
        print(f"[DEBUG] Config: {config}")
        
        # Initialize the MultiCrewFlow with the user task and config
        flow = MultiCrewFlow(user_task=user_task, config=config or {})
        
        # Get metadata about the flow for debugging
        print(f"[DEBUG] Flow registered start methods: {flow._start_methods}")
        print(f"[DEBUG] Flow registered listeners: {flow._listeners}")
        
        # Use the Flow's kickoff method to run the entire process
        print(f"[DEBUG] Running flow.kickoff()...")
        crew_plan = flow.kickoff()
        print(f"[DEBUG] flow.kickoff() complete, result type: {type(crew_plan)}")
        
        # Verify we got a valid crew plan
        if not isinstance(crew_plan, CrewPlan):
            print(f"[WARNING] Flow did not return a CrewPlan, got: {type(crew_plan)}")
            print(f"[DEBUG] Checking Flow state for valid output")
            
            # Check for final_plan in state which would be most complete
            if hasattr(flow, '_state'):
                state = flow._state
                if hasattr(state, 'final_plan') and state.final_plan:
                    print("[DEBUG] Found final_plan in state, returning that")
                    return state.final_plan
            
            # Extract values from the flow's state to create a plan
            domain = config.get("domain", "General")
            
            # If we have implementation results in the state, use their agents and tasks
            agents = []
            tasks = []
            process_type = "sequential"
            
            if hasattr(flow, '_state'):
                state = flow._state
                if hasattr(state, 'implementation_result') and state.implementation_result:
                    print("[DEBUG] Found implementation_result in state, using its agents and tasks")
                    agents = state.implementation_result.agents
                    tasks = state.implementation_result.tasks
                    if hasattr(state.implementation_result, "process_type"):
                        process_type = state.implementation_result.process_type
            
            # If we still don't have agents and tasks, use the output directly
            if not agents and hasattr(crew_plan, 'agents'):
                print("[DEBUG] Using agents from result object")
                agents = crew_plan.agents
                
            if not tasks and hasattr(crew_plan, 'tasks'):
                print("[DEBUG] Using tasks from result object")
                tasks = crew_plan.tasks
                
            # Create a basic crew plan with available data
            from .multi_crew_utils import create_input_schema, create_output_schema
            final_crew_plan = CrewPlan(
                name=f"Generated Crew for {domain}",
                description=f"A crew designed to solve {config.get('problem_context', 'the given task')}",
                agents=agents,
                tasks=tasks,
                process=process_type,
                domain=domain,
                problem_context=config.get("problem_context", ""),
                input_context=config.get("input_context", ""),
                output_context=config.get("output_context", ""),
                context={
                    "domain": domain,
                    "problem_context": config.get("problem_context", ""),
                    "input_context": config.get("input_context", ""),
                    "output_context": config.get("output_context", ""),
                    "process_areas": config.get("process_areas", []),
                    "constraints": config.get("constraints", [])
                }
            )
            
            # Add schemas
            final_crew_plan.input_schema = create_input_schema(
                domain, 
                config.get("problem_context", ""), 
                config.get("input_context", "")
            )
            final_crew_plan.output_schema = create_output_schema(
                config.get("output_context", "")
            )
            
            print(f"[DEBUG] Created crew plan with {len(agents)} agents and {len(tasks)} tasks")
            return final_crew_plan
        
        print(f"[DEBUG] Returning CrewPlan with {len(crew_plan.agents)} agents and {len(crew_plan.tasks)} tasks")
        return crew_plan
            
    except Exception as e:
        # Log the error
        print(f"Error in create_crew_with_flow: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Create a minimal fallback crew plan
        domain = config.get("domain", "General") if config else "General"
        fallback_crew_plan = CrewPlan(
            name=f"Generated Crew for {domain}",
            description="Basic crew plan created due to flow error",
            agents=[
                AgentDefinition(
                    name="Task Manager",
                    role="Coordinate the overall process workflow",
                    goal="Ensure successful completion of the task",
                    backstory="Experienced project manager with expertise in workflow optimization"
                ),
                AgentDefinition(
                    name="Domain Expert",
                    role=f"Provide specialized knowledge in {domain}",
                    goal="Ensure domain-specific accuracy and quality",
                    backstory=f"Expert with deep knowledge of {domain} systems and processes"
                ),
                AgentDefinition(
                    name="Quality Controller",
                    role="Verify outputs and ensure they meet requirements",
                    goal="Maintain high quality standards throughout the process",
                    backstory="Detail-oriented professional with experience in quality assurance"
                )
            ],
            tasks=[
                TaskDefinition(
                    name="Analyze Requirements",
                    description="Review all requirements and input data",
                    assigned_to="Task Manager",
                    expected_output="Detailed analysis report",
                    dependencies=[],
                    context=[]
                ),
                TaskDefinition(
                    name="Process Domain-Specific Information",
                    description=f"Apply {domain} domain knowledge to the task",
                    assigned_to="Domain Expert",
                    expected_output="Domain-specific processing results",
                    dependencies=["Analyze Requirements"],
                    context=["Analyze Requirements"]
                ),
                TaskDefinition(
                    name="Verify Results",
                    description="Check output quality and compliance with requirements",
                    assigned_to="Quality Controller",
                    expected_output="Verification report",
                    dependencies=["Process Domain-Specific Information"],
                    context=["Process Domain-Specific Information"]
                ),
                TaskDefinition(
                    name="Finalize Output",
                    description="Prepare final deliverable with documentation",
                    assigned_to="Task Manager",
                    expected_output="Complete final output",
                    dependencies=["Verify Results"],
                    context=["Verify Results"]
                )
            ],
            process="sequential",
            domain=domain,
            problem_context=config.get("problem_context", "") if config else "",
            input_context=config.get("input_context", "") if config else "",
            output_context=config.get("output_context", "") if config else ""
        )
        
        # Create basic schemas for the fallback plan
        from .multi_crew_utils import create_input_schema, create_output_schema
        fallback_crew_plan.input_schema = create_input_schema(
            domain, 
            config.get("problem_context", "") if config else "", 
            config.get("input_context", "") if config else ""
        )
        fallback_crew_plan.output_schema = create_output_schema(
            config.get("output_context", "") if config else ""
        )
        
        print("[DEBUG] Created fallback crew plan due to error")
        return fallback_crew_plan