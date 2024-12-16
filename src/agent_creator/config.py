# config.py
from pydantic import BaseModel
from typing import Any, Dict

class CrewConfig(BaseModel):
    crew: Dict[str, Any]
    agents: Any
    tasks: Any
    input_schema_json: Any
