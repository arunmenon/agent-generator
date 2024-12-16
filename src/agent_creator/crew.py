# crew.py
from typing import Any, Dict
from crewai import Crew, Process
from crewai.project import CrewBase, before_kickoff, crew
from .llm import create_llm
from .agents import get_planner_agent, get_schema_converter_agent
from .tasks import (
    gather_user_requirements_task,
    plan_tasks_and_agents_task,
    assemble_schema_task,
    refine_and_output_final_config_task
)
from .config import CrewConfig

@CrewBase
class MetaCrew:
    """
    MetaCrew orchestrates:
    1. Requirements gathering
    2. Planning tasks and agents
    3. Assembling schema
    4. Refining schema
    """
    def __init__(self, llm_model="openai/gpt-4"):
        self.llm_model = llm_model
        self.llm = create_llm(model=self.llm_model, temperature=0.2, verbose=False)
        self.inputs: Dict[str, Any] = {}

        # Initialize agents
        self.planner_agent = get_planner_agent(self.llm)
        self.schema_converter_agent = get_schema_converter_agent(self.llm)

        # Initialize tasks
        self.gather_task = gather_user_requirements_task(self.planner_agent)
        self.planning_task = plan_tasks_and_agents_task(self.planner_agent, self.gather_task)
        self.assemble_task = assemble_schema_task(self.schema_converter_agent, self.planning_task, CrewConfig)
        self.refine_task = refine_and_output_final_config_task(self.schema_converter_agent, self.assemble_task, CrewConfig)

    @before_kickoff
    def capture_inputs(self, inputs: Dict[str, Any]):
        self.inputs = inputs
        return inputs

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.planner_agent, self.schema_converter_agent],
            tasks=[self.gather_task, self.planning_task, self.assemble_task, self.refine_task],
            process=Process.sequential,
            verbose=True
        )
