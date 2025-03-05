"""
Agent definitions for the Implementation Crew.
"""

from crewai import Agent
from typing import List, Any

def create_agents(llm: Any) -> List[Agent]:
    """
    Create and return the agents for the Implementation Crew.
    
    Args:
        llm: Language model to use for the agents
        
    Returns:
        List of Agent objects
    """
    # Agent Engineer agent
    agent_engineer = Agent(
        role="Agent Engineer",
        goal="Design agent capabilities and characteristics",
        backstory="""You are an expert in designing AI agents with effective capabilities,
        especially for solving problems in the {domain} domain. You know how to define 
        clear roles, goals, and backstories that make agents successful at their tasks 
        and ensure they complement each other in a crew. You excel at creating agents 
        that can understand {problem_context} challenges and work with the expected 
        {input_context} inputs to produce the required {output_context} outputs.""",
        verbose=True,
        llm=llm
    )
    
    # Task Designer agent
    task_designer = Agent(
        role="Task Designer",
        goal="Create specific and well-defined task specifications",
        backstory="""You are a specialist in task design who knows how to break down
        complex processes into actionable, clearly-defined tasks. You excel at
        specifying inputs, outputs, and success criteria for tasks that agents
        can execute effectively. You have expertise designing task workflows for
        {domain} problems and understand what tasks are needed to transform
        {input_context} into {output_context} while working within {problem_context}.""",
        verbose=True,
        llm=llm
    )
    
    # Workflow Specialist agent
    workflow_specialist = Agent(
        role="Workflow Specialist",
        goal="Optimize task dependencies and execution flow",
        backstory="""You are an expert in workflow optimization who understands how
        to structure task dependencies for maximum efficiency. You can identify which
        tasks can run in parallel, which need to be sequential, and how to minimize
        bottlenecks in complex workflows.""",
        verbose=True,
        llm=llm
    )
    
    # Integration Expert agent
    integration_expert = Agent(
        role="Integration Expert",
        goal="Ensure system coherence and smooth component interaction",
        backstory="""You are a systems integrator who specializes in making sure all
        parts of a complex system work smoothly together. You can identify potential
        interface issues, ensure consistent data flow between components, and validate
        that the system works as a cohesive whole.""",
        verbose=True,
        llm=llm
    )
    
    return [agent_engineer, task_designer, workflow_specialist, integration_expert]