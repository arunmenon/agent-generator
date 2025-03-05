"""
Flow implementation for orchestrating multiple CrewAI crews.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from crewai.flow.flow import Flow, listen, start
import json
import logging

# Get logger
logger = logging.getLogger(__name__)

from ..crews.models import (
    AnalysisOutput, PlanningOutput, ImplementationOutput, 
    EvaluationOutput, CrewPlan, AgentDefinition, TaskDefinition
)
from ..crews.analysis_crew import AnalysisCrew
from ..crews.planning_crew import PlanningCrew
from ..crews.implementation_crew import ImplementationCrew
from ..crews.evaluation_crew import EvaluationCrew

class MultiCrewState(BaseModel):
    """State model for multi-crew workflow processes."""
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

class MultiCrewFlow(Flow[MultiCrewState]):
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
        super().__init__()
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
    
    def _initialize_crews(self):
        """Initialize all crew instances."""
        self.analysis_crew = AnalysisCrew(config=self.config)
        self.planning_crew = PlanningCrew(config=self.config)
        self.implementation_crew = ImplementationCrew(config=self.config)
        self.evaluation_crew = EvaluationCrew(config=self.config)
    
    @start()
    def run_analysis_crew(self):
        """Start the flow by running the Analysis Crew."""
        print(f"Starting Multi-Crew Flow - ID: {self.state.id}")
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
            planning_result = self.planning_crew.plan(
                user_task=self.user_task,
                analysis_result=analysis_result
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
        
        # Run the Implementation Crew
        try:
            implementation_result = self.implementation_crew.implement(
                user_task=self.user_task,
                analysis_result=analysis_result,
                planning_result=planning_result
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
        
        # Run the Evaluation Crew
        try:
            evaluation_result = self.evaluation_crew.evaluate(
                user_task=self.user_task,
                analysis_result=analysis_result,
                planning_result=planning_result,
                implementation_result=implementation_result
            )
            
            # Store in state
            self.state.evaluation_result = evaluation_result
            
            # Add to iteration history
            self.state.iteration_history.append({
                "iteration": len(self.state.iteration_history) + 1,
                "analysis": analysis_result.dict(),
                "planning": planning_result.dict(),
                "implementation": implementation_result.dict(),
                "evaluation": evaluation_result.dict()
            })
            
            print(f"Evaluation complete. Overall score: {evaluation_result.overall_score}")
            
            # Determine if refinement is needed
            if evaluation_result.overall_score < 7 and sum([
                self.state.analysis_iterations,
                self.state.planning_iterations,
                self.state.implementation_iterations
            ]) < 9:  # Limit total iterations
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
        if isinstance(evaluation_data, dict) and "implementation" in evaluation_data:
            implementation_result = evaluation_data["implementation"]
            evaluation_result = evaluation_data["evaluation"]
        else:
            # This is a direct evaluation result from a refinement cycle
            implementation_result = self.state.implementation_result
            evaluation_result = evaluation_data
        
        # Use agents and tasks directly, don't convert to dict and back
        # This preserves the interpolation placeholders
        
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
        crew_plan.generate_schemas_from_context()
        
        # Store in state
        self.state.final_plan = crew_plan
        
        print("Crew configuration finalized.")
        print(f"Agents: {len(implementation_result.agents)}, Tasks: {len(implementation_result.tasks)}")
        print(f"Process type: {implementation_result.process_type}")
        
        return crew_plan

def create_crew_with_flow(user_task: str, config: Dict[str, Any] = None) -> CrewPlan:
    """Creates a crew plan using the Multi-Crew Flow approach."""
    flow = MultiCrewFlow(user_task=user_task, config=config or {})
    result = flow.kickoff()
    
    # Result is the CrewPlan
    return result