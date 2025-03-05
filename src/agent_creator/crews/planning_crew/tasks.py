"""
Task definitions for the Planning Crew.
"""

from crewai import Task, Agent
from typing import List, Dict

def create_tasks(agents: List[Agent]) -> List[Task]:
    """
    Create and return the tasks for the Planning Crew.
    
    Args:
        agents: List of agents to assign tasks to
        
    Returns:
        List of Task objects
    """
    # Extract agents by role
    planning_manager = next(a for a in agents if a.role == "Planning Manager")
    best_of_n_generator = next(a for a in agents if a.role == "Best-of-N Generator")
    tree_of_thoughts_agent = next(a for a in agents if a.role == "Tree-of-Thoughts Explorer")
    rebase_agent = next(a for a in agents if a.role == "REBASE Specialist")
    verification_agent = next(a for a in agents if a.role == "Verification Agent")
    
    # Set context for agent roles and backstories 
    # (Note: CrewAI interpolation is already handled automatically with {variable} syntax)
    # We don't need to manually replace anything here
    
    # Task 1: Select Algorithm
    select_algorithm = Task(
        description="""
        Based on the user task and analysis, select the most appropriate planning algorithm.
        
        User Task: {user_task}
        Domain: {domain}
        Problem Context: {problem_context}
        Input Context: {input_context}
        Output Context: {output_context}
        Process Areas: {process_areas}
        Constraints: {constraints}
        Analysis Results: {analysis_result}
        
        Available Planning Algorithms:
        1. Best-of-N Planning: Generate multiple plans and select the best one based on evaluation criteria.
        2. Tree of Thoughts (ToT): Explore multiple reasoning paths and select the most promising one.
        3. REBASE: Recursively break down the problem, evaluate solutions, and synthesize the final approach.
        
        Your job is to:
        1. Analyze the task complexity, domain, and constraints
        2. Consider the specific needs of {domain} and {problem_context}
        3. Select the most appropriate algorithm for this specific task
        4. Provide clear justification for your selection
        
        Format your response as a JSON object with these fields:
        - selected_algorithm: Name of the selected algorithm (one of the three listed above)
        - algorithm_justification: Detailed explanation of why this algorithm is most appropriate
        """,
        agent=planning_manager,
        expected_output="JSON with algorithm selection and justification"
    )
    
    # Task 2a: Generate Best-of-N Plans
    generate_best_of_n_plans = Task(
        description="""
        Generate multiple diverse candidate plans using the Best-of-N approach.
        
        User Task: {{user_task}}
        Analysis Results: {{analysis_result}}
        
        Your job is to:
        1. Generate 3-5 diverse candidate approaches to solving the problem
        2. Ensure each plan meets the requirements and constraints
        3. Make each plan meaningfully different in approach
        4. Structure each plan with agents and tasks
        
        Format your response as a JSON object with:
        - candidate_plans: Array of plan objects, each with:
          - plan_name: A descriptive name
          - approach: Detailed description of the approach
          - agents: Array of agent definitions (with name, role, goal, backstory)
          - tasks: Array of task definitions (with name, description, assigned_to, dependencies)
        """,
        agent=best_of_n_generator,
        expected_output="JSON with multiple candidate plans",
        context=[select_algorithm],
        human_input=False  # This ensures the task is assigned only when selected
    )
    
    # Task 2b: Generate Tree-of-Thoughts Plan
    generate_tot_plan = Task(
        description="""
        Generate a plan using the Tree-of-Thoughts approach.
        
        User Task: {{user_task}}
        Analysis Results: {{analysis_result}}
        
        Your job is to:
        1. Break down the problem into key decision points
        2. Explore 2-3 alternative paths at each decision point
        3. Evaluate each path and select the most promising one
        4. Create a final plan based on the optimal path
        
        Format your response as a JSON object with:
        - reasoning_tree: Description of the decision tree and reasoning
        - selected_path: The optimal path through the decision tree
        - final_plan: A plan object with:
          - agents: Array of agent definitions (with name, role, goal, backstory)
          - tasks: Array of task definitions (with name, description, assigned_to, dependencies)
        """,
        agent=tree_of_thoughts_agent,
        expected_output="JSON with ToT plan",
        context=[select_algorithm],
        human_input=False  # This ensures the task is assigned only when selected
    )
    
    # Task 2c: Generate REBASE Plan
    generate_rebase_plan = Task(
        description="""
        Generate a plan using the REBASE approach.
        
        User Task: {{user_task}}
        Analysis Results: {{analysis_result}}
        
        Your job is to:
        1. Recursively break down the problem into component subproblems
        2. Develop solutions for each subproblem
        3. Synthesize the component solutions into a coherent whole
        
        Format your response as a JSON object with:
        - component_breakdown: Array of subproblems and their solutions
        - synthesis: Explanation of how the components are integrated
        - final_plan: A plan object with:
          - agents: Array of agent definitions (with name, role, goal, backstory)
          - tasks: Array of task definitions (with name, description, assigned_to, dependencies)
        """,
        agent=rebase_agent,
        expected_output="JSON with REBASE plan",
        context=[select_algorithm],
        human_input=False  # This ensures the task is assigned only when selected
    )
    
    # Task 3: Verify Plans
    verify_plans = Task(
        description="""
        Evaluate the generated plans and provide quality assessment.
        
        User Task: {{user_task}}
        Analysis Results: {{analysis_result}}
        Selected Algorithm: {{select_algorithm.output}}
        
        # If Best-of-N was selected:
        Candidate Plans: {{generate_best_of_n_plans.output}}
        
        # If Tree-of-Thoughts was selected:
        ToT Plan: {{generate_tot_plan.output}}
        
        # If REBASE was selected:
        REBASE Plan: {{generate_rebase_plan.output}}
        
        Your job is to:
        1. Verify each plan against the requirements and constraints
        2. Assess completeness, efficiency, feasibility, and alignment
        3. Score each plan on a scale of 1-10
        4. Provide specific feedback on strengths and weaknesses
        
        Format your response as a JSON object with:
        - verification_results: Array of verification objects, each with:
          - plan_name: Name of the plan being verified
          - completeness_score: Rating from 1-10
          - efficiency_score: Rating from 1-10
          - feasibility_score: Rating from 1-10
          - alignment_score: Rating from 1-10
          - overall_score: Average of all scores
          - strengths: Array of strengths
          - weaknesses: Array of weaknesses
        - best_plan: Name of the highest-scoring plan
        """,
        agent=verification_agent,
        expected_output="JSON with verification results",
        context=[select_algorithm, generate_best_of_n_plans, generate_tot_plan, generate_rebase_plan]
    )
    
    # Task 4: Finalize Plan
    finalize_plan = Task(
        description="""
        Select and finalize the best plan based on verification results.
        
        User Task: {{user_task}}
        Analysis Results: {{analysis_result}}
        Selected Algorithm: {{select_algorithm.output}}
        Verification Results: {{verify_plans.output}}
        
        # If Best-of-N was selected:
        Candidate Plans: {{generate_best_of_n_plans.output}}
        
        # If Tree-of-Thoughts was selected:
        ToT Plan: {{generate_tot_plan.output}}
        
        # If REBASE was selected:
        REBASE Plan: {{generate_rebase_plan.output}}
        
        Your job is to:
        1. Select the best plan based on verification results
        2. Make any final improvements or adjustments based on feedback
        3. Format the final plan with complete agent and task definitions
        
        Format your response as a JSON object with:
        - selected_algorithm: Name of the algorithm used
        - algorithm_justification: Why this algorithm was appropriate
        - candidate_plans: Summary of all plans considered
        - selected_plan: The final selected plan with:
          - agents: Array of agent definitions (with name, role, goal, backstory)
          - tasks: Array of task definitions (with name, description, assigned_to, dependencies)
          - workflow: Object with sequence and parallel_tasks information
        - verification_score: Overall quality score from verification
        """,
        agent=planning_manager,
        expected_output="JSON with final selected plan",
        context=[select_algorithm, generate_best_of_n_plans, generate_tot_plan, generate_rebase_plan, verify_plans]
    )
    
    return [
        select_algorithm,
        generate_best_of_n_plans,
        generate_tot_plan,
        generate_rebase_plan,
        verify_plans,
        finalize_plan
    ]