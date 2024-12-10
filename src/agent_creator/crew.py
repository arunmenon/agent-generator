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
            goal="Analyze user requirements and produce a conceptual plan",
            backstory="Expert at analyzing high-level needs and determining tasks and agent types.",
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
            goal="Convert conceptual tasks and agents into a CrewAI schema",
            backstory="Skilled in translating plans into final CrewAI schema-compliant configurations.",
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
        # Only this task needs to use the user inputs, so we will still use format.
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

Summarize these into a structured JSON object. No extra text, just JSON.
"""
        # This task uses placeholders from inputs, so it will be interpolated at runtime by CrewAI.
        return Task(
            description=description,
            expected_output="A JSON object with user's high-level requirements.",
            agent=self.planner_agent()
        )

    @task
    def plan_tasks_and_agents_task(self) -> Task:
        # This task does not rely on user input placeholders anymore.
        # Replace {{output}} with double braces to avoid format issues.
        description = """
Given these user requirements:
{{output}}

(Example in a retail e-commerce context, like Walmart's product catalog)
If user requirements involve "Enhancing product data quality for the Walmart e-commerce catalog", conceptual tasks might be:
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
- Taxonomy Specialist (for mapping attributes to the internal taxonomy)
- QA Engineer (for checking data consistency and completeness)
- Data Analyst (for conducting and evaluating A/B tests)

Now, based on the provided user requirements above:

Determine:
- Conceptual tasks needed
- Required agent types

Return JSON with "plannedTasks" and "requiredAgentTypes".
"""
        # No .format() call needed because we do not rely on inputs here.
        return Task(
            description=description,
            expected_output="Conceptual plan in JSON.",
            agent=self.planner_agent(),
            context=[self.gather_user_requirements_task()]
        )

    @task
    def assemble_schema_task(self) -> Task:
        # Again, double braces around "crew", "agents", etc. to avoid format treating them as placeholders.
        description = """
From this conceptual plan:
{{output}}

Produce CrewAI schema:
{{
  "crew": {{}},
  "agents": [],
  "tasks": [],
  "input_schema_json": {{}}
}}

No code blocks, just return JSON. Fill missing fields if needed.
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
        description = """
Given this draft config:
{{output}}

Refine to ensure perfect schema compliance:
- Ensure crew, agents, tasks, input_schema_json present.
- Agents have role, goal, backstory.
- Tasks have name, description, expected_output, agent.
Return final JSON only.
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
