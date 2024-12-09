import logging
from typing import Any, Dict
from pydantic import BaseModel
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, task, crew, before_kickoff
import litellm

logging.basicConfig(level=logging.DEBUG) 

class CrewConfig(BaseModel):
    crew: Dict[str, Any]
    agents: Any
    tasks: Any
    input_schema_json: Any

@CrewBase
class MetaCrew:
    def __init__(self, llm_model="openai/gpt-4o"):
        self.llm_model = llm_model
        self.llm = LLM(
            model=self.llm_model,
            temperature=0.2,
            verbose=True
        )
        self.inputs: Dict[str, Any] = {}

    @before_kickoff
    def capture_inputs(self, inputs: Dict[str, Any]):
        print("DEBUG: Capturing inputs:", inputs)
        logging.debug(f"Capturing inputs: {inputs}")
        self.inputs = inputs
        return inputs

    @agent
    def planner_agent(self) -> Agent:
        return Agent(
            role="Planning Architect",
            goal="Break down user requirements into conceptual tasks and identify what agents (specialists) are needed.",
            backstory="An expert at analyzing high-level needs and determining the tasks and agent types required.",
            llm=self.llm,
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
    def schema_converter_agent(self) -> Agent:
        return Agent(
            role="Schema Converter",
            goal="Convert the conceptual tasks and agents into a final CrewAI schema-compliant configuration.",
            backstory="Skilled at translating plans into the exact fields required by the CrewAI schema.",
            llm=self.llm,
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
        prompt = f"""
Analyze the user inputs and produce a structured JSON summarizing the user's high-level requirements.

User Description: {self.inputs.get('user_description','No description')}
User Input Description: {self.inputs.get('user_input_description','Not provided')}
User Output Description: {self.inputs.get('user_output_description','Not provided')}
Tools: {self.inputs.get('user_tools','None')}
Process: {self.inputs.get('user_process','None')}
Planning: {self.inputs.get('user_planning',False)}
Knowledge: {self.inputs.get('user_knowledge',False)}
Human Input Tasks: {self.inputs.get('user_human_input_tasks',False)}
Memory: {self.inputs.get('user_memory',False)}
Cache: {self.inputs.get('user_cache',False)}
Manager LLM: {self.inputs.get('user_manager_llm',None)}

Just summarize these requirements as JSON. Do not define tasks or agents here.
"""
        return Task(
            description="Summarize user requirements into structured JSON.",
            expected_output="A JSON object with the user's high-level requirements.",
            agent=self.planner_agent(),
            prompt_template=prompt
        )

    @task
    def plan_tasks_and_agents_task(self) -> Task:
        prompt = f"""
Based on the previously summarized requirements ({{requirements_json}}), determine conceptually what tasks are needed to achieve these requirements and what types of agents (specialists) would be required.

For example, if user wants 'Generate prompts for writing tasks', think about tasks like 'Research theme', 'Draft prompts', 'Review and refine prompts', and agents like 'Research Specialist', 'Creative Writer', etc.

Produce a conceptual JSON with two sections:
- "plannedTasks": a list of conceptual tasks with a brief idea of what they do (no strict schema yet).
- "requiredAgentTypes": a list of conceptual agent types needed (like 'Prompt Writer', 'Editor', 'Researcher').

No CrewAI schema yet, just planning. No mention of persona.
"""
        return Task(
            description="Determine conceptual tasks and required agent types.",
            expected_output="A conceptual JSON with planned tasks and required agent types.",
            agent=self.planner_agent(),
            context=[self.gather_user_requirements_task()],
            prompt_template=prompt
        )

    @task
    def assemble_schema_task(self) -> Task:
        prompt = """
Now transform the conceptual plan ({{plan_json}}) into a final CrewAI schema:

- "crew": derive from user requirements.
- "agents": An array of agents, each with 'role', 'goal', 'backstory'. Use the conceptual agent types identified and assign them a role, goal, and backstory.
- "tasks": An array of tasks. Each must have:
  "name" (snake_case),
  "description" (human-readable),
  "expected_output" (what it produces),
  "agent" (assign one of the defined agents by role).
- "input_schema_json": null if none.

All arrays must be present. If conceptual plan is vague, create at least one agent and one task following CrewAI style.
No persona mentions, just produce the final JSON.
"""
        return Task(
            description="Convert conceptual plan into CrewAI schema.",
            expected_output="CrewAI-compliant JSON configuration.",
            agent=self.schema_converter_agent(),
            context=[self.plan_tasks_and_agents_task()],
            prompt_template=prompt,
            output_pydantic=CrewConfig
        )

    @task
    def refine_and_output_final_config_task(self) -> Task:
        prompt = """
Refine the given config {{draft_config}} to ensure strict CrewAI schema compliance:
- "crew", "agents", "tasks", "input_schema_json" present.
- agents: 'role', 'goal', 'backstory'.
- tasks: 'name', 'description', 'expected_output', 'agent'.
If something is missing, add placeholders.
Return final JSON.
"""
        return Task(
            description="Refine and output the final configuration.",
            expected_output="The final refined JSON configuration.",
            agent=self.schema_converter_agent(),
            context=[self.assemble_schema_task()],
            prompt_template=prompt,
            output_pydantic=CrewConfig
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.planner_agent(), self.schema_converter_agent()],
            tasks=[
                self.gather_user_requirements_task(),
                self.plan_tasks_and_agents_task(),
                self.assemble_schema_task(),
                self.refine_and_output_final_config_task()
            ],
            process=Process.sequential,
            verbose=True
        )
