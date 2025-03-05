"""
Task definitions for the Analysis Crew.
"""

from crewai import Task, Agent
from typing import List, Dict

def create_tasks(agents: List[Agent]) -> List[Task]:
    """
    Create and return the tasks for the Analysis Crew.
    
    Args:
        agents: List of agents to assign tasks to
        
    Returns:
        List of Task objects
    """
    # Extract agents by role
    constraint_analyst = next(a for a in agents if a.role == "Constraint Analyst")
    requirements_engineer = next(a for a in agents if a.role == "Requirements Engineer")
    domain_expert = next(a for a in agents if a.role == "Domain Expert")
    
    # Task 1: Extract Requirements
    extract_requirements = Task(
        description="""
        Analyze the user task and extract clear, actionable requirements.
        
        User Task: {{user_task}}
        
        Your job is to:
        1. Identify the core requirements that must be fulfilled
        2. Organize them into functional and non-functional requirements
        3. Fill in any gaps with reasonable assumptions
        4. Create a structured list of requirements
        
        Format your response as a JSON object with "requirements" as a list of strings.
        """,
        agent=requirements_engineer,
        expected_output="JSON with requirements list"
    )
    
    # Task 2: Identify Constraints
    identify_constraints = Task(
        description="""
        Analyze the user task and identify all constraints that will impact the solution.
        
        User Task: {{user_task}}
        Requirements: {{extract_requirements.output}}
        
        Your job is to:
        1. Identify explicit constraints directly mentioned in the task
        2. Infer implicit constraints based on the context
        3. Consider technological, resource, time, or other limitations
        4. Create a structured list of constraints
        
        Format your response as a JSON object with "constraints" as a list of strings.
        """,
        agent=constraint_analyst,
        expected_output="JSON with constraints list",
        context=[extract_requirements]
    )
    
    # Task 3: Assess Domain Knowledge
    assess_domain = Task(
        description="""
        Analyze the user task and determine the domain knowledge required.
        
        User Task: {{user_task}}
        Requirements: {{extract_requirements.output}}
        Constraints: {{identify_constraints.output}}
        
        Your job is to:
        1. Identify the technical domains relevant to this task
        2. Assess the complexity level on a scale of 1-10
        3. Determine time sensitivity of the task
        4. Define clear success criteria
        5. Recommend whether a sequential or hierarchical process would be better for this task
        
        Format your response as a JSON object with these fields:
        - domain_knowledge: List of relevant domains
        - complexity: Numeric rating (1-10)
        - time_sensitivity: Object with is_critical (boolean) and reasoning (string)
        - success_criteria: List of measurable outcomes
        - recommended_process_type: Either "sequential" or "hierarchical" with explanation
        """,
        agent=domain_expert,
        expected_output="JSON with domain analysis",
        context=[extract_requirements, identify_constraints]
    )
    
    # Task 4: Synthesize Analysis
    synthesize_analysis = Task(
        description="""
        Synthesize all the analysis into a comprehensive report.
        
        User Task: {{user_task}}
        Requirements: {{extract_requirements.output}}
        Constraints: {{identify_constraints.output}}
        Domain Analysis: {{assess_domain.output}}
        
        Your job is to:
        1. Compile all the information into a single, coherent analysis
        2. Ensure there are no contradictions or redundancies
        3. Format the output as a structured JSON document
        
        Format your response as a JSON object with these fields:
        - constraints: List from constraints analysis
        - requirements: List from requirements analysis
        - complexity: From domain analysis
        - domain_knowledge: List from domain analysis
        - time_sensitivity: Object from domain analysis
        - success_criteria: List from domain analysis
        - recommended_process_type: From domain analysis
        """,
        agent=requirements_engineer,
        expected_output="JSON with complete analysis",
        context=[extract_requirements, identify_constraints, assess_domain]
    )
    
    return [extract_requirements, identify_constraints, assess_domain, synthesize_analysis]