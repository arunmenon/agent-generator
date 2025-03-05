"""
Task definitions for the Implementation Crew.
"""

from crewai import Task, Agent
from typing import List, Dict

def create_tasks(agents: List[Agent]) -> List[Task]:
    """
    Create and return the tasks for the Implementation Crew.
    
    Args:
        agents: List of agents to assign tasks to
        
    Returns:
        List of Task objects
    """
    # Extract agents by role
    agent_engineer = next(a for a in agents if a.role == "Agent Engineer")
    task_designer = next(a for a in agents if a.role == "Task Designer")
    workflow_specialist = next(a for a in agents if a.role == "Workflow Specialist")
    integration_expert = next(a for a in agents if a.role == "Integration Expert")
    
    # Task 1: Design Agents
    design_agents = Task(
        description="""
        Create detailed agent definitions based on the selected plan.
        
        User Task: {user_task}
        Domain: {domain}
        Problem Context: {problem_context}
        Input Context: {input_context}
        Output Context: {output_context}
        Process Areas: {process_areas}
        Constraints: {constraints}
        Analysis Results: {analysis_result}
        Planning Results: {planning_result}
        
        Your job is to:
        1. Review the agent definitions in the selected plan
        2. Enhance and refine the agent specifications
        3. Ensure each agent has a clear role, goal, and backstory
        4. Make sure agents collectively cover all required capabilities
        5. Include domain expertise related to {domain} in agent backstories
        6. Ensure agents understand how to work with {input_context} inputs and produce {output_context} outputs
        
        Format your response as a JSON object with:
        - agents: Array of agent definitions, each with:
          - name: Descriptive agent name
          - role: Clear role description
          - goal: Specific goal or objective
          - backstory: Detailed backstory that explains capabilities
        """,
        agent=agent_engineer,
        expected_output="JSON with agent definitions"
    )
    
    # Task 2: Design Tasks
    design_tasks = Task(
        description="""
        Create detailed task definitions based on the selected plan.
        
        User Task: {{user_task}}
        Analysis Results: {{analysis_result}}
        Planning Results: {{planning_result}}
        Agent Definitions: {{design_agents.output}}
        
        Your job is to:
        1. Review the task definitions in the selected plan
        2. Enhance and refine the task specifications
        3. Ensure each task has a clear purpose and expected output
        4. Assign each task to the most appropriate agent
        5. Define dependencies between tasks
        
        Format your response as a JSON object with:
        - tasks: Array of task definitions, each with:
          - name: Descriptive task name
          - description: Detailed description of what the task does
          - assigned_to: Name of the agent assigned to this task
          - dependencies: Array of task names that must complete before this task
          - complexity: Complexity level (Low, Medium, High)
        """,
        agent=task_designer,
        expected_output="JSON with task definitions",
        context=[design_agents]
    )
    
    # Task 3: Define Workflow
    define_workflow = Task(
        description="""
        Create an optimized workflow definition for task execution.
        
        User Task: {{user_task}}
        Analysis Results: {{analysis_result}}
        Planning Results: {{planning_result}}
        Agent Definitions: {{design_agents.output}}
        Task Definitions: {{design_tasks.output}}
        
        Your job is to:
        1. Analyze the task dependencies and relationships
        2. Create a sequence for task execution
        3. Identify which tasks can be executed in parallel
        4. Ensure the workflow is efficient and logical
        
        Format your response as a JSON object with:
        - workflow: Object containing:
          - sequence: Array of task names in execution order
          - parallel_tasks: Array of arrays, where each sub-array contains tasks that can run in parallel
        """,
        agent=workflow_specialist,
        expected_output="JSON with workflow definition",
        context=[design_agents, design_tasks]
    )
    
    # Task 4: Specify Tools
    specify_tools = Task(
        description="""
        Specify the tools needed by the agents.
        
        User Task: {{user_task}}
        Analysis Results: {{analysis_result}}
        Planning Results: {{planning_result}}
        Agent Definitions: {{design_agents.output}}
        Task Definitions: {{design_tasks.output}}
        
        Your job is to:
        1. Identify tools and resources needed by the agents
        2. Specify which agents use which tools
        3. Define the purpose of each tool
        
        Format your response as a JSON object with:
        - tools: Array of tool definitions, each with:
          - name: Tool name
          - purpose: What the tool does
          - used_by: Array of agent names that use this tool
        """,
        agent=integration_expert,
        expected_output="JSON with tool definitions",
        context=[design_agents, design_tasks]
    )
    
    # Task 5: Integrate Components
    integrate_components = Task(
        description="""
        Integrate all components into a cohesive implementation.
        
        User Task: {{user_task}}
        Analysis Results: {{analysis_result}}
        Planning Results: {{planning_result}}
        Agent Definitions: {{design_agents.output}}
        Task Definitions: {{design_tasks.output}}
        Workflow Definition: {{define_workflow.output}}
        Tool Definitions: {{specify_tools.output}}
        
        Your job is to:
        1. Validate that all components work together
        2. Ensure no gaps or inconsistencies exist
        3. Recommend the appropriate process type (sequential or hierarchical)
        4. Compile everything into a complete implementation
        
        Format your response matching the ImplementationOutput model with:
        - agents: List of AgentDefinition objects from agent definitions
        - tasks: List of TaskDefinition objects from task definitions
        - workflow: WorkflowDefinition object from workflow definition
        - tools: List of ToolDefinition objects from tool definitions
        - process_type: Recommended process type ("sequential" or "hierarchical") with justification
        """,
        agent=integration_expert,
        expected_output="ImplementationOutput model with complete implementation",
        context=[design_agents, design_tasks, define_workflow, specify_tools]
    )
    
    return [design_agents, design_tasks, define_workflow, specify_tools, integrate_components]