# agents.py
from crewai import Agent, LLM

def get_planner_agent(llm: LLM) -> Agent:
    """
    Returns the planner agent configured with the given LLM.
    """
    return Agent(
        role="Planning Architect",
        goal="Transform high-level user requirements into a conceptual plan of tasks and needed specialists.",
        backstory="Expert at requirements analysis and task structuring.",
        llm=llm,
        memory=True,
        verbose=False,
        allow_delegation=False,
        max_iter=5,
        respect_context_window=True,
        use_system_prompt=True,
        cache=False,
        max_retry_limit=2,
    )

def get_schema_converter_agent(llm: LLM) -> Agent:
    """
    Returns the schema converter agent configured with the given LLM.
    """
    return Agent(
        role="Schema Converter",
        goal="Convert conceptual tasks and agents into a CrewAI-compliant schema.",
        backstory="Skilled in schema creation and ensuring compliance with defined formats.",
        llm=llm,
        memory=True,
        verbose=False,
        allow_delegation=False,
        max_iter=5,
        respect_context_window=True,
        use_system_prompt=True,
        cache=False,
        max_retry_limit=2,
    )
