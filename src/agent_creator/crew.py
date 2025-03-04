# src/agent_creator/crew.py

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, task, crew, before_kickoff

class CrewConfig(BaseModel):
    crew: Dict[str, Any]
    agents: Any
    tasks: Any
    input_schema_json: Any

# Structured data models for agent communication
class UserRequirements(BaseModel):
    """Structured user requirements extracted from input."""
    description: str = Field(..., description="High-level description of the project")
    input_description: str = Field(..., description="Description of input data sources")
    output_description: str = Field(..., description="Description of expected output format")
    tools: List[str] = Field(default_factory=list, description="List of tools to use")
    process: str = Field(default="sequential", description="Process type (sequential or hierarchical)")
    planning: bool = Field(default=False, description="Whether to use planning")
    knowledge: bool = Field(default=False, description="Whether to use knowledge")
    human_input_tasks: bool = Field(default=False, description="Whether to use human input tasks")
    memory: bool = Field(default=False, description="Whether to use memory")
    cache: bool = Field(default=False, description="Whether to use cache")
    manager_llm: Optional[str] = Field(default=None, description="Manager LLM to use")

class PlanConstraint(BaseModel):
    """Represents a constraint that plans must satisfy."""
    name: str = Field(..., description="Short identifier for the constraint")
    description: str = Field(..., description="Detailed explanation of the constraint")
    validation_prompt: str = Field(..., description="Prompt to check if a plan satisfies this constraint")

class ConstraintList(BaseModel):
    """List of constraints extracted from requirements."""
    constraints: List[PlanConstraint] = Field(default_factory=list)

class TaskDefinition(BaseModel):
    """Definition of a task in a plan."""
    name: str = Field(..., description="Name of the task")
    purpose: str = Field(..., description="Purpose or goal of the task")
    dependencies: List[str] = Field(default_factory=list, description="Tasks this task depends on")
    complexity: str = Field(default="Medium", description="Complexity level (Low, Medium, High)")

class AgentDefinition(BaseModel):
    """Definition of an agent in a plan."""
    name: str = Field(..., description="Name of the agent")
    role: str = Field(..., description="Role of the agent")
    goal: str = Field(..., description="Goal of the agent")
    backstory: str = Field(default="", description="Backstory of the agent")

class ConceptualPlan(BaseModel):
    """Conceptual plan with tasks and agent types."""
    planned_tasks: List[TaskDefinition] = Field(default_factory=list)
    required_agent_types: List[AgentDefinition] = Field(default_factory=list)

class Plan(BaseModel):
    """Represents a complete plan generated by an agent."""
    name: str = Field(..., description="Name of the plan")
    content: str = Field(..., description="Detailed description of the plan")
    planned_tasks: List[TaskDefinition] = Field(default_factory=list)
    required_agent_types: List[AgentDefinition] = Field(default_factory=list)
    score: Optional[float] = Field(default=None, description="Overall score of the plan")
    constraints_satisfied: List[str] = Field(default_factory=list, description="Constraints satisfied by this plan")
    constraints_violated: List[str] = Field(default_factory=list, description="Constraints violated by this plan")

class PlanEvaluation(BaseModel):
    """Evaluation of a plan against constraints."""
    constraints_satisfied: List[str] = Field(default_factory=list)
    constraints_violated: List[str] = Field(default_factory=list)
    completeness: int = Field(..., ge=1, le=10, description="Completeness score (1-10)")
    efficiency: int = Field(..., ge=1, le=10, description="Efficiency score (1-10)")
    feasibility: int = Field(..., ge=1, le=10, description="Feasibility score (1-10)")
    alignment: int = Field(..., ge=1, le=10, description="Alignment with requirements score (1-10)")
    explanations: Dict[str, str] = Field(default_factory=dict)
    total_score: int = Field(..., description="Sum of all scores")

class EvaluatedPlan(BaseModel):
    """Plan with its evaluation."""
    name: str = Field(..., description="Name of the plan")
    evaluation: PlanEvaluation = Field(...)

class PlanEvaluationResult(BaseModel):
    """Result of evaluating multiple plans."""
    evaluated_plans: List[EvaluatedPlan] = Field(...)
    best_plan: str = Field(..., description="Name of the highest scoring plan")

class AlternativePlans(BaseModel):
    """Collection of alternative plans."""
    plans: List[Plan] = Field(...)

class InputSchemaDefinition(BaseModel):
    """Definition of the input schema for the crew."""
    input_schema_json: Dict[str, Any] = Field(default_factory=dict)

class PlanGenResult(BaseModel):
    """Result from running multiple plan generation techniques."""
    best_plan: Plan = Field(...)
    all_plans: List[Plan] = Field(...)
    execution_details: Dict[str, Any] = Field(default_factory=dict)

class AlgorithmSelectionResult(BaseModel):
    """Result of selecting an algorithm for plan generation."""
    algorithm: str = Field(..., description="Selected algorithm (best_of_n, tot, or rebase)")
    reasoning: str = Field(..., description="Reasoning behind the algorithm selection")
    recommended_params: Dict[str, Any] = Field(default_factory=dict, description="Recommended parameters for the algorithm")

class PlanRefinementFeedback(BaseModel):
    """Feedback for refining a plan."""
    constraints_violated: List[str] = Field(default_factory=list, description="Constraints that were violated")
    improvement_suggestions: List[str] = Field(default_factory=list, description="Suggestions for improving the plan")
    satisfied_score: int = Field(..., ge=0, le=100, description="How well the plan satisfied constraints (0-100)")
    needs_refinement: bool = Field(..., description="Whether the plan needs further refinement")
    recommended_algorithm: str = Field(default="same", description="Recommended algorithm for refinement (same, best_of_n, tot, rebase)")

@CrewBase
class MetaCrew():
    def __init__(self, 
                 llm_model="openai/gpt-4", 
                 n_samples=3, 
                 use_best_of_n=True, 
                 use_tot=False,
                 max_refinement_iterations=3,
                 min_satisfaction_threshold=85):
        self.llm_model = llm_model
        # Set verbose=False to reduce debug logs
        self.llm = LLM(model=self.llm_model, temperature=0.2, verbose=False)
        self.inputs: Dict[str, Any] = {}
        # PlanGEN parameters
        self.n_samples = n_samples  # Number of plans to generate for Best-of-N
        self.use_best_of_n = use_best_of_n  # Whether to use Best-of-N sampling
        self.use_tot = use_tot  # Whether to use Tree-of-Thought search
        
        # PlanGEN refinement parameters
        self.max_refinement_iterations = max_refinement_iterations  # Maximum number of refinement iterations
        self.min_satisfaction_threshold = min_satisfaction_threshold  # Minimum satisfaction threshold (0-100)

    @before_kickoff
    def capture_inputs(self, inputs: Dict[str, Any]):
        """
        Store user inputs in self.inputs so placeholders like {user_description}
        get replaced by CrewAI's .format(**inputs) at runtime.
        """
        self.inputs = inputs
        return inputs

    @agent
    def planner_agent(self) -> Agent:
        """
        Agent that proposes conceptual tasks & agent types from user requirements.
        """
        return Agent(
            role="Planning Architect",
            goal=(
                "Transform user requirements into a minimal, cohesive set of tasks "
                "and well-defined agent roles."
            ),
            backstory=(
                "A seasoned planning architect with expertise in orchestrating workflows, "
                "ensuring each task is minimal, actionable, and properly sequenced."
            ),
            llm=self.llm,
            memory=True,
            verbose=False,
            allow_delegation=False,
            max_iter=5,
            respect_context_window=True,
            use_system_prompt=True,
            cache=False,
            max_retry_limit=2,
        )
    
    @agent
    def constraint_agent(self) -> Agent:
        """
        Agent that identifies and validates constraints from user requirements.
        """
        return Agent(
            role="Constraint Analyst",
            goal=(
                "Identify, extract, and formalize constraints from user requirements that "
                "must be satisfied by any valid plan."
            ),
            backstory=(
                "An expert analyst specializing in identifying explicit and implicit constraints "
                "from requirements and formalizing them as validation checks."
            ),
            llm=self.llm,
            memory=True,
            verbose=False,
            allow_delegation=False,
            max_iter=3,
            respect_context_window=True,
            use_system_prompt=True,
            cache=False,
            max_retry_limit=2,
        )
    
    @agent
    def algorithm_selector_agent(self) -> Agent:
        """
        Agent that selects the most appropriate algorithm for a given problem.
        """
        return Agent(
            role="Algorithm Selector",
            goal=(
                "Analyze problem requirements and constraints to select the most appropriate "
                "algorithm for generating an optimal plan."
            ),
            backstory=(
                "An algorithm expert with deep knowledge of various planning and reasoning "
                "approaches, including Best-of-N sampling, Tree-of-Thought (ToT) search, and REBASE, "
                "who can match problem characteristics to the most suitable algorithm."
            ),
            llm=self.llm,
            memory=True,
            verbose=False,
            allow_delegation=False,
            max_iter=3,
            respect_context_window=True,
            use_system_prompt=True,
            cache=False,
            max_retry_limit=2,
        )
    
    @agent
    def plan_evaluator_agent(self) -> Agent:
        """
        Agent that evaluates plans against constraints and provides scores.
        """
        return Agent(
            role="Plan Evaluator",
            goal=(
                "Systematically evaluate plans against all constraints and requirements, "
                "providing clear scores and detailed feedback for refinement."
            ),
            backstory=(
                "A rigorous evaluator with expertise in analyzing plans from multiple angles "
                "and providing objective assessments based on well-defined criteria, as well as "
                "actionable feedback for improvement."
            ),
            llm=self.llm,
            memory=True,
            verbose=False,
            allow_delegation=False,
            max_iter=3,
            respect_context_window=True,
            use_system_prompt=True,
            cache=False,
            max_retry_limit=2,
        )
        
    @agent
    def plan_refiner_agent(self) -> Agent:
        """
        Agent that refines plans based on evaluation feedback.
        """
        return Agent(
            role="Plan Refiner",
            goal=(
                "Refine and improve plans based on evaluation feedback, focusing on "
                "addressing violated constraints and incorporating improvement suggestions."
            ),
            backstory=(
                "An expert plan refiner with a talent for iterative improvement, "
                "capable of understanding evaluation feedback and making targeted "
                "adjustments to strengthen a plan's alignment with constraints."
            ),
            llm=self.llm,
            memory=True,
            verbose=False,
            allow_delegation=False,
            max_iter=4,
            respect_context_window=True,
            use_system_prompt=True,
            cache=False,
            max_retry_limit=2,
        )

    @agent
    def schema_converter(self) -> Agent:
        """
        Agent that merges tasks with input_schema_json and refines the final CrewAI schema.
        Preserves any quadruple-braced placeholders (e.g. {{{{title}}}}).
        """
        return Agent(
            role="Schema Converter",
            goal=(
                "Merge planned tasks/agents with a partial input_schema_json snippet into a final CrewAI config. "
                "Validate each agent/task, fill missing fields, and return the final JSON."
            ),
            backstory=(
                "A schema architect well-versed in CrewAI standards. Ensures tasks/agents are fully defined, "
                "removes extraneous info, and preserves placeholders if relevant."
            ),
            llm=self.llm,
            memory=True,
            verbose=False,
            allow_delegation=False,
            max_iter=5,
            respect_context_window=True,
            use_system_prompt=True,
            cache=False,
            max_retry_limit=2,
        )

    @task
    def gather_user_requirements_task(self) -> Task:
        """
        Gathers raw user inputs with placeholders. CrewAI .format(**inputs) will fill them
        before the LLM sees it. Returns a structured UserRequirements object.
        """
        description = """
Below are user inputs. Extract them into a structured format matching the UserRequirements model:

```python
class UserRequirements(BaseModel):
    description: str
    input_description: str
    output_description: str
    tools: List[str]
    process: str = "sequential"
    planning: bool = False
    knowledge: bool = False
    human_input_tasks: bool = False
    memory: bool = False
    cache: bool = False
    manager_llm: Optional[str] = None
```

Format your response as valid Python code that creates a UserRequirements instance. The user provided:

User Description: {user_description}
User Input Description: {user_input_description}
User Output Description: {user_output_description}
Tools: {user_tools}
Process: {user_process}
Planning: {user_planning}
Knowledge: {user_knowledge}
Human Input Tasks: {user_human_input_tasks}
Memory: {user_memory}
Cache: {user_cache}
Manager LLM: {user_manager_llm}

Your answer should start with "UserRequirements(" and end with ")" and include all fields.
"""
        return Task(
            description=description,
            expected_output="UserRequirements instance with structured user requirements",
            agent=self.planner_agent(),
            output_pydantic=UserRequirements
        )
        
    @task
    def identify_constraints_task(self) -> Task:
        """
        Identifies constraints from user requirements that any valid plan must satisfy.
        Returns a structured ConstraintList object.
        """
        description = r"""
Based on the user requirements:
{{output}}

Identify all constraints that any valid solution must satisfy. These can be explicit requirements 
or implicit constraints based on the problem domain.

Your response should match the following Pydantic models:

```python
class PlanConstraint(BaseModel):
    name: str
    description: str
    validation_prompt: str

class ConstraintList(BaseModel):
    constraints: List[PlanConstraint]
```

For each constraint:
1. Give it a clear name
2. Write a detailed description
3. Provide a validation prompt that could be used to check if a plan satisfies this constraint

Focus on identifying:
- Functional requirements (what the solution must do)
- Performance requirements (how well it must perform)
- Resource constraints (time, budget, tools, etc.)
- Domain-specific rules or limitations
- Dependencies between components

Be thorough and comprehensive - these constraints will be used to evaluate and refine plans.

Format your response as Python code that creates a ConstraintList object containing all identified constraints.
Start with "ConstraintList(constraints=[" and include all PlanConstraint objects.
"""
        return Task(
            description=description,
            expected_output="ConstraintList object with identified constraints",
            agent=self.constraint_agent(),
            context=[self.gather_user_requirements_task()],
            output_pydantic=ConstraintList
        )
        
    @task
    def select_algorithm_task(self) -> Task:
        """
        Selects the most appropriate algorithm for generating a plan based on the problem and constraints.
        Returns an AlgorithmSelectionResult object.
        """
        description = r"""
Based on the user requirements:
{{output}}

And the identified constraints:
{constraints}

Select the most appropriate algorithm for generating a plan. Consider the following algorithms:

1. Best-of-N sampling: Generate multiple plans independently and pick the best one.
   - Good for problems with clear evaluation criteria
   - Benefits from diversity of approaches
   - Can be computationally expensive for large N

2. Tree-of-Thought (ToT) search: Generate a plan step by step, exploring multiple branches at each step.
   - Good for problems that benefit from structured reasoning
   - Helpful when the solution space is large but can be navigated with intermediate feedback
   - Works well for problems that can be broken down into sequential decisions

3. REBASE (REward BAlanced SEarch): A more advanced tree search guided by a learned reward model.
   - Best for complex problems with multiple competing objectives
   - Good when evaluation criteria might be subjective or nuanced
   - Requires more computational resources but can produce more sophisticated plans

Your response should match the following Pydantic model:

```python
class AlgorithmSelectionResult(BaseModel):
    algorithm: str  # One of: "best_of_n", "tot", "rebase"
    reasoning: str
    recommended_params: Dict[str, Any] = {}
```

Analyze the problem characteristics and constraints to determine which algorithm would be most effective.
Consider factors like:
- Problem complexity and structure
- Number and nature of constraints
- Whether the problem benefits from exploration of diverse approaches
- Computational budget considerations

Format your response as Python code that creates an AlgorithmSelectionResult object.
Start with "AlgorithmSelectionResult(" and include your selected algorithm, reasoning, and any recommended parameters.
"""
        description = description.replace("{constraints}", "{{constraints}}")
        
        return Task(
            description=description,
            expected_output="AlgorithmSelectionResult with selected algorithm and reasoning",
            agent=self.algorithm_selector_agent(),
            context=[self.gather_user_requirements_task(), self.identify_constraints_task()],
            output_pydantic=AlgorithmSelectionResult
        )

    @task
    def plan_tasks_and_agents_task(self) -> Task:
        """
        Proposes tasks & agent types using quadruple braces {{{{title}}}} if needed.
        Keep double braces for CrewAI placeholders (e.g. {{output}}).
        Returns a structured ConceptualPlan object.
        """
        # Raw string so Python doesn't treat backslashes/newlines specially.
        # Double braces to avoid KeyError from .format().
        description = r"""
Given these user requirements:
{{output}}

We also have 'inputDescription': {{{{user_input_description}}}}, which might imply placeholders
like {{{{title}}}}, {{{{targetLanguage}}}}, etc.

Your response should match the following Pydantic models:

```python
class TaskDefinition(BaseModel):
    name: str
    purpose: str
    dependencies: List[str] = []
    complexity: str = "Medium"  # Low, Medium, High

class AgentDefinition(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str = ""

class ConceptualPlan(BaseModel):
    planned_tasks: List[TaskDefinition]
    required_agent_types: List[AgentDefinition]
```

**INSTRUCTIONS**:
1. Analyze the user's requirements → produce a conceptual plan:
   - For each task: name, purpose, dependencies, complexity.
   - If relevant to user_input_description, embed placeholders like {{{{title}}}} or {{{{targetLanguage}}}} in the tasks.
2. Determine agent types: role, goal, backstory.
   - If relevant, embed placeholders in those fields (e.g. "Translator for {{{{title}}}}").

Format your response as Python code that creates a ConceptualPlan object.
Start with "ConceptualPlan(" and include all TaskDefinition and AgentDefinition objects.

Example format:
```python
ConceptualPlan(
    planned_tasks=[
        TaskDefinition(
            name="TaskName",
            purpose="Task purpose",
            dependencies=[],
            complexity="Low"
        )
    ],
    required_agent_types=[
        AgentDefinition(
            name="AgentName",
            role="Agent role",
            goal="Agent goal",
            backstory="Agent backstory"
        )
    ]
)
```
"""
        return Task(
            description=description,
            expected_output="ConceptualPlan object with tasks and agent types",
            agent=self.planner_agent(),
            context=[self.gather_user_requirements_task()],
            output_pydantic=ConceptualPlan
        )

    @task
    def interpret_input_description_task(self) -> Task:
        """
        Takes 'inputDescription' from user requirements → partial input_schema_json snippet.
        E.g. if inputDescription says "Title to localize," produce:
        {
          "input_schema_json": {
            "title": {"type": "string", "description": "..."}
          }
        }
        """
        # Here we double any braces in the snippet.
        description = r"""
From user requirements (especially 'inputDescription'):
{{output}}

Your response should match the following Pydantic model:

```python
class InputSchemaDefinition(BaseModel):
    input_schema_json: Dict[str, Any] = {}
```

**INSTRUCTIONS**:
1. Construct partial `input_schema_json` from inputDescription
2. For each input field identified:
   - Set the appropriate type (string, number, boolean, etc.)
   - Add a clear description

Format your response as Python code that creates an InputSchemaDefinition object.
Start with "InputSchemaDefinition(input_schema_json=" and end with ")".

Example format:
```python
InputSchemaDefinition(input_schema_json={
    "title": {"type": "string", "description": "..."},
    "targetLanguage": {"type": "string", "description": "..."}
})
```
"""
        return Task(
            description=description,
            expected_output="InputSchemaDefinition with partial input_schema_json",
            agent=self.schema_converter(),
            context=[self.gather_user_requirements_task()],
            output_pydantic=InputSchemaDefinition
        )

    @task
    def generate_alternative_plans_task(self) -> Task:
        """
        Generates multiple alternative plans for Best-of-N sampling.
        """
        description = r"""
Based on the user requirements:
{{output}}

The constraints identified:
{constraints}

Generate {n_samples} alternative high-quality plans. Each plan should be different 
in approach, but all should meet the core requirements.

Your response should match the following Pydantic models:

```python
class TaskDefinition(BaseModel):
    name: str
    purpose: str
    dependencies: List[str] = []
    complexity: str = "Medium"  # Low, Medium, High

class AgentDefinition(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str = ""

class Plan(BaseModel):
    name: str 
    content: str
    planned_tasks: List[TaskDefinition]
    required_agent_types: List[AgentDefinition]
    
class AlternativePlans(BaseModel):
    plans: List[Plan]
```

For each plan:
1. Give it a descriptive name
2. Provide a comprehensive description of the approach
3. Include the planned tasks and agents similar to the original plan format

Ensure each plan is meaningfully different in:
- Technical approach
- Team composition
- Process flow
- Resource allocation

Format your response as Python code that creates an AlternativePlans object with {n_samples} Plan objects.
Start with "AlternativePlans(plans=[" and include all Plan objects.
"""
        description = description.replace("{n_samples}", str(self.n_samples))
        description = description.replace("{constraints}", "{{constraints}}")
        
        return Task(
            description=description,
            expected_output=f"AlternativePlans object with {self.n_samples} alternative plans",
            agent=self.planner_agent(),
            context=[self.gather_user_requirements_task(), self.identify_constraints_task()],
            output_pydantic=AlternativePlans
        )
    
    @task
    def evaluate_plans_task(self) -> Task:
        """
        Evaluates multiple plans against constraints.
        """
        description = r"""
Evaluate these plans:
{{output}}

Against the identified constraints:
{constraints}

Your response should match the following Pydantic models:

```python
class PlanEvaluation(BaseModel):
    constraints_satisfied: List[str]
    constraints_violated: List[str]
    completeness: int  # 1-10
    efficiency: int  # 1-10
    feasibility: int  # 1-10
    alignment: int  # 1-10
    explanations: Dict[str, str]
    total_score: int

class EvaluatedPlan(BaseModel):
    name: str
    evaluation: PlanEvaluation

class PlanEvaluationResult(BaseModel):
    evaluated_plans: List[EvaluatedPlan]
    best_plan: str  # Name of highest scoring plan
```

For each plan:
1. Check if it satisfies each constraint
2. Rate it on a scale of 1-10 for:
   - Completeness
   - Efficiency
   - Feasibility
   - Alignment with requirements
3. Provide a brief explanation for each rating
4. Calculate total_score as the sum of all scores

Format your response as Python code that creates a PlanEvaluationResult object.
Start with "PlanEvaluationResult(" and include all EvaluatedPlan objects.
Be sure to identify which plan has the highest score and include that name in the 'best_plan' field.
"""
        description = description.replace("{constraints}", "{{constraints}}")
        
        return Task(
            description=description,
            expected_output="PlanEvaluationResult with evaluated plans and best plan",
            agent=self.plan_evaluator_agent(),
            context=[
                self.identify_constraints_task(),
                self.generate_alternative_plans_task() if self.use_best_of_n else self.plan_tasks_and_agents_task()
            ],
            output_pydantic=PlanEvaluationResult
        )
        
    @task
    def provide_plan_feedback_task(self) -> Task:
        """
        Provides detailed feedback on a plan for refinement purposes.
        Returns a PlanRefinementFeedback object.
        """
        description = r"""
Analyze this plan:
{{output}}

Against the identified constraints:
{constraints}

Provide detailed feedback on how well the plan satisfies constraints and what improvements are needed.

Your response should match the following Pydantic model:

```python
class PlanRefinementFeedback(BaseModel):
    constraints_violated: List[str]
    improvement_suggestions: List[str]
    satisfied_score: int  # 0-100
    needs_refinement: bool
    recommended_algorithm: str = "same"  # One of: "same", "best_of_n", "tot", "rebase"
```

Specifically:
1. List all constraints that the plan violates
2. Provide specific, actionable suggestions for improving the plan
3. Give an overall satisfaction score from 0-100
4. Determine if the plan needs further refinement (True if score < {threshold})
5. Recommend whether to continue with the same algorithm or try a different one

Format your response as Python code that creates a PlanRefinementFeedback object.
Start with "PlanRefinementFeedback(" and include all required fields.

The feedback should be specific enough that a plan refiner can use it to make targeted improvements.
"""
        description = description.replace("{constraints}", "{{constraints}}")
        description = description.replace("{threshold}", str(self.min_satisfaction_threshold))
        
        return Task(
            description=description,
            expected_output="PlanRefinementFeedback with detailed improvement guidance",
            agent=self.plan_evaluator_agent(),
            context=[
                self.identify_constraints_task(),
                self.evaluate_plans_task() if self.use_best_of_n else self.plan_tasks_and_agents_task()
            ],
            output_pydantic=PlanRefinementFeedback
        )
        
    @task
    def refine_plan_task(self) -> Task:
        """
        Refines a plan based on feedback.
        Returns an improved Plan object.
        """
        description = r"""
Given this plan:
{{plan}}

And this feedback:
{{feedback}}

Create an improved version of the plan that addresses the issues identified in the feedback.

Your response should match the following Pydantic models:

```python
class TaskDefinition(BaseModel):
    name: str
    purpose: str
    dependencies: List[str] = []
    complexity: str = "Medium"  # Low, Medium, High

class AgentDefinition(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str = ""

class Plan(BaseModel):
    name: str 
    content: str
    planned_tasks: List[TaskDefinition]
    required_agent_types: List[AgentDefinition]
```

Follow these steps:
1. Address each violated constraint identified in the feedback
2. Implement the improvement suggestions
3. Ensure your refined plan maintains the strengths of the original plan
4. Give the refined plan a name that indicates it's a refinement (e.g., "Refined Plan: [Original Name]")

Format your response as Python code that creates a Plan object.
Start with "Plan(" and include all required fields with your improvements.

Make your refinements specific and targeted to address the issues raised in the feedback.
"""
        return Task(
            description=description,
            expected_output="Refined Plan object addressing feedback",
            agent=self.plan_refiner_agent(),
            context=[],  # Context will be provided dynamically
            output_pydantic=Plan
        )

    @task
    def assemble_schema_task(self) -> Task:
        """
        Merges the conceptual plan + partial input_schema_json into a standard CrewAI schema.
        """
        # Double braces so .format won't interpret them. 
        description = r"""
We have a conceptual plan:
{{output}}

And also a partial input_schema_json from interpret_input_description_task.

Create a full CrewAI schema following this structure:

```python
class CrewConfig(BaseModel):
    crew: Dict[str, Any]
    agents: Any
    tasks: Any
    input_schema_json: Any
```

- Merge plan + input_schema_json
- Keep placeholders like {{{{title}}}} if they exist.

Format your response as Python code that creates a CrewConfig object.
Start with "CrewConfig(" and include all necessary fields.
"""
        return Task(
            description=description,
            expected_output="CrewConfig object with complete schema",
            agent=self.schema_converter(),
            context=[
                self.plan_tasks_and_agents_task(),
                self.interpret_input_description_task()
            ],
            output_pydantic=CrewConfig
        )

    @task
    def refine_and_output_final_config_task(self) -> Task:
        """
        Final step: ensures placeholders remain if relevant; cleans up extraneous text.
        """
        # Double braces around the snippet if you show example JSON.
        description = r"""
Given this draft config:
{{output}}

Your response should match the following Pydantic model:

```python
class CrewConfig(BaseModel):
    crew: Dict[str, Any]
    agents: Any
    tasks: Any
    input_schema_json: Any
```

**INSTRUCTIONS**:
1. Ensure "crew", "agents", "tasks", "input_schema_json" are present.
2. Each agent: name, role, goal, backstory. Keep placeholders {{{{title}}}} if relevant.
3. Each task: name, description, expected_output, agent, human_input, context_tasks.
   - Keep placeholders if they make sense. Remove truly extraneous placeholders only.

Format your response as Python code that creates a refined CrewConfig object.
Start with "CrewConfig(" and include all necessary fields.
"""
        return Task(
            description=description,
            expected_output="Refined CrewConfig object",
            agent=self.schema_converter(),
            context=[self.assemble_schema_task()],
            output_pydantic=CrewConfig
        )

    def run_plan_refinement_cycle(self, crew: Crew, initial_plan: Plan, constraints: ConstraintList) -> Plan:
        """
        Runs the iterative plan refinement cycle, a key component of PlanGEN.
        Takes an initial plan and refines it until it meets the satisfaction threshold or hits max iterations.
        """
        current_plan = initial_plan
        
        for iteration in range(self.max_refinement_iterations):
            # Run feedback task
            feedback_task = self.provide_plan_feedback_task()
            feedback_task.description = feedback_task.description.replace("{{output}}", str(current_plan))
            feedback_task.description = feedback_task.description.replace("{{constraints}}", str(constraints))
            
            feedback_result = crew.run_task(feedback_task)
            feedback: PlanRefinementFeedback = feedback_result.output
            
            # Check if refinement is needed
            if not feedback.needs_refinement:
                print(f"Plan meets satisfaction threshold ({feedback.satisfied_score}%). No further refinement needed.")
                return current_plan
                
            print(f"Plan refinement iteration {iteration+1}: satisfaction score {feedback.satisfied_score}%")
            
            # Change algorithm if recommended
            if feedback.recommended_algorithm != "same" and feedback.recommended_algorithm != "":
                print(f"Changing algorithm to {feedback.recommended_algorithm} based on feedback")
                # Logic to switch algorithms would go here
                # This is a placeholder - in a real implementation we would change the algorithm
            
            # Run refinement task
            refine_task = self.refine_plan_task()
            refine_task.description = refine_task.description.replace("{{plan}}", str(current_plan))
            refine_task.description = refine_task.description.replace("{{feedback}}", str(feedback))
            
            refine_result = crew.run_task(refine_task)
            current_plan = refine_result.output
            
        print(f"Reached maximum refinement iterations ({self.max_refinement_iterations}). Returning best plan.")
        return current_plan
    
    @crew
    def crew(self) -> Crew:
        """
        Final pipeline implementing the PlanGEN workflow:
        1. Gather user requirements
        2. Identify constraints
        3. Select algorithm
        4. Generate initial plan(s)
        5. Evaluate plan(s)
        6. Refine plans iteratively until satisfactory
        7. Convert final plan to CrewAI schema
        """
        # Core agents needed for all workflows
        agents = [
            self.planner_agent(),
            self.constraint_agent(),
            self.algorithm_selector_agent(),
            self.plan_evaluator_agent(),
            self.plan_refiner_agent(),
            self.schema_converter()
        ]
        
        # Core tasks needed for all workflows
        tasks = [
            self.gather_user_requirements_task(),
            self.identify_constraints_task(),
            self.select_algorithm_task(),
        ]
        
        # Select planning approach based on algorithm selection
        # For now, we're using a simplified approach that always uses 
        # best_of_n if enabled, but in a more sophisticated implementation
        # we would choose the algorithm based on the selection task result
        if self.use_best_of_n:
            tasks.extend([
                self.generate_alternative_plans_task(),
                self.evaluate_plans_task(),
            ])
        else:
            tasks.append(self.plan_tasks_and_agents_task())
            
        # Schema conversion tasks
        tasks.extend([
            self.interpret_input_description_task(),
            self.assemble_schema_task(),
            self.refine_and_output_final_config_task()
        ])
            
        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
    def kickoff_with_refinement(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override of the standard kickoff method to include the iterative refinement loop.
        This is the method that should be called from outside to run the full PlanGEN workflow.
        """
        # Run the initial crew workflow
        crew_instance = self.crew()
        initial_result = crew_instance.kickoff(inputs=inputs)
        
        # After the initial run, extract the plan and constraints
        best_plan = None
        constraints = None
        
        # Here we would extract the best plan and constraints from the initial result
        # This is a simplified version - in a real implementation we would extract this data
        # from the actual result returned by the crew
        
        # If plan needs refinement based on evaluation, run the refinement cycle
        if self.use_best_of_n and best_plan and constraints:
            refined_plan = self.run_plan_refinement_cycle(crew_instance, best_plan, constraints)
            
            # Update the result with the refined plan
            # Again, this is simplified - we would need to integrate this with the actual result
            
        return initial_result