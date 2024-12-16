# tasks.py
from crewai import Task
from .agents import get_planner_agent, get_schema_converter_agent
from crewai.project import task

def gather_user_requirements_task(planner_agent) -> Task:
    description = """
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

Summarize these into JSON:
{
  "description": "...",
  "inputDescription": "...",
  "outputDescription": "...",
  "tools": [...],
  "process": "...",
  "planning": ...,
  "knowledge": ...,
  "humanInputTasks": ...,
  "memory": ...,
  "cache": ...,
  "managerLLM": "..."
}
    """
    return Task(
        description=description,
        expected_output="A JSON object with user's requirements.",
        agent=planner_agent
    )

def plan_tasks_and_agents_task(planner_agent, gather_task) -> Task:
    description = """
Given these user requirements:
{{output}}

(Example in a retail e-commerce context, like Walmart's product catalog)
If user requirements involve "Enhancing product data quality for the Walmart e-commerce catalog":
- Extract product attributes from vendor feeds
- Standardize and enrich product titles and descriptions
- Enhance and validate product images
- Map product attributes to internal Walmart taxonomy
- Validate data consistency and completeness
- Perform A/B testing to measure improvements

Required agent types might be:
- Data Curator (for extracting and structuring product attributes)
- Content Specialist (for refining titles and descriptions)
- Image Analyst (for improving and validating product images)
- Taxonomy Specialist (for mapping attributes)
- QA Engineer (for checking consistency/completeness)
- Data Analyst (for conducting and evaluating A/B tests)

Break them down into conceptual tasks and define the required agent types.

Return JSON with:
{
  "plannedTasks": [
    {
      "name": "TaskName",
      "purpose": "Short description",
      "dependencies": [],
      "complexity": "Low/Medium/High"
    }
  ],
  "requiredAgentTypes": [
    {
      "role": "AgentRoleName",
      "goal": "What this agent aims to achieve",
      "backstory": "Short background"
    }
  ]
}
"""
    return Task(
        description=description,
        expected_output="Conceptual plan in JSON.",
        agent=planner_agent,
        context=[gather_task]
    )

def assemble_schema_task(schema_converter_agent, planning_task, CrewConfig):
    description = """
From this conceptual plan:
{{output}}

Produce a CrewAI schema as per the expected format. No code blocks, just return JSON.
{
  "crew": { "name": "ProjectCrew", "process": "...", "planning": ... },
  "agents": [],
  "tasks": [],
  "input_schema_json": {}
}
"""
    return Task(
        description=description,
        expected_output="CrewAI-compliant JSON configuration.",
        agent=schema_converter_agent,
        context=[planning_task],
        output_pydantic=CrewConfig
    )

def refine_and_output_final_config_task(schema_converter_agent, assemble_task, CrewConfig):
    description = """
Given this draft config:
{{output}}

Refine and ensure perfect CrewAI schema compliance:
- Ensure crew, agents, tasks, input_schema_json present.
- Agents have role, goal, backstory.
- Tasks are well-defined.
Return final JSON only.
"""
    return Task(
        description=description,
        expected_output="Refined final JSON configuration.",
        agent=schema_converter_agent,
        context=[assemble_task],
        output_pydantic=CrewConfig
    )
