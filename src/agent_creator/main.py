#!/usr/bin/env python
import sys
import warnings
import json
import requests
import argparse
from typing import Dict, Any

from src.agent_creator.crew import AgentCreator
from src.agent_creator.flow_crew import MultiCrewFlow, create_crew_with_flow

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI LLMs'
    }
    AgentCreator().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        AgentCreator().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        AgentCreator().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        AgentCreator().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test_flow_direct(task: str, model_name: str = "gpt-4o", temperature: float = 0.7) -> Dict[str, Any]:
    """
    Test the flow directly without using the API.
    
    Args:
        task: The task description for the crew
        model_name: The LLM model to use
        temperature: The temperature parameter for the LLM
        
    Returns:
        The flow result
    """
    config = {
        "model_name": model_name,
        "temperature": temperature
    }
    
    print(f"Running flow directly with task: {task}")
    result = create_crew_with_flow(task, config)
    
    # Return as dictionary with basic info
    return {
        "status": "success",
        "agents": [agent.__dict__ for agent in result.agents],
        "tasks": [task.__dict__ for task in result.tasks],
        "process": result.process
    }

def test_flow_api(task: str, model_name: str = "gpt-4o", 
                 temperature: float = 0.7, debug: bool = False) -> Dict[str, Any]:
    """
    Test the flow API by creating a crew from a given task.
    
    Args:
        task: The task description for the crew
        model_name: The LLM model to use
        temperature: The temperature parameter for the LLM
        debug: Whether to use the debug endpoint
        
    Returns:
        The API response
    """
    base_url = "http://localhost:8000"
    
    # Determine which endpoint to use
    if debug:
        endpoint = f"{base_url}/flow/debug"
        data = {
            "task": task,
            "model_name": model_name,
            "temperature": temperature
        }
        response = requests.post(endpoint, json=data)
    else:
        endpoint = f"{base_url}/flow/create"
        params = {
            "task": task,
            "model_name": model_name,
            "temperature": temperature
        }
        response = requests.post(endpoint, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return {}

def run_flow():
    """Test the flow implementation."""
    parser = argparse.ArgumentParser(description="Test the Agent Creator Flow")
    parser.add_argument("--task", type=str, required=True, help="Task description for the crew")
    parser.add_argument("--model", type=str, default="gpt-4o", help="LLM model to use")
    parser.add_argument("--temp", type=float, default=0.7, help="Temperature parameter")
    parser.add_argument("--api", action="store_true", help="Use API rather than direct flow")
    parser.add_argument("--debug", action="store_true", help="Use debug endpoint (only with --api)")
    
    args = parser.parse_args()
    
    if args.api:
        print(f"Testing Flow API with task: {args.task}")
        result = test_flow_api(args.task, args.model, args.temp, args.debug)
    else:
        print(f"Testing Flow directly with task: {args.task}")
        result = test_flow_direct(args.task, args.model, args.temp)
    
    # Pretty print the result
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("No result returned")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "flow":
        # Remove the flow argument for argparse
        sys.argv.pop(1)
        run_flow()
    else:
        run()
