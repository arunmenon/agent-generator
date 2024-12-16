# src/my_project/api/schemas.py
from pydantic import BaseModel
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

