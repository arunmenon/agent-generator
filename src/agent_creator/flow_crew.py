import json
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start

# Import existing models
from src.agent_creator.crew import CrewPlan, AgentDefinition, TaskDefinition


class AgentState(BaseModel):
    """State model for agent workflow processes."""
    task_analysis: Optional[Dict[str, Any]] = None
    algorithm_selection: Optional[Dict[str, Any]] = None
    initial_plan: Optional[Dict[str, Any]] = None
    evaluation: Optional[Dict[str, Any]] = None
    refined_plan: Optional[Dict[str, Any]] = None
    final_plan: Optional[CrewPlan] = None
    iteration_count: int = 0
    feedback_history: List[Dict[str, Any]] = []


class MetaCrewFlow(Flow[AgentState]):
    """Hierarchical flow implementation for creating a crew based on a user request."""
    
    # Configuration properties
    model: str = "gpt-4o"
    temperature: float = 0.7
    user_task: str = ""
    config: Dict[str, Any] = {}
    
    def __init__(self, user_task: str, config: Dict[str, Any] = None):
        """Initialize the flow with user task and configuration."""
        super().__init__()
        self.user_task = user_task
        self.config = config or {}
    
    @start()
    def analyze_requirements(self):
        """Entry point that analyzes user requirements and task constraints."""
        print(f"Starting MetaCrew Flow - ID: {self.state.id}")
        
        # Initialize LLM and configuration
        self._initialize_llm()
        
        # Create analysis subtasks
        task_analysis = self._analyze_task(self.user_task)
        self.state.task_analysis = task_analysis
        
        # Select planning algorithm based on task complexity
        algorithm_selection = self._select_planning_algorithm(task_analysis)
        self.state.algorithm_selection = algorithm_selection
        
        return {
            "task_analysis": task_analysis,
            "algorithm_selection": algorithm_selection
        }
    
    @listen(analyze_requirements)
    def generate_initial_plan(self, analysis_results):
        """Creates the initial plan based on the analysis results."""
        task_analysis = analysis_results["task_analysis"]
        algorithm_selection = analysis_results["algorithm_selection"]
        
        # Generate the initial plan
        initial_plan = self._create_initial_plan(
            self.user_task,
            task_analysis,
            algorithm_selection
        )
        
        # Store in state
        self.state.initial_plan = initial_plan
        return initial_plan
    
    @listen(generate_initial_plan)
    def evaluate_and_refine(self, initial_plan):
        """Evaluates the initial plan and initiates refinement if needed."""
        # Evaluate the plan
        evaluation = self._evaluate_plan(
            self.user_task,
            initial_plan,
            self.state.task_analysis
        )
        
        # Store in state
        self.state.evaluation = evaluation
        
        # Determine if refinement is needed
        needs_refinement = evaluation["overall_score"] < 7
        
        if needs_refinement:
            print(f"Plan needs refinement. Current score: {evaluation['overall_score']}")
            refined_plan = self._refine_plan(
                initial_plan,
                evaluation,
                self.state.task_analysis
            )
            self.state.refined_plan = refined_plan
            self.state.iteration_count += 1
            
            # Add to feedback history
            self.state.feedback_history.append({
                "iteration": self.state.iteration_count,
                "evaluation": evaluation,
                "plan_before": initial_plan,
                "plan_after": refined_plan
            })
            
            return {
                "plan": refined_plan,
                "evaluation": evaluation,
                "is_refined": True
            }
        else:
            print(f"Initial plan meets quality threshold. Score: {evaluation['overall_score']}")
            return {
                "plan": initial_plan,
                "evaluation": evaluation,
                "is_refined": False
            }
    
    @listen(evaluate_and_refine)
    def finalize_crew_config(self, refinement_result):
        """Converts the final plan into executable crew configuration."""
        final_plan_data = refinement_result["plan"]
        evaluation = refinement_result["evaluation"]
        
        # Convert to crew plan with agents and tasks
        agents = []
        for agent_def in final_plan_data["agents"]:
            agents.append(
                AgentDefinition(
                    name=agent_def["name"],
                    role=agent_def["role"],
                    goal=agent_def["goal"],
                    backstory=agent_def["backstory"]
                )
            )
        
        tasks = []
        for task_def in final_plan_data["tasks"]:
            dependencies = task_def.get("dependencies", [])
            tasks.append(
                TaskDefinition(
                    name=task_def["name"],
                    purpose=task_def["description"],
                    dependencies=dependencies,
                    complexity="Medium"  # Default value, can be refined
                )
            )
        
        crew_plan = CrewPlan(agents=agents, tasks=tasks)
        self.state.final_plan = crew_plan
        
        return crew_plan
    
    # Helper methods to implement the actual functionality
    def _initialize_llm(self):
        """Initialize the language model with configuration."""
        from langchain.chat_models import ChatOpenAI
        
        self.llm = ChatOpenAI(
            base_url=self.config.get("api_base", None),
            api_key=self.config.get("api_key", None),
            model=self.config.get("model_name", self.model),
            temperature=self.config.get("temperature", self.temperature),
            streaming=False
        )
    
    def _analyze_task(self, user_task):
        """Analyze the user task to extract constraints and requirements."""
        response = self._call_llm(f"""
        Based on the following user task, identify the key constraints, requirements, and parameters
        that will influence how we should structure our crew.

        # User Task
        {user_task}

        # Output Format
        Provide a JSON object with these fields:
        - constraints: List of specific limitations or boundaries that the solution must respect
        - requirements: List of all necessary elements that must be present in the solution
        - complexity: Task complexity on a scale of 1-10
        - domain_knowledge: Domains of expertise needed
        - time_sensitivity: Object with is_critical (boolean) and reasoning (string)
        - success_criteria: How will we know when the task is successfully completed
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
                "success_criteria": []
            }
    
    def _select_planning_algorithm(self, task_analysis):
        """Select planning algorithm based on task complexity and needs."""
        response = self._call_llm(f"""
        Based on the following task analysis, determine the most appropriate planning algorithm to use.

        # Task Analysis
        {json.dumps(task_analysis, indent=2)}

        # Available Planning Algorithms
        1. Best-of-N Planning: Generate multiple plans and select the best one based on evaluation criteria.
        2. Tree of Thoughts (ToT): Explore multiple reasoning paths and select the most promising one.
        3. REBASE: Recursively break down the problem, evaluate solutions, and synthesize the final approach.

        # Output Format
        Provide a JSON object with these fields:
        - selected_algorithm: Name of the selected algorithm (one of the three listed above)
        - justification: Why this algorithm is most appropriate for this task
        - expected_benefits: List of advantages this algorithm provides for this specific task
        - potential_drawbacks: List of limitations or concerns with using this algorithm
        """)
        
        # Parse response as JSON
        try:
            return json.loads(response)
        except:
            # Fallback with basic structure if parsing fails
            return {
                "selected_algorithm": "Best-of-N Planning",
                "justification": "Simple and efficient baseline approach",
                "expected_benefits": ["Easy to implement", "Produces reliable results"],
                "potential_drawbacks": ["May not find optimal solutions for complex tasks"]
            }
    
    def _create_initial_plan(self, user_task, task_analysis, algorithm_selection):
        """Create an initial plan for the crew based on the analysis."""
        response = self._call_llm(f"""
        Create an initial plan for a crew that will tackle the following user task.

        # User Task
        {user_task}

        # Task Analysis
        {json.dumps(task_analysis, indent=2)}

        # Selected Planning Algorithm
        {json.dumps(algorithm_selection, indent=2)}

        # Output Format
        Create a detailed plan as a JSON object with these fields:
        - agents: List of agents needed, each with name, role, goal, and backstory
        - tasks: List of tasks to perform, each with name, description, assigned_to, and optional dependencies
        - workflow: Object with sequence (task order) and optional parallel_tasks
        - tools: List of tools needed, each with name, purpose, and used_by (list of agent names)
        - expected_outcome: Clear description of the expected result
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
                "tools": [],
                "expected_outcome": ""
            }
    
    def _evaluate_plan(self, user_task, initial_plan, task_analysis):
        """Evaluate the initial plan and provide feedback for improvement."""
        response = self._call_llm(f"""
        Evaluate the following plan for a crew that will tackle a user task.

        # User Task
        {user_task}

        # Task Analysis
        {json.dumps(task_analysis, indent=2)}

        # Initial Plan
        {json.dumps(initial_plan, indent=2)}

        # Evaluation Criteria
        1. Completeness: Does the plan cover all aspects needed to fulfill the task?
        2. Efficiency: Is the plan structured to minimize redundancy and maximize resource utilization?
        3. Feasibility: Is the plan realistically executable given typical constraints?
        4. Alignment: How well does the plan align with the user's stated goals and constraints?
        5. Risk Management: Does the plan account for potential issues or failures?

        # Output Format
        Provide a JSON object with these fields:
        - strengths: List of strongest aspects of the plan
        - weaknesses: List of areas that need improvement
        - missing_elements: List of critical components absent from the plan
        - redundancies: List of unnecessary duplication or overlap
        - improvement_suggestions: List of specific suggestions for enhancing the plan
        - overall_score: Rating on a scale of 1-10
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
                "redundancies": [],
                "improvement_suggestions": [],
                "overall_score": 5
            }
    
    def _refine_plan(self, initial_plan, evaluation, task_analysis):
        """Refine the plan based on the evaluation feedback."""
        response = self._call_llm(f"""
        Refine the following plan based on the evaluation feedback.

        # Initial Plan
        {json.dumps(initial_plan, indent=2)}

        # Evaluation
        {json.dumps(evaluation, indent=2)}

        # Task Analysis
        {json.dumps(task_analysis, indent=2)}

        # Refinement Instructions
        1. Address all weaknesses identified in the evaluation
        2. Add any missing elements
        3. Remove or consolidate redundancies
        4. Implement the improvement suggestions where appropriate
        5. Ensure the refined plan is complete, efficient, feasible, aligned with user goals, and manages risks effectively

        # Output Format
        Provide a refined plan with the same structure as the initial plan, but with improvements based on the evaluation.
        Use exactly the same JSON format as the initial plan, with these fields:
        - agents: List of agents needed, each with name, role, goal, and backstory
        - tasks: List of tasks to perform, each with name, description, assigned_to, and optional dependencies
        - workflow: Object with sequence (task order) and optional parallel_tasks
        - tools: List of tools needed, each with name, purpose, and used_by (list of agent names)
        - expected_outcome: Clear description of the expected result
        """)
        
        # Parse response as JSON
        try:
            return json.loads(response)
        except:
            # Fallback if parsing fails
            return initial_plan
    
    def _call_llm(self, prompt):
        """Helper method to call the LLM with a prompt."""
        from langchain.schema import HumanMessage
        
        if not hasattr(self, 'llm'):
            self._initialize_llm()
            
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        return response.content


def create_crew_with_flow(user_task: str, config: Dict[str, Any] = None) -> CrewPlan:
    """Creates a crew plan using the Flow-based approach."""
    flow = MetaCrewFlow(user_task=user_task, config=config or {})
    result = flow.kickoff()
    
    # Result is the CrewPlan
    return result