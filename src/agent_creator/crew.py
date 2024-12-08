# src/my_project/agent_creator/crew.py
from typing import Any, Dict
from pydantic import BaseModel
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, task, crew, before_kickoff
from crewai_tools import SerperDevTool # example tool

class CrewConfig(BaseModel):
    crew: Dict[str, Any]
    agents: Any
    tasks: Any
    input_schema_json: Any

class MetaCrew(CrewBase):
    def __init__(self, llm_model="gpt-4"):
        self.llm_model = llm_model
        self.inputs: Dict[str, Any] = {}

    @before_kickoff
    def capture_inputs(self, inputs: Dict[str, Any]):
        # Store the user inputs for reference in tasks if needed
        self.inputs = inputs
        return inputs

    @agent
    def requirements_architect_agent(self) -> Agent:
        # No major logic change required
        return Agent(
            role="Requirements Architect",
            goal="Analyze user requirements and produce an initial crew configuration blueprint",
            backstory="An expert in understanding user needs and structuring them into a workable plan",
            llm=self.llm_model,
            memory=True,
            verbose=False,
            allow_delegation=False,
            max_iter=5,
            respect_context_window=True,
            use_system_prompt=True,
            cache=False,
            max_retry_limit=2,
        )

    @agent
    def configuration_refiner_agent(self) -> Agent:
        # No major logic change required
        return Agent(
            role="Configuration Refiner",
            goal="Refine the initial configuration into a fully detailed, validated crew setup",
            backstory="Skilled in polishing and verifying all details of the planned workflow",
            llm=self.llm_model,
            memory=True,
            verbose=False,
            allow_delegation=False,
            max_iter=5,
            respect_context_window=True,
            use_system_prompt=True,
            cache=False,
            max_retry_limit=2,
        )

    @task
    def gather_user_requirements_task(self) -> Task:
        # This will produce a JSON exactly matching user inputs
        prompt = """
You are the Requirements Architect Agent. 
The user provided some requirements for a crew configuration. They are:
- user_description: {user_description}
- user_input_description: {user_input_description}
- user_output_description: {user_output_description}
- user_tools: {user_tools}
- user_process: {user_process}
- user_planning: {user_planning}
- user_knowledge: {user_knowledge}
- user_human_input_tasks: {user_human_input_tasks}
- user_memory: {user_memory}
- user_cache: {user_cache}
- user_manager_llm: {user_manager_llm}

Return a JSON object that contains all these fields exactly, keyed by their names.
"""
        return Task(
            description="Collect and summarize the user's requirements into a structured JSON.",
            expected_output="JSON object with all user requirements.",
            agent=self.requirements_architect_agent(),
            prompt_template=prompt
        )

    @task
    def draft_initial_config_task(self) -> Task:
        # Incorporate user inputs into the config
        # Make sure the crew section includes user_process, user_planning, user_manager_llm, etc.
        # Make sure input_schema_json reflects user_input_description and user_output_description
        prompt = """
You are the Requirements Architect Agent. The user requirements {{requirements_json}} have been provided.

Construct a draft configuration that includes:
- A `crew` object with:
  - `name`: a crew name derived from user_description
  - `process`: use user_process
  - if user_planning=True, add `"planning": true` and optionally `"planning_llm": "gpt-4"`
  - if user_process='hierarchical' and user_manager_llm is not null, add `"manager_llm": user_manager_llm`
  - Include `user_memory`, `user_cache`, and `user_knowledge` as boolean fields in the `crew` object.
  - If `user_knowledge=True`, note that we might attach knowledge sources later (just mark it as an attribute).
- `agents`: at least one agent that fits user_description (you can create minimal placeholders)
- `tasks`: at least one task showing input and output usage
- `input_schema_json`: must reflect `user_input_description` and `user_output_description`
  For example, `input_schema_json` might contain `{"input_format": user_input_description, "output_format": user_output_description}`

Also, if user_tools is a list, reflect that these tools are going to be available to the agents.

`user_human_input_tasks`: If True, ensure at least one task requires human input (set `human_input: true` for that task).

Return the entire configuration as a well-structured JSON:
{
  "crew": {...},
  "agents": [...],
  "tasks": [...],
  "input_schema_json": {...}
}
"""
        return Task(
            description="Draft an initial crew configuration from user requirements.",
            expected_output="Draft JSON configuration",
            agent=self.requirements_architect_agent(),
            context=[self.gather_user_requirements_task()],
            prompt_template=prompt
        )

    @task
    def refine_config_task(self) -> Task:
        # Validate and ensure all user-driven properties are present
        prompt = """
You are the Configuration Refiner Agent. Given this draft config {{draft_config}}, validate and refine it:
- Ensure crew_name, process, planning, manager_llm, user_memory, user_cache, user_knowledge, user_human_input_tasks are correct and present in the `crew` object.
- Validate the input_schema_json matches user_input_description and user_output_description from the user requirements.
- Ensure all user tools are included if provided.
- If something is missing or inconsistent, fix it.
- Return the final refined JSON configuration.
"""
        return Task(
            description="Refine and validate the draft configuration into a final configuration.",
            expected_output="Final refined JSON configuration",
            agent=self.configuration_refiner_agent(),
            context=[self.draft_initial_config_task()],
            prompt_template=prompt,
            output_pydantic=CrewConfig
        )

    @task
    def output_final_config_task(self) -> Task:
        return Task(
            description="Output the final refined configuration.",
            expected_output="The final refined JSON configuration.",
            agent=self.configuration_refiner_agent(),
            context=[self.refine_config_task()],
            output_pydantic=CrewConfig
        )

    @crew
    def crew(self) -> Crew:
        # We do not dynamically tweak agent creation anymore;
        # Just run tasks in a straightforward sequential process.
        return Crew(
            agents=[
                self.requirements_architect_agent(),
                self.configuration_refiner_agent()
            ],
            tasks=[
                self.gather_user_requirements_task(),
                self.draft_initial_config_task(),
                self.refine_config_task(),
                self.output_final_config_task()
            ],
            process=Process.sequential,
            verbose=True
        )
