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

@CrewBase
class MetaCrew:
    def __init__(self, llm_model="gpt-4"):
        self.llm_model = llm_model
        self.inputs: Dict[str, Any] = {}
        
    @before_kickoff
    def capture_inputs(self, inputs: Dict[str, Any]):
        self.inputs = inputs
        return inputs

    @agent
    def requirements_architect_agent(self) -> Agent:
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
        prompt = """
You are the Requirements Architect Agent. 
...
"""
        return Task(
            description="Collect and summarize the user's requirements into a structured JSON.",
            expected_output="JSON object with all user requirements.",
            agent=self.requirements_architect_agent(),
            prompt_template=prompt
        )

    @task
    def draft_initial_config_task(self) -> Task:
        prompt = """
You are the Requirements Architect Agent. ...
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
        prompt = """
You are the Configuration Refiner Agent. ...
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
