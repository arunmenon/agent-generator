"""
A simplified mock API server for testing the frontend without requiring CrewAI.
"""

import json
import time
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

app = FastAPI()

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model definitions
class AgentDefModel(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str = ""

class TaskDefModel(BaseModel):
    name: str
    purpose: str
    dependencies: List[str] = []
    complexity: str = "Medium"

# Mock crew data
next_crew_id = 1000
crews = {}

# Create some sample crew data
def create_sample_crew():
    global next_crew_id
    crew_id = next_crew_id
    next_crew_id += 1
    
    crews[str(crew_id)] = {
        "crew_id": crew_id,
        "crew_name": "Sample Customer Service Bot",
        "process": "sequential",
        "manager_llm": "gpt-4o",
        "is_active": True,
        "agents": [
            {
                "name": "Customer Service Agent",
                "role": "Handle customer inquiries and provide helpful responses",
                "goal": "Ensure customer satisfaction",
                "backstory": "Experienced in customer support with deep product knowledge",
                "llm": "gpt-4o"
            },
            {
                "name": "Product Specialist",
                "role": "Provide detailed product information",
                "goal": "Give accurate product details and recommendations",
                "backstory": "Expert in the product catalog and features",
                "llm": "gpt-4o"
            }
        ],
        "tasks": [
            {
                "name": "Greet Customer",
                "description": "Welcome the customer and identify their needs",
                "agent_name": "Customer Service Agent",
                "expected_output": "Customer need identified",
                "human_input": False,
                "context_tasks": []
            },
            {
                "name": "Provide Information",
                "description": "Answer customer questions with detailed product information",
                "agent_name": "Product Specialist",
                "expected_output": "Product information provided",
                "human_input": False,
                "context_tasks": ["Greet Customer"]
            }
        ]
    }
    
    return crew_id

# Create initial sample crew
create_sample_crew()

# Endpoints
@app.get("/")
def read_root():
    return {"message": "Mock Agent Creator API"}

@app.get("/crews")
def list_crews():
    """List all crews."""
    return [
        {
            "crew_id": crew_data["crew_id"],
            "crew_name": crew_data["crew_name"],
            "process": crew_data["process"],
            "num_agents": len(crew_data["agents"])
        }
        for crew_id, crew_data in crews.items()
    ]

@app.get("/crews/{crew_id}")
def get_crew(crew_id: str):
    """Get a specific crew by ID."""
    if crew_id not in crews:
        raise HTTPException(status_code=404, detail="Crew not found")
    return crews[crew_id]

@app.post("/flow/create")
def create_crew_with_flow_api(
    task: str,
    model_name: Optional[str] = Query("gpt-4o", description="The LLM to use"),
    temperature: Optional[float] = Query(0.7, description="LLM temperature parameter")
):
    """Create a new crew configuration using the Flow-based approach."""
    # Simulate processing time
    time.sleep(1)
    
    # Create a new crew
    global next_crew_id
    crew_id = next_crew_id
    next_crew_id += 1
    
    # Build a more varied response based on the task
    task_lower = task.lower()
    
    # Different crew configurations based on task type
    if "chatbot" in task_lower or "customer service" in task_lower:
        crew_name = f"Customer Service Bot: {task[:20]}..."
        agents = [
            {
                "name": "Customer Service Agent",
                "role": "Handle customer inquiries",
                "goal": "Ensure customer satisfaction",
                "backstory": "Experienced in customer support",
                "llm": model_name
            },
            {
                "name": "Product Specialist",
                "role": "Provide product details",
                "goal": "Give accurate information",
                "backstory": "Expert in product catalog",
                "llm": model_name
            }
        ]
        tasks = [
            {
                "name": "Greet_Customer",
                "description": "Welcome customer and identify needs",
                "agent_name": "Customer Service Agent",
                "expected_output": "Customer need identified",
                "human_input": False,
                "context_tasks": []
            },
            {
                "name": "Answer_Questions",
                "description": "Provide detailed information",
                "agent_name": "Product Specialist", 
                "expected_output": "Information provided",
                "human_input": False,
                "context_tasks": ["Greet_Customer"]
            }
        ]
        process = "sequential"
    elif "research" in task_lower or "analysis" in task_lower:
        crew_name = f"Research Team: {task[:20]}..."
        agents = [
            {
                "name": "Research Lead",
                "role": "Coordinate research activities",
                "goal": "Generate comprehensive insights",
                "backstory": "Experienced academic researcher",
                "llm": model_name
            },
            {
                "name": "Data Analyst",
                "role": "Analyze data and extract patterns",
                "goal": "Discover meaningful insights",
                "backstory": "Statistical expert with domain knowledge",
                "llm": model_name
            },
            {
                "name": "Content Writer",
                "role": "Synthesize findings into reports",
                "goal": "Create clear, concise reports",
                "backstory": "Technical writer with research background",
                "llm": model_name
            }
        ]
        tasks = [
            {
                "name": "Define_Research_Scope",
                "description": "Clarify research questions and methodology",
                "agent_name": "Research Lead",
                "expected_output": "Research plan",
                "human_input": False,
                "context_tasks": []
            },
            {
                "name": "Analyze_Data",
                "description": "Examine relevant data sources",
                "agent_name": "Data Analyst",
                "expected_output": "Data insights",
                "human_input": False,
                "context_tasks": ["Define_Research_Scope"]
            },
            {
                "name": "Create_Report",
                "description": "Write comprehensive findings report",
                "agent_name": "Content Writer",
                "expected_output": "Final report",
                "human_input": False,
                "context_tasks": ["Analyze_Data"]
            }
        ]
        process = "hierarchical"
    else:
        # Default crew for other task types
        crew_name = f"Flow-Generated Crew: {task[:20]}..."
        agents = [
            {
                "name": "Task Coordinator",
                "role": "Coordinate overall workflow",
                "goal": "Ensure successful completion of all tasks",
                "backstory": "Experienced project manager",
                "llm": model_name
            },
            {
                "name": "Domain Expert",
                "role": "Provide specialized knowledge",
                "goal": "Deliver accurate domain-specific information",
                "backstory": "Subject matter expert with years of experience",
                "llm": model_name
            }
        ]
        tasks = [
            {
                "name": "Plan_Execution",
                "description": "Create execution plan with milestones",
                "agent_name": "Task Coordinator",
                "expected_output": "Detailed plan document",
                "human_input": False,
                "context_tasks": []
            },
            {
                "name": "Implement_Solution",
                "description": "Apply domain knowledge to solve problem",
                "agent_name": "Domain Expert",
                "expected_output": "Solution artifacts",
                "human_input": False,
                "context_tasks": ["Plan_Execution"]
            }
        ]
        process = "sequential"
    
    # Store in our mock database
    crews[str(crew_id)] = {
        "crew_id": crew_id,
        "crew_name": crew_name,
        "process": process,
        "manager_llm": model_name,
        "is_active": True,
        "agents": agents,
        "tasks": tasks
    }
    
    return {
        "status": "success", 
        "crew_id": crew_id,
        "message": f"Crew created successfully using Multi-Crew Flow approach with {process} process"
    }

@app.post("/flow/debug")
def debug_crew_flow(
    task: str = Body(..., embed=True),
    model_name: str = Body("gpt-4o", embed=True),
    temperature: float = Body(0.7, embed=True)
):
    """Debug endpoint that returns the full analysis process without saving to the database."""
    # Simulate processing time
    time.sleep(2)
    
    # Return debug information with mock analysis data
    return {
        "status": "success",
        "task": task,
        "analysis": {
            "constraints": ["Must respond within 5 seconds", "Must be accurate"],
            "requirements": ["Product knowledge", "Returns policy understanding"],
            "complexity": 6,
            "domain_knowledge": ["E-commerce", "Customer service"],
            "time_sensitivity": {"is_critical": True, "reasoning": "Customer satisfaction depends on quick responses"},
            "success_criteria": ["Accurate information provided", "Customer issue resolved"],
            "recommended_process_type": "sequential"
        },
        "planning": {
            "selected_algorithm": "Best-of-N Planning",
            "algorithm_justification": "Well-suited for customer service workflows with clear steps",
            "candidate_plans": [
                {"name": "Sequential Approach", "score": 8},
                {"name": "Hierarchical Structure", "score": 6}
            ],
            "selected_plan": {
                "name": "Sequential Customer Service",
                "description": "A straightforward sequential approach"
            },
            "verification_score": 8
        },
        "implementation": {
            "agents": [
                {
                    "name": "Customer Service Agent",
                    "role": "Handle customer inquiries and provide helpful responses",
                    "goal": "Ensure customer satisfaction",
                    "backstory": "Experienced in customer support with deep product knowledge"
                },
                {
                    "name": "Product Specialist",
                    "role": "Provide detailed product information",
                    "goal": "Give accurate product details and recommendations",
                    "backstory": "Expert in the product catalog and features"
                },
                {
                    "name": "Returns Handler",
                    "role": "Process return requests efficiently",
                    "goal": "Make the returns process smooth and transparent",
                    "backstory": "Knowledgeable about company return policies and procedures"
                }
            ],
            "tasks": [
                {
                    "name": "Greet and identify customer needs",
                    "description": "Establish rapport and understand customer requirements",
                    "dependencies": [],
                    "complexity": "Low"
                },
                {
                    "name": "Provide product information",
                    "description": "Answer detailed questions about products",
                    "dependencies": ["Greet and identify customer needs"],
                    "complexity": "Medium"
                },
                {
                    "name": "Process return requests",
                    "description": "Handle returns efficiently according to policy",
                    "dependencies": ["Greet and identify customer needs"],
                    "complexity": "Medium"
                }
            ],
            "workflow": {"sequence": ["Greet", "Answer", "Process"]},
            "process_type": "sequential",
            "tools": []
        },
        "evaluation": {
            "strengths": ["Clear task division", "Specialized agents"],
            "weaknesses": ["Limited handling of complex queries"],
            "missing_elements": ["Escalation process for difficult cases"],
            "recommendations": ["Add escalation mechanism"],
            "overall_score": 8,
            "improvement_area": "none"
        },
        "iterations": {
            "analysis": 1,
            "planning": 1,
            "implementation": 1,
            "evaluation": 1
        },
        "final_crew_plan": {
            "agents": [
                {
                    "name": "Customer Service Agent",
                    "role": "Handle customer inquiries and provide helpful responses",
                    "goal": "Ensure customer satisfaction",
                    "backstory": "Experienced in customer support with deep product knowledge"
                },
                {
                    "name": "Product Specialist",
                    "role": "Provide detailed product information",
                    "goal": "Give accurate product details and recommendations",
                    "backstory": "Expert in the product catalog and features"
                },
                {
                    "name": "Returns Handler",
                    "role": "Process return requests efficiently",
                    "goal": "Make the returns process smooth and transparent",
                    "backstory": "Knowledgeable about company return policies and procedures"
                }
            ],
            "tasks": [
                {
                    "name": "Greet and identify customer needs",
                    "purpose": "Establish rapport and understand customer requirements",
                    "dependencies": [],
                    "complexity": "Low"
                },
                {
                    "name": "Provide product information",
                    "purpose": "Answer detailed questions about products",
                    "dependencies": ["Greet and identify customer needs"],
                    "complexity": "Medium"
                },
                {
                    "name": "Process return requests",
                    "purpose": "Handle returns efficiently according to policy",
                    "dependencies": ["Greet and identify customer needs"],
                    "complexity": "Medium"
                }
            ],
            "process": "sequential"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)