"""
Utility functions for multi-crew flows.
"""

def create_input_schema(domain, problem_context, input_context):
    """Create a basic input schema for a crew plan."""
    class InputSchema:
        def __init__(self):
            self.type = "object"
            self.properties = {
                "domain": {
                    "type": "string",
                    "description": f"The domain context ({domain})",
                    "example": domain
                },
                "problem_context": {
                    "type": "string",
                    "description": "Detailed description of the problem being solved",
                    "example": problem_context
                },
                "input_data": {
                    "type": "object",
                    "description": f"The input data: {input_context}",
                    "example": {"sample": "data"}
                }
            }
            self.required = ["domain", "problem_context", "input_data"]
        
        def model_dump(self):
            return {
                "type": self.type,
                "properties": self.properties,
                "required": self.required
            }
    
    return InputSchema()

def create_output_schema(output_context):
    """Create a basic output schema for a crew plan."""
    class OutputSchema:
        def __init__(self):
            self.type = "object"
            self.properties = {
                "result": {
                    "type": "object",
                    "description": f"The output result: {output_context}",
                    "example": {"status": "success", "data": {}}
                }
            }
        
        def model_dump(self):
            return {
                "type": self.type,
                "properties": self.properties
            }
    
    return OutputSchema()