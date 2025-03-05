"""
Simplified test script for flow crew API testing - includes mock classes so we don't need
the full crewai dependencies.
"""

import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# Mock classes to replace flow_crew imports
class AgentDefinition:
    """Definition of an agent with name, role, goal and backstory."""
    
    def __init__(self, name: str, role: str, goal: str, backstory: str = ""):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        
    def __dict__(self):
        return {
            "name": self.name,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory
        }

class TaskDefinition:
    """Definition of a task with name, purpose and optional dependencies."""
    
    def __init__(self, name: str, purpose: str, dependencies: List[str] = None, complexity: str = "Medium"):
        self.name = name
        self.purpose = purpose
        self.dependencies = dependencies or []
        self.complexity = complexity
        
    def __dict__(self):
        return {
            "name": self.name,
            "purpose": self.purpose,
            "dependencies": self.dependencies,
            "complexity": self.complexity
        }

class CrewPlan:
    """A plan for a crew with agents, tasks and process type."""
    
    def __init__(self, agents: List[AgentDefinition], tasks: List[TaskDefinition], process: str = "sequential"):
        self.agents = agents
        self.tasks = tasks
        self.process = process

# Mock the CrewAI Flow functionality (since we can't install crewai)
class MockFlowClass:
    def kickoff(self):
        # Return a mock CrewPlan
        agents = [
            AgentDefinition(
                name="Customer Service Agent",
                role="Handle customer inquiries and provide helpful responses",
                goal="Ensure customer satisfaction",
                backstory="Experienced in customer support with deep product knowledge"
            ),
            AgentDefinition(
                name="Product Specialist",
                role="Provide detailed product information",
                goal="Give accurate product details and recommendations",
                backstory="Expert in the product catalog and features"
            ),
            AgentDefinition(
                name="Returns Handler",
                role="Process return requests efficiently",
                goal="Make the returns process smooth and transparent",
                backstory="Knowledgeable about company return policies and procedures"
            )
        ]
        
        tasks = [
            TaskDefinition(
                name="Greet and identify customer needs",
                purpose="Establish rapport and understand customer requirements",
                dependencies=[],
                complexity="Low"
            ),
            TaskDefinition(
                name="Provide product information",
                purpose="Answer detailed questions about products",
                dependencies=["Greet and identify customer needs"],
                complexity="Medium"
            ),
            TaskDefinition(
                name="Process return requests",
                purpose="Handle returns efficiently according to policy",
                dependencies=["Greet and identify customer needs"],
                complexity="Medium"
            )
        ]
        
        return CrewPlan(agents=agents, tasks=tasks, process="sequential")

# Mock the Flow class
def create_crew_with_flow_mock(user_task: str, config: Dict[str, Any] = None) -> CrewPlan:
    """
    Mock implementation of create_crew_with_flow that returns a fixed CrewPlan.
    """
    print(f"Creating crew for task: {user_task}")
    print(f"Config: {config}")
    
    return MockFlowClass().kickoff()

def test_flow():
    """Test the flow implementation with a mock."""
    task = "Create a customer service chatbot that handles product inquiries and returns"
    config = {
        "model_name": "gpt-4o",
        "temperature": 0.7
    }
    
    # Just use the mock implementation for now
    print("Using mock implementation...")
    crew_plan = create_crew_with_flow_mock(task, config)
    
    # Print the result
    print("\nCreated Crew Plan:")
    print(f"Process: {crew_plan.process}")
    print(f"Agents: {len(crew_plan.agents)}")
    for i, agent in enumerate(crew_plan.agents):
        print(f"\nAgent {i+1}: {agent.name}")
        print(f"Role: {agent.role}")
        print(f"Goal: {agent.goal}")
    
    print(f"\nTasks: {len(crew_plan.tasks)}")
    for i, task in enumerate(crew_plan.tasks):
        print(f"\nTask {i+1}: {task.name}")
        print(f"Purpose: {task.purpose}")
        print(f"Dependencies: {task.dependencies}")
    
    # This is what would be stored in the API response
    api_response = {
        "status": "success",
        "crew_id": 12345,  # This would normally be generated by the database
        "agents": [agent.__dict__() for agent in crew_plan.agents],
        "tasks": [task.__dict__() for task in crew_plan.tasks],
        "process": crew_plan.process
    }
    
    print("\nAPI Response (JSON):")
    print(json.dumps(api_response, indent=2))
    
    # Return the crew plan for further testing
    return crew_plan

if __name__ == "__main__":
    test_flow()