# src/agent_creator/crew.py

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
        """
        Store user inputs in self.inputs so placeholders like {user_description}
        get replaced by CrewAI’s .format(**inputs) at runtime.
        """
        self.inputs = inputs
        return inputs

    @agent
    def planner_agent(self) -> Agent:
        """
        Agent that proposes conceptual tasks & agent types from user requirements.
        """
        return Agent(
            role="Planning Architect",
            goal=(
                "Transform user requirements into a minimal, cohesive set of tasks "
                "and well-defined agent roles."
            ),
            backstory=(
                "A seasoned planning architect with expertise in orchestrating workflows, "
                "ensuring each task is minimal, actionable, and properly sequenced."
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
        """
        Agent that merges tasks with input_schema_json and refines the final CrewAI schema.
        Preserves any quadruple-braced placeholders (e.g. {{{{title}}}}).
        """
        return Agent(
            role="Schema Converter",
            goal=(
                "Merge planned tasks/agents with a partial input_schema_json snippet into a final CrewAI config. "
                "Validate each agent/task, fill missing fields, and return the final JSON."
            ),
            backstory=(
                "A schema architect well-versed in CrewAI standards. Ensures tasks/agents are fully defined, "
                "removes extraneous info, and preserves placeholders if relevant."
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
        """
        Gathers raw user inputs with placeholders. CrewAI .format(**inputs) will fill them
        before the LLM sees it.
        """
        description = """
Below are user inputs. Extract them into strictly formatted JSON with keys:
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

No commentary, just JSON. The user provided:

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
            expected_output="A JSON object with top-level user requirements.",
            agent=self.planner_agent()
        )

    @task
    def plan_tasks_and_agents_task(self) -> Task:
        """
        Proposes tasks & agent types using quadruple braces {{{{title}}}} if needed.
        Keep double braces for CrewAI placeholders (e.g. {{output}}).
        """
        # Raw string so Python doesn't treat backslashes/newlines specially.
        # Double braces to avoid KeyError from .format().
        description = r"""
Given these user requirements:
{{output}}

We also have 'inputDescription': {{{{user_input_description}}}}, which might imply placeholders
like {{{{title}}}}, {{{{targetLanguage}}}}, etc.

**INSTRUCTIONS**:
1. Analyze the user’s requirements → produce a conceptual plan:
   - For each task: name, purpose, dependencies, complexity.
   - If relevant to user_input_description, embed placeholders like {{{{title}}}} or {{{{targetLanguage}}}} in the tasks.
2. Determine agent types: role, goal, backstory.
   - If relevant, embed placeholders in those fields (e.g. "Translator for {{{{title}}}}").
3. Return strictly JSON. For instance:

[[  <-- We'll double-brace the JSON snippet
  {{
    "plannedTasks": [
      {{
        "name": "TaskNameExample",
        "purpose": "Translate {{{{title}}}} into {{{{targetLanguage}}}}",
        "dependencies": [],
        "complexity": "Low"
      }}
    ],
    "requiredAgentTypes": [
      {{
        "role": "Translator for {{{{title}}}}",
        "goal": "Accurately translate {{{{title}}}}",
        "backstory": "..."
      }}
    ]
  }}
]]

No commentary.
"""
        return Task(
            description=description,
            expected_output="Conceptual plan in JSON (may have placeholders).",
            agent=self.planner_agent(),
            context=[self.gather_user_requirements_task()]
        )

    @task
    def interpret_input_description_task(self) -> Task:
        """
        Takes 'inputDescription' from user requirements → partial input_schema_json snippet.
        E.g. if inputDescription says "Title to localize," produce:
        {
          "input_schema_json": {
            "title": {"type": "string", "description": "..."}
          }
        }
        """
        # Here we double any braces in the snippet.
        description = r"""
From user requirements (especially 'inputDescription'):
{{output}}

**INSTRUCTIONS**:
1. Construct partial `input_schema_json` from inputDescription. Example:

{{
  "input_schema_json": {{
    "title": {{ "type": "string", "description": "..." }},
    "targetLanguage": {{ "type": "string", "description": "..." }}
  }}
}}

No commentary, only JSON.
"""
        return Task(
            description=description,
            expected_output="Partial JSON snippet for input_schema_json based on inputDescription.",
            agent=self.schema_converter(),
            context=[self.gather_user_requirements_task()]
        )

    @task
    def assemble_schema_task(self) -> Task:
        """
        Merges the conceptual plan + partial input_schema_json into a standard CrewAI schema.
        """
        # Double braces so .format won't interpret them. 
        description = r"""
We have a conceptual plan:
{{output}}

And also a partial input_schema_json from interpret_input_description_task.

**INSTRUCTIONS**:
- Merge plan + input_schema_json
- Produce a standard CrewAI schema like:
{{
  "crew": {{ }},
  "agents": [],
  "tasks": [],
  "input_schema_json": {{}}
}}
- Keep placeholders like {{{{title}}}} if they exist.
- Return final JSON only, no commentary.
"""
        return Task(
            description=description,
            expected_output="CrewAI-compliant JSON (placeholders intact).",
            agent=self.schema_converter(),
            context=[
                self.plan_tasks_and_agents_task(),
                self.interpret_input_description_task()
            ],
            output_pydantic=CrewConfig
        )

    @task
    def refine_and_output_final_config_task(self) -> Task:
        """
        Final step: ensures placeholders remain if relevant; cleans up extraneous text.
        """
        # Double braces around the snippet if you show example JSON.
        description = r"""
Given this draft config:
{{output}}

**INSTRUCTIONS**:
1. Ensure "crew", "agents", "tasks", "input_schema_json" are present.
2. Each agent: name, role, goal, backstory. Keep placeholders {{{{title}}}} if relevant.
3. Each task: name, description, expected_output, agent, human_input, context_tasks.
   - Keep placeholders if they make sense. Remove truly extraneous placeholders only.
4. Return final JSON, no commentary or code blocks.
"""
        return Task(
            description=description,
            expected_output="Refined final JSON schema (preserving placeholders if relevant).",
            agent=self.schema_converter(),
            context=[self.assemble_schema_task()],
            output_pydantic=CrewConfig
        )

    @crew
    def crew(self) -> Crew:
        """
        Final pipeline: gather -> plan -> interpret -> assemble -> refine.
        Quadruple braces for placeholders, double braces for literal JSON. 
        """
        return Crew(
            agents=[self.planner_agent(), self.schema_converter()],
            tasks=[
                self.gather_user_requirements_task(),
                self.plan_tasks_and_agents_task(),
                self.interpret_input_description_task(),
                self.assemble_schema_task(),
                self.refine_and_output_final_config_task()
            ],
            process=Process.sequential,
            verbose=True
        )
