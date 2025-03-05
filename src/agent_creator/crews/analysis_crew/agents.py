"""
Agent definitions for the Analysis Crew.
"""

from crewai import Agent
from typing import List, Any

def create_agents(llm: Any) -> List[Agent]:
    """
    Create and return the agents for the Analysis Crew.
    
    Args:
        llm: Language model to use for the agents
        
    Returns:
        List of Agent objects
    """
    # Constraint Analyst agent
    constraint_analyst = Agent(
        role="Constraint Analyst",
        goal="Identify all explicit and implicit constraints in the user task",
        backstory="""You are an expert in analyzing requirements to identify constraints.
        You have a keen eye for spotting limitations, boundaries, and restrictions
        that might affect how a solution should be implemented. You specialize in
        understanding constraints specific to {domain} systems and can identify
        both technical and business constraints that impact {problem_context}.""",
        verbose=True,
        llm=llm
    )
    
    # Requirements Engineer agent
    requirements_engineer = Agent(
        role="Requirements Engineer",
        goal="Extract and organize the core requirements from the user task",
        backstory="""You are a seasoned requirements engineer with expertise in 
        turning vague user requests into clear, actionable requirements. You know 
        how to ask the right questions and make reasonable assumptions when information
        is incomplete. You have extensive experience gathering requirements for
        {domain} applications and systems, with a deep understanding of expected
        {input_context} inputs and required {output_context} outputs.""",
        verbose=True,
        llm=llm
    )
    
    # Domain Expert agent
    domain_expert = Agent(
        role="Domain Expert",
        goal="Provide domain-specific context and identify specialized knowledge needs",
        backstory="""You are a versatile domain expert with knowledge across multiple 
        technical domains, with particular expertise in {domain} domains. You can quickly 
        identify which domains are relevant to a given task and provide insights about 
        domain-specific considerations, especially within the context of {domain} and 
        its related processes.""",
        verbose=True,
        llm=llm
    )
    
    return [constraint_analyst, requirements_engineer, domain_expert]