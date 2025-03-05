"""
Task definitions for the Evaluation Crew.
"""

from crewai import Task, Agent
from typing import List, Dict

def create_tasks(agents: List[Agent]) -> List[Task]:
    """
    Create and return the tasks for the Evaluation Crew.
    
    Args:
        agents: List of agents to assign tasks to
        
    Returns:
        List of Task objects
    """
    # Extract agents by role
    qa_manager = next(a for a in agents if a.role == "QA Manager")
    completeness_tester = next(a for a in agents if a.role == "Completeness Tester")
    efficiency_analyst = next(a for a in agents if a.role == "Efficiency Analyst")
    alignment_validator = next(a for a in agents if a.role == "Alignment Validator")
    
    # Task 1: Define Evaluation Criteria
    define_evaluation_criteria = Task(
        description="""
        Define comprehensive evaluation criteria for the implementation.
        
        User Task: {user_task}
        Domain: {domain}
        Problem Context: {problem_context}
        Input Context: {input_context}
        Output Context: {output_context}
        Process Areas: {process_areas}
        Constraints: {constraints}
        Analysis Results: {analysis_result}
        Planning Results: {planning_result}
        Implementation Results: {implementation_result}
        
        Your job is to:
        1. Define specific evaluation criteria for this implementation
        2. Prioritize criteria based on the user task and requirements
        3. Establish scoring metrics for each criterion
        4. Create a clear evaluation framework
        
        Format your response matching the expected structure:
        - criteria: Array of evaluation criteria, each with:
          - name: Name of the criterion
          - description: What this criterion evaluates
          - weight: Relative importance (1-10)
          - evaluation_method: How to evaluate this criterion
        """,
        agent=qa_manager,
        expected_output="Evaluation criteria framework"
    )
    
    # Task 2: Test Completeness
    test_completeness = Task(
        description="""
        Evaluate the implementation for completeness and coverage.
        
        User Task: {{user_task}}
        Analysis Results: {{analysis_result}}
        Planning Results: {{planning_result}}
        Implementation Results: {{implementation_result}}
        Evaluation Criteria: {{define_evaluation_criteria.output}}
        
        Your job is to:
        1. Check if all requirements are addressed
        2. Identify any missing elements or gaps
        3. Assess whether edge cases are handled
        4. Evaluate overall coverage of the solution
        
        Format your response matching the expected structure:
        - completeness_score: Numeric score (1-10)
        - missing_elements: Array of missing components or considerations
        - coverage_assessment: Detailed assessment of requirement coverage
        - recommendations: Specific suggestions to improve completeness
        """,
        agent=completeness_tester,
        expected_output="Completeness evaluation",
        context=[define_evaluation_criteria]
    )
    
    # Task 3: Analyze Efficiency
    analyze_efficiency = Task(
        description="""
        Evaluate the implementation for efficiency and resource optimization.
        
        User Task: {{user_task}}
        Analysis Results: {{analysis_result}}
        Planning Results: {{planning_result}}
        Implementation Results: {{implementation_result}}
        Evaluation Criteria: {{define_evaluation_criteria.output}}
        
        Your job is to:
        1. Analyze workflow efficiency and task dependencies
        2. Identify any redundancies or duplicated efforts
        3. Assess resource allocation and utilization
        4. Evaluate whether the selected process type is optimal
        
        Format your response matching the expected structure:
        - efficiency_score: Numeric score (1-10)
        - redundancies: Array of identified redundancies or duplications
        - bottlenecks: Array of potential bottlenecks
        - process_assessment: Evaluation of the selected process type
        - optimization_recommendations: Specific suggestions to improve efficiency
        """,
        agent=efficiency_analyst,
        expected_output="Efficiency analysis",
        context=[define_evaluation_criteria]
    )
    
    # Task 4: Validate Alignment
    validate_alignment = Task(
        description="""
        Evaluate how well the implementation aligns with user needs and requirements.
        
        User Task: {{user_task}}
        Analysis Results: {{analysis_result}}
        Planning Results: {{planning_result}}
        Implementation Results: {{implementation_result}}
        Evaluation Criteria: {{define_evaluation_criteria.output}}
        
        Your job is to:
        1. Assess how well the implementation addresses the core user task
        2. Validate that the solution meets all requirements
        3. Evaluate whether the implemented agents and tasks are appropriate
        4. Determine if the solution will produce the expected outcome
        
        Format your response matching the expected structure:
        - alignment_score: Numeric score (1-10)
        - requirement_satisfaction: Assessment of how well requirements are satisfied
        - appropriate_components: Evaluation of agent and task appropriateness
        - outcome_likelihood: Assessment of likelihood to achieve expected outcome
        - alignment_recommendations: Specific suggestions to improve alignment
        """,
        agent=alignment_validator,
        expected_output="Alignment validation",
        context=[define_evaluation_criteria]
    )
    
    # Task 5: Synthesize Evaluation
    synthesize_evaluation = Task(
        description="""
        Synthesize all evaluation results into a comprehensive assessment.
        
        User Task: {{user_task}}
        Analysis Results: {{analysis_result}}
        Planning Results: {{planning_result}}
        Implementation Results: {{implementation_result}}
        Completeness Evaluation: {{test_completeness.output}}
        Efficiency Analysis: {{analyze_efficiency.output}}
        Alignment Validation: {{validate_alignment.output}}
        
        Your job is to:
        1. Integrate findings from all evaluations
        2. Identify key strengths and weaknesses
        3. Calculate an overall score
        4. Determine which area needs most improvement (analysis, planning, implementation, or none)
        5. Provide actionable recommendations
        
        Format your response as an EvaluationOutput model with:
        - strengths: List of strongest aspects of the implementation
        - weaknesses: List of areas needing improvement
        - missing_elements: List of critical missing elements
        - recommendations: List of specific improvement suggestions
        - overall_score: Overall quality rating (1-10)
        - improvement_area: Which area needs most refinement ("analysis", "planning", "implementation", or "none")
        """,
        agent=qa_manager,
        expected_output="EvaluationOutput with comprehensive assessment",
        context=[test_completeness, analyze_efficiency, validate_alignment]
    )
    
    return [
        define_evaluation_criteria,
        test_completeness,
        analyze_efficiency,
        validate_alignment,
        synthesize_evaluation
    ]