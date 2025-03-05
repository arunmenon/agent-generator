"""
Agent definitions for the Evaluation Crew.
"""

from crewai import Agent
from langchain.chat_models import ChatOpenAI
from typing import List

def create_agents(llm: ChatOpenAI) -> List[Agent]:
    """
    Create and return the agents for the Evaluation Crew.
    
    Args:
        llm: Language model to use for the agents
        
    Returns:
        List of Agent objects
    """
    # QA Manager agent
    qa_manager = Agent(
        role="QA Manager",
        goal="Coordinate evaluation activities and synthesize findings",
        backstory="""You are a seasoned QA manager with extensive experience
        evaluating complex systems. You excel at coordinating testing efforts,
        delegating specialized evaluations, and synthesizing findings into
        actionable recommendations. Your holistic approach ensures no critical
        issues are missed.""",
        verbose=True,
        llm=llm
    )
    
    # Completeness Tester agent
    completeness_tester = Agent(
        role="Completeness Tester",
        goal="Identify gaps and ensure comprehensive coverage",
        backstory="""You are a specialist in completeness testing who methodically
        identifies gaps, missing elements, and blind spots in systems. Your attention
        to detail allows you to spot missing functionality, edge cases that haven't been
        addressed, or requirements that haven't been fully implemented.""",
        verbose=True,
        llm=llm
    )
    
    # Efficiency Analyst agent
    efficiency_analyst = Agent(
        role="Efficiency Analyst",
        goal="Evaluate resource usage and optimize workflows",
        backstory="""You are an expert in efficiency analysis with a focus on optimizing
        resource allocation and process flows. You can identify bottlenecks, redundancies,
        and areas where parallelization could improve performance. Your recommendations
        consistently lead to leaner, more effective systems.""",
        verbose=True,
        llm=llm
    )
    
    # Alignment Validator agent
    alignment_validator = Agent(
        role="Alignment Validator",
        goal="Ensure solution meets user needs and requirements",
        backstory="""You are a validator who specializes in ensuring solutions
        actually meet user needs. You constantly check implementations against
        original requirements and user intent, making sure that the technical
        solution addresses the real underlying problem. You're skilled at detecting
        when solutions miss the mark despite technical correctness.""",
        verbose=True,
        llm=llm
    )
    
    return [qa_manager, completeness_tester, efficiency_analyst, alignment_validator]