import json
from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field
from crewai.flow.flow import Flow, listen, start
from crewai import Crew, Agent, Task, Process
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

# Import existing models
from src.agent_creator.crew import AgentDefinition, TaskDefinition

# Define CrewPlan model
class CrewPlan:
    """A plan for a crew with agents, tasks and process type."""
    
    def __init__(self, agents: List[AgentDefinition], tasks: List[TaskDefinition], process: str = "sequential"):
        self.agents = agents
        self.tasks = tasks
        self.process = process

# Define structured state models
class AnalysisResult(BaseModel):
    """Results from the Analysis Crew."""
    constraints: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    complexity: int = Field(default=5)
    domain_knowledge: List[str] = Field(default_factory=list)
    time_sensitivity: Dict[str, Any] = Field(default_factory=dict)
    success_criteria: List[str] = Field(default_factory=list)
    recommended_process_type: str = Field(default="sequential")

class PlanningResult(BaseModel):
    """Results from the Planning Crew."""
    selected_algorithm: str
    algorithm_justification: str
    candidate_plans: List[Dict[str, Any]] = Field(default_factory=list)
    selected_plan: Dict[str, Any] = Field(default_factory=dict)
    verification_score: int = Field(default=0)

class ImplementationResult(BaseModel):
    """Results from the Implementation Crew."""
    agents: List[Dict[str, Any]] = Field(default_factory=list)
    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    workflow: Dict[str, Any] = Field(default_factory=dict)
    process_type: str = Field(default="sequential")
    tools: List[Dict[str, Any]] = Field(default_factory=list)

class EvaluationResult(BaseModel):
    """Results from the Evaluation Crew."""
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    missing_elements: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    overall_score: int = Field(default=0)
    improvement_area: str = Field(default="")

class MultiCrewState(BaseModel):
    """State model for multi-crew workflow processes."""
    analysis_result: Optional[AnalysisResult] = None
    planning_result: Optional[PlanningResult] = None
    implementation_result: Optional[ImplementationResult] = None
    evaluation_result: Optional[EvaluationResult] = None
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
    model: str = "gpt-4o"
    temperature: float = 0.7
    user_task: str = ""
    config: Dict[str, Any] = {}
    
    # LLM instances
    llm: Any = None
    
    def __init__(self, user_task: str, config: Dict[str, Any] = None):
        """Initialize the flow with user task and configuration."""
        super().__init__()
        self.user_task = user_task
        self.config = config or {}
    
    @start()
    def run_analysis_crew(self):
        """Start the flow by running the Analysis Crew."""
        print(f"Starting Multi-Crew Flow - ID: {self.state.id}")
        print(f"Processing task: {self.user_task}")
        
        # Initialize LLM
        self._initialize_llm()
        
        # Increment iteration counter
        self.state.analysis_iterations += 1
        
        # Create and run the Analysis Crew
        analysis_result = self._run_analysis_crew(self.user_task)
        
        # Store in state
        self.state.analysis_result = AnalysisResult(**analysis_result)
        
        print(f"Analysis complete. Complexity: {analysis_result['complexity']}")
        print(f"Recommended process type: {analysis_result['recommended_process_type']}")
        
        return analysis_result
    
    @listen(run_analysis_crew)
    def run_planning_crew(self, analysis_result):
        """Run the Planning Crew with hierarchical process."""
        # Increment iteration counter
        self.state.planning_iterations += 1
        
        # Create and run the Planning Crew
        planning_result = self._run_planning_crew(self.user_task, analysis_result)
        
        # Store in state
        self.state.planning_result = PlanningResult(**planning_result)
        
        print(f"Planning complete. Selected algorithm: {planning_result['selected_algorithm']}")
        print(f"Verification score: {planning_result['verification_score']}")
        
        return planning_result
    
    @listen(run_planning_crew)
    def run_implementation_crew(self, planning_result):
        """Run the Implementation Crew with sequential process."""
        # Increment iteration counter
        self.state.implementation_iterations += 1
        
        # Get analysis result from state
        analysis_result = self.state.analysis_result.dict()
        
        # Create and run the Implementation Crew
        implementation_result = self._run_implementation_crew(
            self.user_task, 
            analysis_result,
            planning_result
        )
        
        # Store in state
        self.state.implementation_result = ImplementationResult(**implementation_result)
        
        print(f"Implementation complete. {len(implementation_result['agents'])} agents defined.")
        print(f"Process type: {implementation_result['process_type']}")
        
        return implementation_result
    
    @listen(run_implementation_crew)
    def run_evaluation_crew(self, implementation_result):
        """Run the Evaluation Crew with hierarchical process."""
        # Increment iteration counter
        self.state.evaluation_iterations += 1
        
        # Get previous results from state
        analysis_result = self.state.analysis_result.dict()
        planning_result = self.state.planning_result.dict()
        
        # Create and run the Evaluation Crew
        evaluation_result = self._run_evaluation_crew(
            self.user_task,
            analysis_result,
            planning_result,
            implementation_result
        )
        
        # Store in state
        self.state.evaluation_result = EvaluationResult(**evaluation_result)
        
        # Add to iteration history
        self.state.iteration_history.append({
            "iteration": len(self.state.iteration_history) + 1,
            "analysis": analysis_result,
            "planning": planning_result,
            "implementation": implementation_result,
            "evaluation": evaluation_result
        })
        
        print(f"Evaluation complete. Overall score: {evaluation_result['overall_score']}")
        
        # Determine if refinement is needed
        if evaluation_result['overall_score'] < 7 and sum([
            self.state.analysis_iterations,
            self.state.planning_iterations,
            self.state.implementation_iterations
        ]) < 9:  # Limit total iterations
            # Determine which crew needs to refine based on improvement_area
            improvement_area = evaluation_result['improvement_area']
            
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
            if evaluation_result['overall_score'] >= 7:
                print("Evaluation score meets threshold. Proceeding with current results.")
            else:
                print("Maximum iterations reached. Proceeding with best available results.")
                
            return {
                "implementation": implementation_result,
                "evaluation": evaluation_result,
                "needs_refinement": False
            }
    
    @listen(run_evaluation_crew)
    def finalize_crew_config(self, evaluation_data):
        """Converts the final implementation into executable crew configuration."""
        # Check if we're getting a refined result or the evaluation results
        if isinstance(evaluation_data, dict) and "implementation" in evaluation_data:
            implementation_result = evaluation_data["implementation"]
            evaluation_result = evaluation_data["evaluation"]
        else:
            # This is a direct evaluation result from a refinement cycle
            implementation_result = self.state.implementation_result.dict()
            evaluation_result = evaluation_data
        
        # Convert to crew plan with agents and tasks
        agents = []
        for agent_def in implementation_result["agents"]:
            agents.append(
                AgentDefinition(
                    name=agent_def["name"],
                    role=agent_def["role"],
                    goal=agent_def["goal"],
                    backstory=agent_def["backstory"]
                )
            )
        
        tasks = []
        for task_def in implementation_result["tasks"]:
            dependencies = task_def.get("dependencies", [])
            tasks.append(
                TaskDefinition(
                    name=task_def["name"],
                    purpose=task_def["description"],
                    dependencies=dependencies,
                    complexity=task_def.get("complexity", "Medium")
                )
            )
        
        # Create crew plan
        crew_plan = CrewPlan(
            agents=agents, 
            tasks=tasks,
            process=implementation_result.get("process_type", "sequential")
        )
        
        # Store in state
        self.state.final_plan = crew_plan
        
        print("Crew configuration finalized.")
        print(f"Agents: {len(agents)}, Tasks: {len(tasks)}")
        print(f"Process type: {implementation_result.get('process_type', 'sequential')}")
        
        return crew_plan
    
    # =====================================================================
    # Crew implementation methods
    # =====================================================================
    
    def _run_analysis_crew(self, user_task):
        """Run the Analysis Crew to analyze requirements."""
        # This would normally create a CrewAI crew, but we'll simulate with direct LLM calls
        response = self._call_llm(f"""
        You are an Analysis Crew consisting of a Constraint Analyst, Requirements Engineer, and Domain Expert.
        Analyze the following user task to extract key information.

        # User Task
        {user_task}

        # Analysis Instructions
        Work together to identify:
        1. All explicit and implicit constraints
        2. Core requirements for the solution
        3. Complexity level (1-10)
        4. Required domain knowledge
        5. Time sensitivity
        6. Success criteria
        7. Recommended process type (sequential or hierarchical) based on task characteristics

        # Output Format
        Provide a JSON object with these fields:
        - constraints: List of specific limitations or boundaries
        - requirements: List of necessary elements
        - complexity: Numeric rating (1-10)
        - domain_knowledge: List of relevant domains
        - time_sensitivity: Object with is_critical (boolean) and reasoning (string)
        - success_criteria: List of measurable outcomes
        - recommended_process_type: Either "sequential" or "hierarchical" with explanation
        """)
        
        # Parse response as JSON
        try:
            return json.loads(response)
        except:
            # Fallback with basic structure if parsing fails
            return {
                "constraints": [],
                "requirements": [],
                "complexity": 5,
                "domain_knowledge": [],
                "time_sensitivity": {"is_critical": False, "reasoning": ""},
                "success_criteria": [],
                "recommended_process_type": "sequential"
            }
    
    def _run_planning_crew(self, user_task, analysis_result):
        """Run the Planning Crew with hierarchical process."""
        # This simulates a hierarchical planning crew with algorithm specialists
        response = self._call_llm(f"""
        You are a Planning Crew with a hierarchical structure:
        - Planning Manager (you): Oversees the planning process and selects specialists
        - Best-of-N Generator: Creates multiple plans and selects the best
        - Tree-of-Thoughts Agent: Explores multiple reasoning paths
        - REBASE Agent: Recursively breaks down problems
        - Verification Agent: Evaluates plan quality
        
        Based on the user task and analysis, determine the best planning approach and generate a solution.

        # User Task
        {user_task}

        # Analysis Results
        {json.dumps(analysis_result, indent=2)}

        # Planning Instructions
        As the Planning Manager:
        1. Select the most appropriate algorithm approach based on task complexity and domain
        2. Delegate to the relevant specialist agent to generate candidate solutions
        3. Have the Verification Agent score each candidate
        4. Select or synthesize the final approach

        # Output Format
        Provide a JSON object with these fields:
        - selected_algorithm: Which algorithm was chosen (Best-of-N, Tree of Thoughts, or REBASE)
        - algorithm_justification: Why this algorithm is appropriate
        - candidate_plans: Array of plan outlines (at least 2-3 different approaches)
        - selected_plan: The final selected plan with detailed agent/task structure
        - verification_score: Quality score of the selected plan (1-10)
        """)
        
        # Parse response as JSON
        try:
            return json.loads(response)
        except:
            # Fallback with basic structure if parsing fails
            return {
                "selected_algorithm": "Best-of-N Planning",
                "algorithm_justification": "Default approach for moderate complexity tasks",
                "candidate_plans": [],
                "selected_plan": {},
                "verification_score": 5
            }
    
    def _run_implementation_crew(self, user_task, analysis_result, planning_result):
        """Run the Implementation Crew with sequential process."""
        # This simulates a sequential implementation crew
        response = self._call_llm(f"""
        You are an Implementation Crew consisting of:
        - Agent Engineer: Designs agent capabilities
        - Task Designer: Creates task definitions
        - Workflow Specialist: Defines execution order
        - Integration Expert: Ensures system coherence

        Your job is to convert the planning concept into executable agent and task definitions.

        # User Task
        {user_task}

        # Analysis Results
        {json.dumps(analysis_result, indent=2)}

        # Planning Results
        {json.dumps(planning_result, indent=2)}

        # Implementation Instructions
        Work sequentially to:
        1. Define detailed agent characteristics (name, role, goal, backstory)
        2. Create specific task specifications with clear purposes
        3. Structure task dependencies and workflow
        4. Ensure all parts integrate correctly

        # Output Format
        Provide a JSON object with these fields:
        - agents: Array of agent definitions (each with name, role, goal, backstory)
        - tasks: Array of task definitions (each with name, description, assigned_to, dependencies)
        - workflow: Object with sequence and parallel_tasks information
        - process_type: Recommended process type ("sequential" or "hierarchical")
        - tools: Array of tools needed by the agents
        """)
        
        # Parse response as JSON
        try:
            return json.loads(response)
        except:
            # Fallback with basic structure if parsing fails
            return {
                "agents": [],
                "tasks": [],
                "workflow": {"sequence": []},
                "process_type": "sequential",
                "tools": []
            }
    
    def _run_evaluation_crew(self, user_task, analysis_result, planning_result, implementation_result):
        """Run the Evaluation Crew with hierarchical process."""
        # This simulates a hierarchical evaluation crew
        response = self._call_llm(f"""
        You are an Evaluation Crew with a hierarchical structure:
        - QA Manager (you): Coordinates evaluation activities
        - Completeness Tester: Checks for coverage gaps
        - Efficiency Analyst: Evaluates resource usage
        - Alignment Validator: Ensures solution meets user needs

        Evaluate the proposed crew implementation against the user task and requirements.

        # User Task
        {user_task}

        # Analysis Results
        {json.dumps(analysis_result, indent=2)}

        # Planning Results
        {json.dumps(planning_result, indent=2)}

        # Implementation Results
        {json.dumps(implementation_result, indent=2)}

        # Evaluation Instructions
        As the QA Manager:
        1. Define clear evaluation criteria based on completeness, efficiency, feasibility, and alignment
        2. Delegate testing to the specialist evaluators
        3. Synthesize feedback and determine overall quality
        4. Identify areas for improvement

        # Output Format
        Provide a JSON object with these fields:
        - strengths: List of strongest aspects of the implementation
        - weaknesses: List of areas needing improvement
        - missing_elements: Critical components that are missing
        - recommendations: Specific improvement suggestions
        - overall_score: Quality rating (1-10)
        - improvement_area: Which area needs most refinement ("analysis", "planning", "implementation", or "none")
        """)
        
        # Parse response as JSON
        try:
            return json.loads(response)
        except:
            # Fallback with basic structure if parsing fails
            return {
                "strengths": [],
                "weaknesses": [],
                "missing_elements": [],
                "recommendations": [],
                "overall_score": 5,
                "improvement_area": "none"
            }
    
    # =====================================================================
    # Helper methods
    # =====================================================================
    
    def _initialize_llm(self):
        """Initialize the language model with configuration."""
        self.llm = ChatOpenAI(
            base_url=self.config.get("api_base", None),
            api_key=self.config.get("api_key", None),
            model=self.config.get("model_name", self.model),
            temperature=self.config.get("temperature", self.temperature),
            streaming=False
        )
    
    def _call_llm(self, prompt):
        """Helper method to call the LLM with a prompt."""
        if not hasattr(self, 'llm') or self.llm is None:
            self._initialize_llm()
            
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        return response.content


def create_crew_with_flow(user_task: str, config: Dict[str, Any] = None) -> CrewPlan:
    """Creates a crew plan using the Multi-Crew Flow approach."""
    flow = MultiCrewFlow(user_task=user_task, config=config or {})
    result = flow.kickoff()
    
    # Result is the CrewPlan
    return result