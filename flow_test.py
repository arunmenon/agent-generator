"""Test file for checking flow-based crew implementations."""

import sys
from src.agent_creator.flow.multi_crew_flow import MultiCrewFlow, create_crew_with_flow
from src.agent_creator.crews.models import CrewPlan

def test_flow():
    """Test the flow-based crew creation."""
    print("Testing MultiCrewFlow...")
    
    # Create test config
    config = {
        "domain": "Retail Catalog",
        "process_areas": ["Item-Setup"],
        "problem_context": "Retail merchandising team needs to efficiently plan, schedule, and coordinate seasonal product introductions across multiple departments and sales channels",
        "input_context": "Seasonal calendars, historical performance data, vendor lead times, and departmental capacity constraints",
        "output_context": "Optimized seasonal merchandise plan with introduction timelines, promotional schedules, and resource allocation recommendations",
        "constraints": ["Must account for 30+ merchandise departments", "Must integrate with existing inventory systems", "Should provide at least 6-month planning horizon"]
    }
    
    # Test the flow
    task = "Create a seasonal merchandise planning system for retail catalog management"
    
    # Get flow metadata
    flow = MultiCrewFlow(user_task=task, config=config)
    print(f"Flow start methods: {flow._start_methods}")
    print(f"Flow listeners: {flow._listeners}")
    
    print("\nRunning create_crew_with_flow...")
    result = create_crew_with_flow(task, config)
    
    # Check result
    print(f"\nResult type: {type(result)}")
    if isinstance(result, CrewPlan):
        print(f"Crew name: {result.name}")
        print(f"Agents: {len(result.agents)}")
        print(f"Tasks: {len(result.tasks)}")
        
        # Print agent names
        print("\nAgents:")
        for agent in result.agents:
            print(f"- {agent.name}: {agent.role}")
        
        # Print task names
        print("\nTasks:")
        for task in result.tasks:
            print(f"- {task.name}: {task.assigned_to}")
    else:
        print(f"Result is not a CrewPlan: {result}")
    
    return result

if __name__ == "__main__":
    test_flow()