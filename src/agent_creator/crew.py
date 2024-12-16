# crew.py
from typing import Any, Dict
from pydantic import BaseModel
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, task, crew, before_kickoff

class CrewConfig(BaseModel):
    crew: Dict[str, Any]
    agents: Any
    tasks: Any
    input_schema_json: Any

@CrewBase
class MetaCrew():
    def __init__(self, llm_model="openai/gpt-4"):
        self.llm_model = llm_model
        # Set verbose=False to reduce debug logs
        self.llm = LLM(model=self.llm_model, temperature=0.2, verbose=False)
        self.inputs: Dict[str, Any] = {}

    @before_kickoff
    def capture_inputs(self, inputs: Dict[str, Any]):
        self.inputs = inputs
        return inputs

    @agent
    def planner_agent(self) -> Agent:
        return Agent(
            role="Planning Architect",
            goal="Transform the provided user requirements into a well-structured conceptual plan including minimal, cohesive tasks and clearly defined agent roles.",
            backstory=(
                "A seasoned planning architect experienced in data enrichment and workflow "
                "orchestration. Expert at analyzing high-level needs, determining logically "
                "sequenced tasks, and identifying the necessary specialists. Ensures each task "
                "is actionable, minimal, and described with purpose, complexity, and dependencies."
            ),
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
    def schema_converter(self) -> Agent:
        return Agent(
            role="Schema Converter",
            goal=(
                "Convert the conceptual tasks and agents into a fully compliant, final CrewAI schema. "
                "Validate all fields, correct any missing or malformed parts, and ensure a production-ready JSON output."
            ),
            backstory=(
                "A meticulous schema architect trained to produce CrewAI-compliant configurations. "
                "Understands every required field and ensures all tasks and agents are fully defined. "
                "Fills missing fields logically, removes extraneous info, and returns only perfected JSON."
            ),
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
        description = """
Below are user inputs. Extract them and produce a strictly formatted JSON with the following keys:
- description (string)
- inputDescription (string)
- outputDescription (string)
- tools (array of strings)
- process (string)
- planning (boolean)
- knowledge (boolean)
- humanInputTasks (boolean)
- memory (boolean)
- cache (boolean)
- managerLLM (string or null)

Do not add extra commentary. Return only JSON. Ensure correct JSON syntax.

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
"""
        return Task(
            description=description,
            expected_output="A JSON object with user's requirements.",
            agent=self.planner_agent()
        )

    @task
    def plan_tasks_and_agents_task(self) -> Task:
        # Double braces around JSON braces
        description = """
Given these user requirements:
{{output}}

**INSTRUCTIONS:**
- Analyze requirements and determine conceptual tasks. Each task must have:
  - name
  - purpose (short description)
  - dependencies (array, can be empty)
  - complexity (Low/Medium/High)
- Determine required agent types. Each agent type must have:
  - role (one-liner)
  - goal (one-liner)
  - backstory (brief background, domain-relevant)
- Make tasks minimal and actionable, logically sequenced. Agents must be distinct and domain-appropriate.
- Return strictly JSON:
{{
  "plannedTasks": [
    {{
      "name": "TaskNameExample",
      "purpose": "short purpose",
      "dependencies": [],
      "complexity": "Low"
    }}
  ],
  "requiredAgentTypes": [
    {{
      "role": "AgentRoleExample",
      "goal": "Goal line",
      "backstory": "Brief backstory"
    }}
  ]
}}
No extraneous commentary.
"""
        return Task(
            description=description,
            expected_output="Conceptual plan in JSON.",
            agent=self.planner_agent(),
            context=[self.gather_user_requirements_task()]
        )

    @task
    def assemble_schema_task(self) -> Task:
        # Double braces for JSON
        description = """
Given this conceptual plan:
{{output}}

**INSTRUCTIONS:**
- Convert into a CrewAI schema:
{{
  "crew": {{}},
  "agents": [],
  "tasks": [],
  "input_schema_json": {{}}
}}
- Fill all missing fields logically. No code blocks, only JSON.
- Ensure tasks and agents reflect the conceptual plan accurately.
- Include all necessary fields for crew, agents, and tasks.
- No extra commentary, just final JSON.
"""
        return Task(
            description=description,
            expected_output="CrewAI-compliant JSON configuration.",
            agent=self.schema_converter(),
            context=[self.plan_tasks_and_agents_task()],
            output_pydantic=CrewConfig
        )

    @task
    def refine_and_output_final_config_task(self) -> Task:
        # Double braces for JSON
        description = """
Given this draft config:
{{output}}

**INSTRUCTIONS:**
- Refine and ensure perfect CrewAI compliance. Final JSON only.
- Crew, agents, tasks, input_schema_json must be present.
- Each agent: must have role, goal, backstory.
- Each task: must have name, description, expected_output, agent, human_input, context_tasks.
- Remove placeholders or irrelevant details.
- Return only the final refined JSON.
"""
        return Task(
            description=description,
            expected_output="Refined final JSON configuration.",
            agent=self.schema_converter(),
            context=[self.assemble_schema_task()],
            output_pydantic=CrewConfig
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.planner_agent(), self.schema_converter()],
            tasks=[
                self.gather_user_requirements_task(),
                self.plan_tasks_and_agents_task(),
                self.assemble_schema_task(),
                self.refine_and_output_final_config_task()
            ],
            process=Process.sequential,
            verbose=True
        )
