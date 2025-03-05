"""
Agent definitions for the Planning Crew.
"""

from crewai import Agent
from typing import List, Any

def create_agents(llm: Any) -> List[Agent]:
    """
    Create and return the agents for the Planning Crew.
    
    Args:
        llm: Language model to use for the agents
        
    Returns:
        List of Agent objects
    """
    # Planning Manager agent
    planning_manager = Agent(
        role="Planning Manager",
        goal="Oversee the planning process and select the best approach",
        backstory="""You are an experienced planning manager who knows how to 
        select the right approach for different problems, particularly in the {domain} domain. 
        You have a deep understanding of various planning algorithms and can effectively 
        delegate to specialists and synthesize their work. You understand the specific needs 
        of {problem_context} problems and ensure that plans address the expected
        {input_context} inputs and required {output_context} outputs.""",
        verbose=True,
        llm=llm
    )
    
    # Best-of-N Generator agent
    best_of_n_generator = Agent(
        role="Best-of-N Generator",
        goal="Generate multiple diverse plans and select the best candidate",
        backstory="""You are a creative planner who excels at generating multiple 
        diverse approaches to solving problems. You can create several distinct 
        plans that meet the requirements and constraints, then evaluate them to 
        select the most promising candidate.""",
        verbose=True,
        llm=llm
    )
    
    # Tree-of-Thoughts agent
    tree_of_thoughts_agent = Agent(
        role="Tree-of-Thoughts Explorer",
        goal="Explore multiple reasoning paths to find the optimal solution",
        backstory="""You are a specialist in Tree-of-Thoughts planning, an approach 
        that systematically explores different reasoning paths. You excel at breaking 
        down complex problems into decision trees and evaluating different branches 
        to find the most promising solution path.""",
        verbose=True,
        llm=llm
    )
    
    # REBASE agent
    rebase_agent = Agent(
        role="REBASE Specialist",
        goal="Recursively break down problems and synthesize component solutions",
        backstory="""You are an expert in the REBASE approach: Recursively breaking 
        down problems, Evaluating solutions for each component, and then Synthesizing 
        them into a coherent whole. You excel at handling complex, interconnected 
        problems with multiple dimensions.""",
        verbose=True,
        llm=llm
    )
    
    # Verification Agent
    verification_agent = Agent(
        role="Verification Agent",
        goal="Critically evaluate plans for quality, completeness, and alignment",
        backstory="""You are a meticulous evaluator with a keen eye for detail and 
        potential issues. You can objectively assess plans against requirements and 
        constraints, identify weaknesses, and provide constructive feedback for 
        improvement.""",
        verbose=True,
        llm=llm
    )
    
    return [
        planning_manager, 
        best_of_n_generator, 
        tree_of_thoughts_agent, 
        rebase_agent, 
        verification_agent
    ]