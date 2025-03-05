"""
Agent definitions for the Analysis Crew.
"""

from crewai import Agent
from langchain.chat_models import ChatOpenAI
from typing import List

def create_agents(llm: ChatOpenAI) -> List[Agent]:
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
        that might affect how a solution should be implemented.""",
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
        is incomplete.""",
        verbose=True,
        llm=llm
    )
    
    # Domain Expert agent
    domain_expert = Agent(
        role="Domain Expert",
        goal="Provide domain-specific context and identify specialized knowledge needs",
        backstory="""You are a versatile domain expert with knowledge across multiple 
        technical domains. You can quickly identify which domains are relevant to a 
        given task and provide insights about domain-specific considerations.""",
        verbose=True,
        llm=llm
    )
    
    return [constraint_analyst, requirements_engineer, domain_expert]