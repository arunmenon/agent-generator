# src/my_project/api/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class MetaAgentInput(BaseModel):
    user_description: str
    user_input_description: str
    user_output_description: str
    user_tools: List[str] = []
    user_process: str
    user_planning: bool
    user_knowledge: bool
    user_human_input_tasks: bool
    user_memory: bool
    user_cache: bool
    user_manager_llm: Optional[str] = None

class FlowInput(BaseModel):
    task: str = Field(..., description="The primary task description")
    domain: str = Field(..., description="The domain or industry context (e.g., Healthcare, Finance, E-commerce)")
    process_areas: List[str] = Field(default_factory=list, description="Specific process areas within the domain")
    problem_context: str = Field(..., description="Detailed context about the problem being solved")
    input_context: str = Field(..., description="Description of the inputs available to the system")
    output_context: str = Field(..., description="Description of the expected outputs from the system")
    constraints: List[str] = Field(default_factory=list, description="Limitations or requirements that must be followed")
    model_name: str = Field(default="gpt-4o", description="The LLM to use")
    temperature: float = Field(default=0.7, description="LLM temperature parameter")

class AgentSchema(BaseModel):
    """Schema for a CrewAI agent"""
    name: str = Field(..., description="Unique name of the agent")
    role: str = Field(..., description="Role of the agent")
    goal: str = Field(..., description="Goal/objective of the agent")
    backstory: str = Field(..., description="Detailed backstory with context")
    verbose: bool = Field(default=True, description="Whether agent should be verbose")
    allow_delegation: bool = Field(default=True, description="Whether agent can delegate tasks")
    tools: List[str] = Field(default_factory=list, description="Tools available to the agent")

class TaskSchema(BaseModel):
    """Schema for a CrewAI task"""
    description: str = Field(..., description="Full task description including context placeholders")
    agent: str = Field(..., description="Agent assigned to this task (name reference)")
    expected_output: str = Field(..., description="Expected output format description")
    context: List[str] = Field(default_factory=list, description="Task dependencies (by name)")
    async_execution: bool = Field(default=False, description="Whether task can run asynchronously")
    output_file: Optional[str] = Field(default=None, description="File to output results to")

class CrewSchema(BaseModel):
    """Schema for a CrewAI crew configuration"""
    name: str = Field(..., description="Name of the crew")
    description: str = Field(default="", description="Description of the crew's purpose")
    process: str = Field(default="sequential", description="Process type (sequential or hierarchical)")
    agents: List[AgentSchema] = Field(..., description="List of agents in the crew")
    tasks: List[TaskSchema] = Field(..., description="List of tasks for the crew to execute")
    verbose: bool = Field(default=True, description="Whether crew execution should be verbose")
    config: Dict[str, Any] = Field(default_factory=dict, description="Additional configuration")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context parameters for interpolation")

class CrewConfig(BaseModel):
    """Configuration for a complete crew setup including metadata"""
    crew: Dict[str, Any] = Field(..., description="Crew metadata and configuration")
    agents: List[Dict[str, Any]] = Field(..., description="Agent definitions with interpolation placeholders")
    tasks: List[Dict[str, Any]] = Field(..., description="Task definitions with interpolation placeholders")
    input_schema_json: Dict[str, Any] = Field(..., description="JSON schema for input parameters")
    domain: str = Field(..., description="Domain context for the crew")
    process_areas: List[str] = Field(default_factory=list, description="Process areas addressed")
    problem_context: str = Field(..., description="Description of the problem being solved")
    process_type: str = Field(default="sequential", description="Process type for the crew")
